import redis.asyncio as redis
from fastapi import FastAPI, Depends, HTTPException
from fastapi_limiter import FastAPILimiter
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.routes import users, auth, comments  
from src.database.db import get_db
from src.services.middlewares import ProcessTimeHeaderMiddleware
from src.conf.config import config

app = FastAPI()

origins = [
    "http://localhost:8000"
]

app.add_middleware(ProcessTimeHeaderMiddleware)
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router, prefix='/api')
app.include_router(users.routerUsers, prefix='/api')
app.include_router(comments.router, prefix='/api') 



@app.on_event("startup")
async def startup():
    """
    Initializes the Redis connection and FastAPI Limiter on application startup.

    This function is called when the FastAPI application starts up. It establishes a connection to the Redis database
    using the configuration settings from the `config` module, and then initializes the FastAPI Limiter using the
    Redis connection.

    :return: None
    """
    r = await redis.Redis(host=config.REDIS_DOMAIN, port=config.REDIS_PORT, db=0, password=config.REDIS_PASSWORD)
    await FastAPILimiter.init(r)


@app.get("/api/healthchecker")
async def healthchecker(db: AsyncSession = Depends(get_db)):
    """
   Health check endpoint to verify the API's connection to the database.

   Returns a success message if the database connection is established,
   otherwise raises an HTTP exception with a 500 status code.

   :raises HTTPException: If the database is not configured correctly or
       an error occurs while connecting to the database.
   :return: A dictionary containing a welcome message.
   """
    try:
        result = await db.execute(text("SELECT 1"))
        result = result.fetchone()
        if result is None:
            raise HTTPException(status_code=500, detail="Database is not configured correctly")
        return {"message": "Welcome to FastAPI!"}
    except Exception as e:
        print(e)
        raise HTTPException(status_code=500, detail="Error connecting to the database")


@app.get("/")
async def root():
    """
    Root endpoint of the API, serving as a navigation page.

    :return: A dictionary containing a message indicating the navigation page.
    """
    return {"message": "Navigation page"}
