# py-load-balancer

A simple HTTP load balancer using `aiohttp` to distribute traffic across backends. It uses the **Least Connections** strategy to keep things balanced.

### What it does:
- Tracks active connections to each backend.
- Picks the "quietest" server for the next request.
- Handles everything asynchronously (no blocking).
- Ready to go with Docker Compose.

### Setup & Run
Make sure you have Docker running, then:

```bash
docker-compose up --build