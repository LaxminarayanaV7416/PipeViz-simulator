# use the rust image as the base image
FROM gcc:14.3-trixie

# Declare a build argument with a default value
ARG PROGRAM_FILE_NAME=test-fib.cpp
ARG COMPILER_OPTIMIZATION=-O0
ARG ENABLE_LOOP_UNROLLING=0

# Make it visible at runtime too (optional)
ENV PROGRAM_FILE_NAME=${PROGRAM_FILE_NAME}

# set working directory path
WORKDIR /app

# copy the main code/ for now lets call them main.rs
COPY "${PROGRAM_FILE_NAME}" main.cpp

# compile the rust code with debug info
RUN if [ "${ENABLE_LOOP_UNROLLING}" = "1" ]; then \
        g++ -g ${COMPILER_OPTIMIZATION} -funroll-loops -o main main.cpp; \
    else \
        g++ -g ${COMPILER_OPTIMIZATION} -o main main.cpp; \
    fi

# disassemble the compiled binary
RUN objdump -d -S -r -t main > main.asm
