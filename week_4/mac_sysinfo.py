import subprocess
import platform
import json
import shutil

def _run_cmd(cmd):
    """Helper to run shell commands safely and return stripped output."""
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, check=True)
        return result.stdout.strip()
    except subprocess.CalledProcessError:
        return ""

def _check_tool(tool_name):
    """Checks if a command-line tool is installed and returns its path."""
    return shutil.which(tool_name) or ""

def get_unified_m2_context(as_json=True):
    """
    Generates a unified system and toolchain context payload for LLM prompts.
    """
    if platform.system() != "Darwin":
        raise OSError("This script is designed strictly for macOS.")

    # 1. OS & Execution Environment
    # We check if you are running natively or through Rosetta (Intel emulation).
    is_rosetta = _run_cmd("sysctl -n sysctl.proc_translated") == "1"
    
    # Target triple is the exact format Clang uses to compile code (e.g., arm64-apple-darwin23.0.0)
    target_triple = _run_cmd("clang -dumpmachine") or f"{platform.machine()}-apple-darwin{platform.release()}"

    payload = {
        "os_environment": {
            "system": "Darwin",
            "release": platform.release(),
            "architecture": platform.machine(),
            "rosetta2_translated": is_rosetta,  # TELLS LLM: If true, code might run slower; if false, we have native ARM64 speed.
            "target_triple": target_triple      # TELLS LLM: Use this exact string if generating Makefile/Clang build commands.
        },
        
        "hardware_constraints": {
            "cpu_brand": _run_cmd("sysctl -n machdep.cpu.brand_string"),
            "cores": {
                "physical": int(_run_cmd("sysctl -n hw.physicalcpu") or 0),
                "logical": int(_run_cmd("sysctl -n hw.logicalcpu") or 0)
            },
            # TELLS LLM: Apple M2 supports NEON. Never use x86 SSE/AVX vectorization.
            "simd_support": ["neon", "fp16", "apple-accelerate"], 
            
            "memory": {
                # TELLS LLM: Defines the maximum memory ceiling for the C++ program.
                "total_ram_bytes": int(_run_cmd("sysctl -n hw.memsize") or 0),
                # TELLS LLM: macOS on Apple Silicon pages memory in 16KB blocks, not 4KB. Useful for mmap() operations.
                "page_size_bytes": int(_run_cmd("sysctl -n hw.pagesize") or 0)
            },
            
            "cache": {
                # TELLS LLM: CRITICAL for multithreading. Align structs to 128 bytes to prevent "false sharing" cache invalidation.
                "cache_line_size_bytes": int(_run_cmd("sysctl -n hw.cachelinesize") or 0),
                # TELLS LLM: Used for "cache blocking" - sizing mathematical arrays so they fit perfectly in L1/L2 memory.
                "l1_data_cache_bytes": int(_run_cmd("sysctl -n hw.l1dcachesize") or 0),
                "l2_cache_bytes": int(_run_cmd("sysctl -n hw.l2cachesize") or 0)
            }
        },
        
        "toolchain": {
            # TELLS LLM: Knowing exact versions allows the LLM to use modern C++20/C++23 features if the compiler supports them.
            "compilers": {
                "clang": _run_cmd("clang --version | head -n 1"),
                "gcc": _run_cmd("gcc --version | head -n 1") if _check_tool("gcc") else "",
            },
            # TELLS LLM: If CMake is missing but Make is present, the LLM will generate a Makefile instead of CMakeLists.txt.
            "build_tools": {
                "make": _run_cmd("make --version | head -n 1") if _check_tool("make") else "",
                "cmake": _run_cmd("cmake --version | head -n 1") if _check_tool("cmake") else "",
                "ninja": _run_cmd("ninja --version | head -n 1") if _check_tool("ninja") else ""
            }
        }
    }

    return json.dumps(payload, indent=2) if as_json else payload