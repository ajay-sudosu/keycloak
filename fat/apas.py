from fastapi import Depends, FastAPI, Request


fastapi = FastAPI()


def myyuncleisfine(
    request: Request,
):
    panta = request.query_params.get("fav", None)
    print(panta)
    print(panta)


# app = FastAPI()

# app.router.routes


@fastapi.get("/lethimknowuncle/{jasss}")
def get_app(request: Request, jasss: str):
    # Get the current path
    current_path = request.url.path

    # Get the registered path with placeholders from the endpoint
    route_with_placeholders = None
    for route in request.app.router.routes:
        if route.endpoint == request.scope['endpoint']:
            route_with_placeholders = route.path
            break

    return {
        "current_path": current_path,
        "registered_path": route_with_placeholders,
    }


@fastapi.get("/lethimknowuncle/{varone}/{vartwo}")
def get_app1(request: Request, jasss: str, kass: str):
    # Get the current path
    current_path = request.url.path

    # Get the registered path with placeholders from the endpoint
    route_with_placeholders = None
    for route in request.app.router.routes:
        if route.endpoint == request.scope['endpoint']:
            route_with_placeholders = route.path
            break

    return {
        "current_path": current_path,
        "registered_path": route_with_placeholders,
    }
