#include <cstdio>
#include <chrono>

static double calculate(long long iterations, long long param1, long long param2) {
    double result = 1.0;
    for (long long i = 1; i <= iterations; ++i) {
        double j1 = (double)(i * param1 - param2);
        double j2 = (double)(i * param1 + param2);
        double a = 1.0 / j1;
        double b = 1.0 / j2;
        result -= a;
        result += b;
    }
    return result;
}

int main() {
    auto start = std::chrono::steady_clock::now();
    double result = calculate(200000000LL, 4, 1) * 4;
    auto end = std::chrono::steady_clock::now();
    double elapsed = std::chrono::duration<double>(end - start).count();
    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", elapsed);
    return 0;
}
