import aiohttp
import asyncio
import logging
from aiohttp import web

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LoadBalancer:
    def __init__(self, backends):
        self.backends = {url: {"active_conns": 0, "healthy": True} for url in backends}

    async def check_health(self):
        """Background task to check if backends are alive."""
        async with aiohttp.ClientSession() as session:
            while True:
                for url in list(self.backends.keys()):
                    try:
                        async with session.get(url, timeout=2) as resp:
                            is_healthy = resp.status < 500
                    except:
                        is_healthy = False
                    
                    if self.backends[url]["healthy"] != is_healthy:
                        status = "RECOVERED" if is_healthy else "DOWN"
                        logging.warning(f"Backend {url} is {status}")
                    
                    self.backends[url]["healthy"] = is_healthy
                await asyncio.sleep(5)

    async def handle_request(self, request):
        # Filter only healthy backends
        healthy_backends = {u: v for u, v in self.backends.items() if v["healthy"]}
        
        if not healthy_backends:
            return web.Response(text="No healthy backends available", status=503)

        # Least Connections logic among healthy nodes
        target_url = min(healthy_backends, key=lambda u: healthy_backends[u]["active_conns"])
        
        self.backends[target_url]["active_conns"] += 1
        logging.info(f"Routing to {target_url} (Active: {self.backends[target_url]['active_conns']})")

        async with aiohttp.ClientSession() as session:
            try:
                async with session.request(
                    request.method,
                    f"{target_url}{request.path_qs}",
                    headers={k: v for k, v in request.headers.items() if k.lower() != 'host'},
                    data=await request.read()
                ) as response:
                    content = await response.read()
                    return web.Response(body=content, status=response.status, headers=dict(response.headers))
            except Exception as e:
                logging.error(f"Failed to reach {target_url}: {e}")
                return web.Response(text="Upstream Error", status=502)
            finally:
                self.backends[target_url]["active_conns"] -= 1