/*
 * test-fib.c
 * Author: Laxminarayana Vadnala <lvadnala@nd.edu>
 * This is just a mock file for testing the object dump generation
 * for the C programming language.
 */

#include <stdio.h>
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

    printf("Fibonacci sequence (first %u terms):\n", count);

    for (unsigned int i = 0; i < count; i++) {
        unsigned long value = fibonacci(i);
        printf("F(%u) = %lu\n", i, value);
    }

    return 0;
}
