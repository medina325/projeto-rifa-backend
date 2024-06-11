from fastapi import FastAPI
from app.routes import oauth2

app = FastAPI()

app.include_router(oauth2.router, prefix="/oauth", tags=["oauth"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
