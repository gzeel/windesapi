from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.database import initialize_database
from app.routers import admin, auth, courses, legacy, users


LOGO_URL = "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcSv4OLoVaIPJc2VWDiI2yNOVp21OKciAgEfTw&s"


@asynccontextmanager
async def lifespan(app: FastAPI):
    initialize_database()
    yield


app = FastAPI(
    title="WindesAPI",
    description="Lokaal draaiende demo-API met bewust ingebouwde kwetsbaarheden voor onderwijs.",
    version="2.0.0-demo",
    lifespan=lifespan,
)


@app.get("/", response_class=HTMLResponse, include_in_schema=False)
def landing_page() -> str:
    return f"""
    <!doctype html>
    <html lang="nl">
      <head>
        <meta charset="utf-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>WindesAPI</title>
        <style>
          body {{
            align-items: center;
            background: #f5f7fb;
            color: #172033;
            display: flex;
            font-family: Arial, sans-serif;
            justify-content: center;
            margin: 0;
            min-height: 100vh;
          }}
          main {{
            background: white;
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(23, 32, 51, 0.14);
            max-width: 680px;
            padding: 44px;
            text-align: center;
          }}
          img {{ max-width: 220px; width: 65%; }}
          h1 {{ font-size: 2.6rem; margin: 24px 0 8px; }}
          p {{ font-size: 1.05rem; line-height: 1.6; }}
          a {{ color: #005aa7; font-weight: 700; }}
        </style>
      </head>
      <body>
        <main>
          <img src="{LOGO_URL}" alt="WindesAPI logo">
          <h1>WindesAPI</h1>
          <p>Lokaal draaiende insecure-by-design demo-API voor cybersecurityonderwijs.</p>
          <p><a href="/docs">Open API documentatie</a> of test <a href="/health">/health</a>.</p>
        </main>
      </body>
    </html>
    """


@app.get("/health")
def health() -> dict:
    return {"status": "ok", "service": "WindesAPI"}


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(courses.router)
app.include_router(admin.router)
app.include_router(legacy.router)
