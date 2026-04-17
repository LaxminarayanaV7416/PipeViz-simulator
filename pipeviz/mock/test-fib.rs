// test-fib.rs
// Author: Laxminarayana Vadnala <lvadnala@nd.edu>
// This is just a mock file for testing the object dump generation
// for the rust programming language.

/// Compute the n-th Fibonacci number iteratively.
fn fibonacci(n: u32) -> u64 {
    if n == 0 {
        return 0;
    } else if n == 1 {
        return 1;
    }
    fibonacci(n - 1) + fibonacci(n - 2)
}

// main function where program execution starts
fn main() {
    let count: u32 = 10;

    println!("Fibonacci sequence (first {} terms):", count);

    for i in 0..count {
        let value = fibonacci(i);
        println!("F({}) = {}", i, value);
    }
}
