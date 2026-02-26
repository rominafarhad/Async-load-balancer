import os
import sys

# Add the current directory to sys.path so 'app' folder is recognized
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from aiohttp import web
from app.balancer import LoadBalancer

# Define your backend servers here
BACKENDS = [
    "http://localhost:8081",
    "http://localhost:8082"
]

async def start_app():
    lb = LoadBalancer(BACKENDS)
    app = web.Application()
    
    # This route catches everything and sends it to the LoadBalancer class
    app.router.add_any('/{path:.*}', lb.handle_request)
    return app

if __name__ == "__main__":
    app = start_app()
    print("Smart Load Balancer started on http://localhost:8080")
    web.run_app(app, port=8080)