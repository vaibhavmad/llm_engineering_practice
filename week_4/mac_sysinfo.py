import subprocess
import platform
import json
import shutil

def _run_cmd(cmd_list):
    """Safely executes commands via argument lists (shell=False) to prevent injection."""
    try:
        result = subprocess.run(cmd_list, capture_output=True, text=True, check=True)
        # Returns just the first line, safely replacing `| head -n 1`
        return result.stdout.splitlines()[0].strip() if result.stdout else ""
    except (subprocess.CalledProcessError, FileNotFoundError, IndexError):
        return ""

def _probe_compute_features():
    """Filters sysctl hardware flags for arithmetic, vector, and matrix compute features."""
    COMPUTE_ALLOWLIST = {
        "neon", "AdvSIMD", "floatingpoint",
        "FEAT_FP16", "FEAT_BF16", 
        "FEAT_DotProd", "FEAT_I8MM", "FEAT_FHM",
        "AdvSIMD_HPFPCvt"
    }

    try:
        result = subprocess.run(["sysctl", "-a"], capture_output=True, text=True, check=True)
        features = []
        for line in result.stdout.splitlines():
            key, sep, val = line.partition(":")
            
            # Check for successful partition and boolean '1'
            if sep and key.startswith("hw.optional.") and val.strip() == "1":
                # Clean up the key name for easier matching
                clean_key = key.removeprefix("hw.optional.").removeprefix("arm.")
                
                # If it's a core compute feature, add it to our payload
                if clean_key in COMPUTE_ALLOWLIST or any(tag in clean_key for tag in COMPUTE_ALLOWLIST):
                    features.append(clean_key)
        
        return sorted(list(set(features)))
    except (subprocess.CalledProcessError, FileNotFoundError):
        return []

def _check_tool(tool_name):
    """Checks if a binary is installed in the system PATH."""
    return shutil.which(tool_name) or ""

def get_unified_m2_context(as_json=True):
    """Generates a high-signal, measured system and toolchain context payload."""
    if platform.system() != "Darwin":
        raise OSError("This script is designed strictly for macOS.")

    is_rosetta = _run_cmd(["sysctl", "-n", "sysctl.proc_translated"]) == "1"
    target_triple = _run_cmd(["clang", "-dumpmachine"]) or f"{platform.machine()}-apple-darwin{platform.release()}"

    payload = {
        "os_environment": {
            "system": "Darwin",
            "release": platform.release(),
            "architecture": platform.machine(),
            "rosetta2_translated": is_rosetta,
            "target_triple": target_triple
        },
        
        "hardware_constraints": {
            "cpu_brand": _run_cmd(["sysctl", "-n", "machdep.cpu.brand_string"]),
            "cores": {
                "physical": int(_run_cmd(["sysctl", "-n", "hw.physicalcpu"]) or 0),
                "logical": int(_run_cmd(["sysctl", "-n", "hw.logicalcpu"]) or 0)
            },
            "compute_extensions": _probe_compute_features(),
            
            "memory": {
                "total_ram_bytes": int(_run_cmd(["sysctl", "-n", "hw.memsize"]) or 0),
                "page_size_bytes": int(_run_cmd(["sysctl", "-n", "hw.pagesize"]) or 0)
            },
            
            "cache": {
                "cache_line_size_bytes": int(_run_cmd(["sysctl", "-n", "hw.cachelinesize"]) or 0),
                "l1_data_cache_bytes": int(_run_cmd(["sysctl", "-n", "hw.l1dcachesize"]) or 0),
                "l2_cache_bytes": int(_run_cmd(["sysctl", "-n", "hw.l2cachesize"]) or 0)
            }
        },
        
        "toolchain": {
            "compilers": {
                "clang": _run_cmd(["clang", "--version"]) if _check_tool("clang") else "",
                "gcc": _run_cmd(["gcc", "--version"]) if _check_tool("gcc") else "",
            },
            "build_tools": {
                "make": _run_cmd(["make", "--version"]) if _check_tool("make") else "",
                "cmake": _run_cmd(["cmake", "--version"]) if _check_tool("cmake") else "",
                "ninja": _run_cmd(["ninja", "--version"]) if _check_tool("ninja") else ""
            }
        }
    }

    return json.dumps(payload, indent=2) if as_json else payload