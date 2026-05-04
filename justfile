run:
    @echo "Running the Pipeviz Simulator..."
    cd pipeviz && mkdir -p runs
    @echo "Starting the docker compose up..."
    docker compose up --build
