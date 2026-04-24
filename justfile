run-backend:
    @echo "Running the Pipeviz Simulator..."
    cd pipeviz && source .venv/bin/activate && python main.py --port 5001

run-frontend:
    @echo "Running the Pipeviz Simulator frontend..."
    cd pipeviz-ui && bun run dev
