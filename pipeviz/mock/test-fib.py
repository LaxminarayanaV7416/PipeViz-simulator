# test-fib.py
# Author: Laxminarayana Vadnala <lvadnala@nd.edu>
# This is just a mock file for testing the object dump generation
# for the python programming language.

# Compute the n-th Fibonacci number iteratively.
def fibonacci(n: int) -> int:
    if n == 0:
        return 0
    elif n == 1:
        return 1
    return fibonacci(n - 1) + fibonacci(n - 2)


# main function where program execution starts
def main():
    count: int = 10

    print("Fibonacci sequence (first {} terms):".format(count))

    for i in range(count):
        value = fibonacci(i)
        print("F({}) = {}".format(i, value))
