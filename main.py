from fastapi import FastAPI

from adapters.database import engine, Base
from routes import user, post

Base.metadata.create_all(bind=engine)
app = FastAPI()

app.include_router(user.router)
app.include_router(post.router)


@app.get("/")
async def root():
    return {"message": "Swagger available on route /docs"}
