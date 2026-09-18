#include <iostream>
#include <iomanip>
#include <chrono>
#include <cmath>
#include <thread>
#include <vector>
#include <atomic>
#include <cstring>
#include <mutex>

// Highly optimized version using:
// 1. Algebraic simplification: (1/(4i+1) - 1/(4i-1)) = -2/(16i²-1)
// 2. SIMD-friendly loop structure
// 3. Multi-threading with cache-friendly block partitioning
// 4. Reduced precision operations where safe

double calculate_range(size_t start, size_t end) {
    double local_sum = 0.0;
    
    // Process in chunks for better SIMD vectorization
    constexpr size_t BLOCK_SIZE = 4096;
    
    for (size_t i = start; i < end; i += BLOCK_SIZE) {
        size_t block_end = std::min(i + BLOCK_SIZE, end);
        double block_sum = 0.0;
        
        // inner loop for SIMD optimization
        #pragma clang loop vectorize(enable) interleave(enable)
        for (size_t j = i; j < block_end; ++j) {
            // Simplified: (1/(4j+1) - 1/(4j-1)) = -2/(16j²-1)
            double denominator = 16.0 * static_cast<double>(j) * static_cast<double>(j) - 1.0;
            block_sum += 1.0 / denominator;
        }
        
        local_sum += block_sum;
    }
    
    return local_sum;
}

int main() {
    constexpr size_t ITERATIONS = 200000000;
    constexpr int NUM_THREADS = 8; // Apple M2 has 8 cores
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Thread pool
    std::vector<std::thread> threads;
    std::vector<double> partial_sums(NUM_THREADS, 0.0);
    
    // Distribute work evenly across threads
    size_t chunk_size = ITERATIONS / NUM_THREADS;
    
    for (int t = 0; t < NUM_THREADS; ++t) {
        size_t start = t * chunk_size + 1;
        size_t end = (t == NUM_THREADS - 1) ? (ITERATIONS + 1) : ((t + 1) * chunk_size + 1);
        
        threads.emplace_back([&partial_sums, t, start, end]() {
            partial_sums[t] = calculate_range(start, end);
        });
    }
    
    // Join threads
    for (auto& thread : threads) {
        thread.join();
    }
    
    // Combine results
    double total = 0.0;
    for (int t = 0; t < NUM_THREADS; ++t) {
        total += partial_sums[t];
    }
    
    // Final result: result = (1 - 2 * total) * 4
    // Original: result = 1 + sum(-1/(4i-1) + 1/(4i+1)) for i=1..n
    // = 1 + sum(-2/(16i²-1))
    // = 1 - 2 * sum(1/(16i²-1))
    double result = (1.0 - 2.0 * total) * 4.0;
    
    auto end_time = std::chrono::high_resolution_clock::now();
    auto duration = std::chrono::duration_cast<std::chrono::microseconds>(end_time - start_time);
    
    std::cout << std::fixed << std::setprecision(12) << "Result: " << result << std::endl;
    std::cout << std::fixed << std::setprecision(6) << "Execution Time: " << duration.count() / 1000000.0 << " seconds" << std::endl;
    
    return 0;
}
