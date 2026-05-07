#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>

#define N 64      // Matrix size
#define B 8       // Blocking factor (cache line size consideration)

// Non-blocked matrix multiplication (for comparison)
void matrix_multiply_naive(double x[N][N], double y[N][N], double z[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            for (int k = 0; k < N; k++) {
                x[i][j] = x[i][j] + y[i][k] * z[k][j];
            }
        }
    }
}

// Blocked matrix multiplication (cache-optimized)
void matrix_multiply_blocked(double x[N][N], double y[N][N], double z[N][N]) {
    for (int jj = 0; jj < N; jj += B) {
        for (int kk = 0; kk < N; kk += B) {
            for (int i = 0; i < N; i++) {
                for (int j = jj; j < (jj + B < N ? jj + B : N); j++) {
                    double r = 0;
                    for (int k = kk; k < (kk + B < N ? kk + B : N); k++) {
                        r = r + y[i][k] * z[k][j];
                    }
                    x[i][j] = x[i][j] + r;
                }
            }
        }
    }
}

// Initialize matrices
void init_matrices(double x[N][N], double y[N][N], double z[N][N]) {
    for (int i = 0; i < N; i++) {
        for (int j = 0; j < N; j++) {
            x[i][j] = 0.0;
            y[i][j] = (double)(i * N + j);
            z[i][j] = (double)((i + j) % N);
        }
    }
}

int main() {
    double (*x)[N] = malloc(sizeof(double) * N * N);
    double (*y)[N] = malloc(sizeof(double) * N * N);
    double (*z)[N] = malloc(sizeof(double) * N * N);
    
    if (!x || !y || !z) {
        fprintf(stderr, "Memory allocation failed\n");
        return 1;
    }

    init_matrices(x, y, z);
    
    // Run blocked version
    matrix_multiply_blocked(x, y, z);
    
    // Print result sample
    printf("Result[0][0] = %f\n", x[0][0]);
    printf("Result[5][5] = %f\n", x[5][5]);
    
    free(x);
    free(y);
    free(z);
    
    return 0;
}