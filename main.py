from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from app.routers import oauth2, users, rifas

app = FastAPI()
app.mount("/files", StaticFiles(directory="files"), name="files")

app.include_router(oauth2.router, prefix='/oauth', tags=['oauth'])
app.include_router(users.router, prefix='/users', tags=['users'])
app.include_router(rifas.router, prefix='/rifas', tags=['rifas'])

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
