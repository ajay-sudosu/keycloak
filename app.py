from fastapi import FastAPI
from fastapi.responses import HTMLResponse
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

response = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Home Page</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }
        header {
            background-color: #333;
            color: #fff;
            padding: 10px 0;
            text-align: center;
        }
        nav {
            margin: 20px 0;
            text-align: center;
        }
        nav a {
            margin: 0 15px;
            color: #333;
            text-decoration: none;
            font-weight: bold;
        }
        .container {
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #fff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
        }
        footer {
            background-color: #333;
            color: #fff;
            text-align: center;
            padding: 10px 0;
            position: fixed;
            bottom: 0;
            width: 100%;
        }
    </style>
</head>
<body>

    <header>
        <h1>Welcome to My Website</h1>
    </header>

    <nav>
        <a href="#">Home</a>
        <a href="#">About</a>
        <a href="#">Services</a>
        <a href="#">Contact</a>
    </nav>

    <div class="container">
        <h2>Home Page</h2>
        <p>This is the home page of my awesome website. Here you can find information about what we do and how we can help you.</p>
    </div>

    <footer>
        <p>&copy; 2024 My Website. All rights reserved.</p>
    </footer>

</body>
</html>

"""


@app.get("/")
def health_check():
    """
    Health Check API
    """
    return HTMLResponse(response)


@app.get("/redirect")
def health_check():
    """
    Health Check API
    """
    return "Google!"
