#include <iostream>
#include <chrono>
#include <iomanip>

double calculate(long long iterations, double param1, double param2) {
    double result = 1.0;
    for (long long i = 1; i <= iterations; ++i) {
        // This structure is highly amenable to compiler auto-vectorization
        // via SIMD instructions (like NEON on ARM) at -O3 optimization level.
        const double term = i * param1;
        const double j_neg = term - param2;
        const double j_pos = term + param2;
        result -= 1.0 / j_neg;
        result += 1.0 / j_pos;
    }
    return result;
}

int main() {
    auto start_time = std::chrono::high_resolution_clock::now();
    
    const long long iterations = 200000000;
    const double param1 = 4.0;
    const double param2 = 1.0;
    
    // Set output to fixed-point notation, matching Python's f-string formatting
    std::cout << std::fixed;
    std::cout << std::setprecision(12);
    
    double result = calculate(iterations, param1, param2) * 4.0;
    
    auto end_time = std::chrono::high_resolution_clock::now();
    
    // Match the time precision
    std::cout.precision(6);
    
    std::cout << "Result: " << result << std::endl;
    std::cout << "Execution Time: " << (std::chrono::duration<double>(end_time - start_time).count()) << " seconds" << std::endl;
    
    return 0;
}
