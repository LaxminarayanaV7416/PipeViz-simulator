# use the rust image as the base image
FROM gcc:14.3-trixie

# Declare a build argument with a default value
ARG PROGRAM_FILE_NAME=test-fib.c
ARG COMPILER_OPTIMIZATION=-O0
ARG ENABLE_LOOP_UNROLLING=0

# Make it visible at runtime too (optional)
ENV PROGRAM_FILE_NAME=${PROGRAM_FILE_NAME}

# set working directory path
WORKDIR /app

# copy the main code/ for now lets call them main.rs
COPY "${PROGRAM_FILE_NAME}" main.c

# compile the rust code with debug info
RUN if [ "${ENABLE_LOOP_UNROLLING}" = "1" ]; then \
        gcc -g ${COMPILER_OPTIMIZATION} -floop-unroll-all -o main main.c; \
    else \
        gcc -g ${COMPILER_OPTIMIZATION} -o main main.c; \
    fi

# disassemble the compiled binary
RUN objdump -d -S -r -t main > main.asm
