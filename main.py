from fastapi import FastAPI
from app.routes import oauth2
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

app.include_router(oauth2.router, prefix='/oauth', tags=['oauth'])
app.add_middleware(
    CORSMiddleware,
    allow_origins=['http://localhost:5173'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='127.0.0.1', port=8000)
