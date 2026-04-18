# use the rust image as the base image
FROM rust:trixie

# Declare a build argument with a default value
ARG PROGRAM_FILE_NAME=test-fib.rs

# Make it visible at runtime too (optional)
ENV PROGRAM_FILE_NAME=${PROGRAM_FILE_NAME}

# set working directory path
WORKDIR /app

# copy the main code/ for now lets call them main.rs
COPY "${PROGRAM_FILE_NAME}" main.rs

# compile the rust code with debug info
RUN rustc -C debuginfo=2 -o main main.rs

# disassemble the compiled binary
RUN objdump -d -S -r -t main > main.asm
