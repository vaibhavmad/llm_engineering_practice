#include <atomic>
#include <chrono>
#include <cstdio>
#include <memory>
#include <thread>
#include <algorithm>
#include <cstddef>

#if defined(__aarch64__)
#include <arm_neon.h>
#endif

namespace {
constexpr std::size_t Iterations = 200'000'000;
constexpr std::size_t BlockSize = 16'384;
constexpr std::size_t Workers = 7;
constexpr std::size_t BlockCount = (Iterations + BlockSize - 1) / BlockSize;

struct alignas(128) Slot {
    alignas(128) std::atomic<unsigned> ready{0};
    alignas(128) double minus[BlockSize];
    alignas(128) double plus[BlockSize];
};

inline void wait_for(const std::atomic<unsigned>& flag, unsigned value) {
    unsigned spins = 0;
    while (flag.load(std::memory_order_acquire) != value) {
#if defined(__aarch64__)
        __asm__ volatile("yield");
#endif
        if (++spins == 256) {
            spins = 0;
            std::this_thread::yield();
        }
    }
}

void produce(Slot* slots, std::size_t worker) {
    for (std::size_t block = worker; block < BlockCount; block += Workers) {
        Slot& slot = slots[2 * worker + ((block / Workers) & 1)];
        wait_for(slot.ready, 0);

        const std::size_t offset = block * BlockSize;
        const std::size_t count = std::min(BlockSize, Iterations - offset);
        std::size_t k = 0;

#if defined(__aarch64__)
        const float64x2_t one = vdupq_n_f64(1.0);
        const float64x2_t step = vdupq_n_f64(8.0);
        const double first = static_cast<double>(4 * (offset + 1));
        float64x2_t denominator = {first, first + 4.0};

        for (; k + 1 < count; k += 2) {
            vst1q_f64(slot.minus + k,
                      vdivq_f64(one, vsubq_f64(denominator, one)));
            vst1q_f64(slot.plus + k,
                      vdivq_f64(one, vaddq_f64(denominator, one)));
            denominator = vaddq_f64(denominator, step);
        }
#endif
        for (; k < count; ++k) {
            const double denominator = static_cast<double>(4 * (offset + k + 1));
            slot.minus[k] = 1.0 / (denominator - 1.0);
            slot.plus[k] = 1.0 / (denominator + 1.0);
        }

        slot.ready.store(1, std::memory_order_release);
    }
}

// Preserve Python's exact order of floating-point additions and subtractions.
__attribute__((noinline))
double consume(double result, const Slot& slot, std::size_t count) {
#pragma clang fp reassociate(off)
#pragma clang fp contract(off)
#pragma clang loop vectorize(disable)
#pragma clang loop interleave(disable)
    for (std::size_t k = 0; k < count; ++k) {
        result -= slot.minus[k];
        result += slot.plus[k];
    }
    return result;
}

double calculate() {
    std::unique_ptr<Slot[]> slots(new Slot[2 * Workers]);
    std::thread threads[Workers];

    for (std::size_t worker = 0; worker < Workers; ++worker) {
        threads[worker] = std::thread(produce, slots.get(), worker);
    }

    double result = 1.0;
    for (std::size_t block = 0; block < BlockCount; ++block) {
        Slot& slot = slots[2 * (block % Workers) + ((block / Workers) & 1)];
        wait_for(slot.ready, 1);
        result = consume(result, slot,
                         std::min(BlockSize, Iterations - block * BlockSize));
        slot.ready.store(0, std::memory_order_release);
    }

    for (auto& thread : threads) {
        thread.join();
    }
    return result * 4.0;
}
}

int main() {
    const auto start = std::chrono::steady_clock::now();
    const double result = calculate();
    const auto end = std::chrono::steady_clock::now();
    const double seconds = std::chrono::duration<double>(end - start).count();

    std::printf("Result: %.12f\nExecution Time: %.6f seconds\n", result, seconds);
    return 0;
}
