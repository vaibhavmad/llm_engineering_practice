#include <cstdio>
#include <chrono>
#include <arm_neon.h>

__attribute__((noinline)) static double calculate(long iterations, double param1, double param2) {
#pragma clang fp reassociate(off) contract(off) reciprocal(off)
    double result = 1.0;
    const float64x2_t one = vdupq_n_f64(1.0);
    long i = 1;
    for (; i + 7 <= iterations; i += 8) {
        double b = (double)i * param1;
        // j values: i*p1 - p2, i*p1 + p2 for 8 consecutive i (exact in double)
        float64x2_t j0 = {b - param2,               b + param2};
        float64x2_t j1 = {b + param1 - param2,      b + param1 + param2};
        float64x2_t j2 = {b + 2*param1 - param2,    b + 2*param1 + param2};
        float64x2_t j3 = {b + 3*param1 - param2,    b + 3*param1 + param2};
        float64x2_t j4 = {b + 4*param1 - param2,    b + 4*param1 + param2};
        float64x2_t j5 = {b + 5*param1 - param2,    b + 5*param1 + param2};
        float64x2_t j6 = {b + 6*param1 - param2,    b + 6*param1 + param2};
        float64x2_t j7 = {b + 7*param1 - param2,    b + 7*param1 + param2};
        float64x2_t r0 = one / j0;
        float64x2_t r1 = one / j1;
        float64x2_t r2 = one / j2;
        float64x2_t r3 = one / j3;
        float64x2_t r4 = one / j4;
        float64x2_t r5 = one / j5;
        float64x2_t r6 = one / j6;
        float64x2_t r7 = one / j7;
        result -= vgetq_lane_f64(r0, 0); result += vgetq_lane_f64(r0, 1);
        result -= vgetq_lane_f64(r1, 0); result += vgetq_lane_f64(r1, 1);
        result -= vgetq_lane_f64(r2, 0); result += vgetq_lane_f64(r2, 1);
        result -= vgetq_lane_f64(r3, 0); result += vgetq_lane_f64(r3, 1);
        result -= vgetq_lane_f64(r4, 0); result += vgetq_lane_f64(r4, 1);
        result -= vgetq_lane_f64(r5, 0); result += vgetq_lane_f64(r5, 1);
        result -= vgetq_lane_f64(r6, 0); result += vgetq_lane_f64(r6, 1);
        result -= vgetq_lane_f64(r7, 0); result += vgetq_lane_f64(r7, 1);
    }
    for (; i <= iterations; ++i) {
        double b = (double)i * param1;
        double ja = b - param2;
        double jb = b + param2;
        result -= 1.0 / ja;
        result += 1.0 / jb;
    }
    return result;
}

int main() {
    auto start = std::chrono::steady_clock::now();
    double result = calculate(200000000L, 4.0, 1.0) * 4.0;
    auto end = std::chrono::steady_clock::now();
    double secs = std::chrono::duration<double>(end - start).count();
    printf("Result: %.12f\n", result);
    printf("Execution Time: %.6f seconds\n", secs);
    return 0;
}
