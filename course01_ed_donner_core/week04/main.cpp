#include <cstdio>
#include <cstdint>
#include <vector>
#include <thread>
#include <atomic>
#include <chrono>
#include <arm_neon.h>

static constexpr int64_t ITER = 200000000LL;
static constexpr int64_t CHUNK = 16384;
static constexpr int SLOTS = 32;

struct alignas(128) Slot {
    std::atomic<int64_t> ready{-1};
    std::atomic<int64_t> freed{-1};
    double* buf;
};

static Slot slots[SLOTS];
static std::atomic<int64_t> next_chunk{0};
static int64_t nchunks;

static inline void fill_chunk(double* __restrict buf, int64_t start, int64_t n) {
#pragma clang fp reassociate(off) contract(off) reciprocal(off)
    const float64x2_t one = vdupq_n_f64(1.0);
    const float64x2_t off = {-1.0, 1.0};
    int64_t k = 0;
    for (; k + 4 <= n; k += 4) {
        double b0 = 4.0 * (double)(start + k);
        float64x2_t j0 = vaddq_f64(vdupq_n_f64(b0), off);
        float64x2_t j1 = vaddq_f64(vdupq_n_f64(b0 + 4.0), off);
        float64x2_t j2 = vaddq_f64(vdupq_n_f64(b0 + 8.0), off);
        float64x2_t j3 = vaddq_f64(vdupq_n_f64(b0 + 12.0), off);
        vst1q_f64(buf + 2 * k, vdivq_f64(one, j0));
        vst1q_f64(buf + 2 * k + 2, vdivq_f64(one, j1));
        vst1q_f64(buf + 2 * k + 4, vdivq_f64(one, j2));
        vst1q_f64(buf + 2 * k + 6, vdivq_f64(one, j3));
    }
    for (; k < n; ++k) {
        double b = 4.0 * (double)(start + k);
        float64x2_t j = vaddq_f64(vdupq_n_f64(b), off);
        vst1q_f64(buf + 2 * k, vdivq_f64(one, j));
    }
}

static void worker() {
    for (;;) {
        int64_t c = next_chunk.fetch_add(1, std::memory_order_relaxed);
        if (c >= nchunks) break;
        Slot& s = slots[c % SLOTS];
        while (s.freed.load(std::memory_order_acquire) < c - SLOTS) {
            std::this_thread::yield();
        }
        int64_t start = c * CHUNK + 1;
        int64_t n = ITER - (start - 1);
        if (n > CHUNK) n = CHUNK;
        fill_chunk(s.buf, start, n);
        s.ready.store(c, std::memory_order_release);
    }
}

static double sum_chunk(const double* __restrict buf, int64_t n, double result) {
#pragma clang fp reassociate(off) contract(off) reciprocal(off)
    for (int64_t k = 0; k < n; ++k) {
        result -= buf[2 * k];
        result += buf[2 * k + 1];
    }
    return result;
}

int main() {
    auto t0 = std::chrono::steady_clock::now();

    nchunks = (ITER + CHUNK - 1) / CHUNK;
    std::vector<double> storage((size_t)SLOTS * CHUNK * 2 + 16);
    for (int i = 0; i < SLOTS; ++i) slots[i].buf = storage.data() + (size_t)i * CHUNK * 2;

    unsigned hw = std::thread::hardware_concurrency();
    int nworkers = hw > 1 ? (int)hw - 1 : 1;
    std::vector<std::thread> threads;
    threads.reserve(nworkers);
    for (int i = 0; i < nworkers; ++i) threads.emplace_back(worker);

    double result = 1.0;
    for (int64_t c = 0; c < nchunks; ++c) {
        Slot& s = slots[c % SLOTS];
        while (s.ready.load(std::memory_order_acquire) != c) {
            /* spin */
        }
        int64_t start = c * CHUNK + 1;
        int64_t n = ITER - (start - 1);
        if (n > CHUNK) n = CHUNK;
        result = sum_chunk(s.buf, n, result);
        s.freed.store(c, std::memory_order_release);
    }
    for (auto& t : threads) t.join();

    result *= 4.0;
    auto t1 = std::chrono::steady_clock::now();
    double secs = std::chrono::duration<double>(t1 - t0).count();

    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", secs);
    return 0;
}
