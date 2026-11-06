#include <iostream>
#include <iomanip>
#include <chrono>

double calculate(int iterations, int param1, int param2) {
    double result = 1.0;
    for (int i = 1; i <= iterations; ++i) {
        int j1 = i * param1 - param2;
        result -= 1.0 / j1;
        int j2 = i * param1 + param2;
        result += 1.0 / j2;
    }
    return result;
}

int main() {
    using namespace std::chrono;
    auto start_time = high_resolution_clock::now();

    double result = calculate(200000000, 4, 1) * 4;

    auto end_time = high_resolution_clock::now();
    double exec_time = duration<double>(end_time - start_time).count();

    std::cout << "Result: " << std::fixed << std::setprecision(12) << result << std::endl;
    std::cout << "Execution Time: " << std::fixed << std::setprecision(6) << exec_time << " seconds" << std::endl;

    return 0;
}
