from fastapi import FastAPI

from auth_service.auth_apis import router as auth_router
from compute_service.compute_apis import router as compute_router
from storage_service.storage_apis import router as storage_router
from network_service.network_apis import router as network_router
from juju_service.juju_apis import router as juju_router
from domain_apis.domain_apis import router as domain_router


app = FastAPI()

app.include_router(auth_router)
app.include_router(compute_router)
app.include_router(storage_router)
app.include_router(network_router)
app.include_router(juju_router)
app.include_router(domain_router)


@app.get("/")
def health_check():
    """
    Health Check API
    """
    return "Healthy!"
