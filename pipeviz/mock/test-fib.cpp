/*
 * test-fib.cpp
 * Author: Laxminarayana Vadnala <lvadnala@nd.edu>
 * This is just a mock file for testing the object dump generation
 * for the C++ programming language.
 */

#include <iostream>

/* Compute the n-th Fibonacci number recursively. */
unsigned long fibonacci(unsigned int n) {
    if (n == 0) {
        return 0;
    } else if (n == 1) {
        return 1;
    }
    return fibonacci(n - 1) + fibonacci(n - 2);
}

/* main function where program execution starts */
int main() {
    unsigned int count = 10;

    std::cout << "Fibonacci sequence (first " << count << " terms):\n";

    for (unsigned int i = 0; i < count; i++) {
        unsigned long value = fibonacci(i);
        std::cout << "F(" << i << ") = " << value << "\n";
    }

    return 0;
}
