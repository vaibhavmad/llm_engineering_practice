#include <cstdio>
#include <chrono>
#include <arm_neon.h>

static double calculate(long iterations, double param1, double param2) {
    double result = 1.0;
    const float64x2_t ones = vdupq_n_f64(1.0);
    const float64x2_t off = (float64x2_t){-param2, param2};
    double d = 0.0;
    for (long i = 1; i <= iterations; ++i) {
        d += param1;  // exact: d = i * param1
        float64x2_t den = vaddq_f64(vdupq_n_f64(d), off);
        float64x2_t r = vdivq_f64(ones, den);
        result -= vgetq_lane_f64(r, 0);
        result += vgetq_lane_f64(r, 1);
    }
    return result;
}

int main() {
    auto start = std::chrono::high_resolution_clock::now();
    double result = calculate(200000000L, 4.0, 1.0) * 4.0;
    auto end = std::chrono::high_resolution_clock::now();
    double secs = std::chrono::duration<double>(end - start).count();
    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", secs);
    return 0;
}
