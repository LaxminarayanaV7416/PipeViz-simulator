// nested_unroll_demo.c
#include <stdio.h>

int main(void) {
    int n = 1000;
    int sum = 0;
    for (int i = 0; i < n; i++) {
        for (int j = 0; j < n; j++) {
            sum += i + j;
        }
    }
    printf("sum = %d\n", sum);
    return 0;
}
