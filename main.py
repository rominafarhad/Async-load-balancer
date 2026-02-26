import asyncio
from aiohttp import web
from balance import LoadBalancer

BACKENDS = ["http://backend1:8081", "http://backend2:8082"]

async def start_background_tasks(app):
    app['health_check'] = asyncio.create_task(app['lb'].check_health())

async def cleanup_background_tasks(app):
    app['health_check'].cancel()
    await app['health_check']

def create_app():
    lb = LoadBalancer(BACKENDS)
    app = web.Application()
    app['lb'] = lb
    
    app.on_startup.append(start_background_tasks)
    app.on_cleanup.append(cleanup_background_tasks)
    
    app.router.add_route('*', '/{path:.*}', lb.handle_request)
    return app

if __name__ == "__main__":
    app = create_app()
    web.run_app(app, port=8080)