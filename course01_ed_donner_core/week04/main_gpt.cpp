#include <chrono>
#include <cstdio>
#include <cstdint>

int main() {
    const auto start = std::chrono::system_clock::now();

    double result = 1.0;
    for (std::uint32_t j = 3; j < 800000003u; j += 4) {
        result -= 1.0 / static_cast<double>(j);
        result += 1.0 / static_cast<double>(j + 2);
    }
    result *= 4.0;

    const auto end = std::chrono::system_clock::now();
    const double elapsed = std::chrono::duration<double>(end - start).count();

    std::printf("Result: %.12f\n", result);
    std::printf("Execution Time: %.6f seconds\n", elapsed);
    return 0;
}
