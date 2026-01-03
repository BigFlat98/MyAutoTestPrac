# Builder stage
FROM rust:latest as builder

WORKDIR /usr/src/chat

# Copy manifests first for caching dependencies
COPY Cargo.toml Cargo.lock ./

# Create dummy main.rs to build dependencies
RUN mkdir src && echo "fn main() {}" > src/main.rs
RUN cargo build --release

# Remove dummy build artifacts
RUN rm -f target/release/deps/chat*

# Copy actual source code
COPY . .

# Build the actual application
RUN cargo build --release

# Runtime stage
FROM debian:bookworm-slim

# Install OpenSSL (required for sqlx/postgres)
RUN apt-get update && apt-get install -y libssl-dev ca-certificates && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy binary from builder
COPY --from=builder /usr/src/chat/target/release/chat /app/chat

# Copy .env file (optional, but good for defaults if needed)
# COPY .env .env 

EXPOSE 3000

CMD ["./chat"]
