# use the rust image as the base image
FROM rust:trixie

# set working directory path
WORKDIR /app

# copy the main code/ for now lets call them main.rs
COPY main.rs .

# compile the rust code with debug info
RUN rustc -C debuginfo=2 -o main main.rs

# disassemble the compiled binary
RUN objdump -d main > main.asm
