#include <iostream>
#include <iomanip>
#include <chrono>
#include <thread>
#include <vector>
#include <atomic>
#include <cmath>
#include <mutex>

// Optimized parallel implementation using multiple threads
// Each thread computes a portion of the series independently

double calculate_chunk(long long start, long long end, int param1, int param2) {
    double local_result = 0.0;
    
    // Use loop unrolling for better performance
    long long i = start;
    
    // Process 4 iterations per loop for better instruction-level parallelism
    for (; i + 3 <= end; i += 4) {
        // j1 = i * 4 - 1, contribute -1/j1
        local_result -= 1.0 / (i * param1 - param2);
        local_result += 1.0 / (i * param1 + param2);
        
        // j2 = (i+1) * 4 - 1
        local_result -= 1.0 / ((i + 1) * param1 - param2);
        local_result += 1.0 / ((i + 1) * param1 + param2);
        
        // j3 = (i+2) * 4 - 1
        local_result -= 1.0 / ((i + 2) * param1 - param2);
        local_result += 1.0 / ((i + 2) * param1 + param2);
        
        // j4 = (i+3) * 4 - 1
        local_result -= 1.0 / ((i + 3) * param1 - param2);
        local_result += 1.0 / ((i + 3) * param1 + param2);
    }
    
    // Handle remaining iterations
    for (; i <= end; ++i) {
        local_result -= 1.0 / (i * param1 - param2);
        local_result += 1.0 / (i * param1 + param2);
    }
    
    return local_result;
}

int main() {
    const long long ITERATIONS = 200000000;
    const int PARAM1 = 4;
    const int PARAM2 = 1;
    
    // Determine number of threads to use (use all available cores)
    unsigned int num_threads = std::thread::hardware_concurrency();
    if (num_threads == 0) num_threads = 8; // Fallback to 8 if detection fails
    
    auto start_time = std::chrono::high_resolution_clock::now();
    
    // Allocate thread pool and result storage
    std::vector<std::thread> threads;
    std::vector<double> partial_results(num_threads);
    
    // Calculate work distribution
    long long chunk_size = ITERATIONS / num_threads;
    long long remainder = ITERATIONS % num_threads;
    
    // Launch threads
    long long current_start = 1;
    for (unsigned int i = 0; i < num_threads; ++i) {
        long long current_end = current_start + chunk_size - 1;
        if (i < remainder) {
            current_end++;
        }
        
        threads.emplace_back([&partial_results, i, current_start, current_end]() {
            partial_results[i] = calculate_chunk(current_start, current_end, PARAM1, PARAM2);
        });
        
        current_start = current_end + 1;
    }
    
    // Wait for all threads to complete
    for (auto& thread : threads) {
        thread.join();
    }
    
    // Sum up partial results
    double result = 1.0;
    for (unsigned int i = 0; i < num_threads; ++i) {
        result += partial_results[i];
    }
    
    // Multiply by 4 as in original code
    result *= 4.0;
    
    auto end_time = std::chrono::high_resolution_clock::now();
    std::chrono::duration<double> elapsed = end_time - start_time;
    
    // Output results with same formatting as Python code
    std::cout << std::fixed << std::setprecision(12);
    std::cout << "Result: " << result << std::endl;
    std::cout << "Execution Time: " << std::fixed << std::setprecision(6) 
              << elapsed.count() << " seconds" << std::endl;
    
    return 0;
}
