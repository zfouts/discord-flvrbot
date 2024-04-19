# Stage 1: Build and install the library
FROM python:3.10-slim AS builder
WORKDIR /build

# Copy setup.py and the flvrbot package
COPY setup.py .
COPY flvrbot/ flvrbot/

# Install the library
RUN pip install --upgrade pip && \
    pip install .  # Install the package including dependencies

# Stage 2: Prepare the runtime environment
FROM python:3.10-slim AS runtime
WORKDIR /app

# Copy the installed packages from the builder stage
COPY --from=builder /usr/local/lib/python3.10/site-packages /usr/local/lib/python3.10/site-packages

# Copy your Python script to the container
COPY example/main.py /app/main.py

# Set workdir to /app so custom cogs work
WORKDIR /app
# Set the command to run your script
CMD ["python", "/app/main.py"]

