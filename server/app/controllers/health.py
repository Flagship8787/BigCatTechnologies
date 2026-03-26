from fastapi import FastAPI

def register(app: FastAPI):
    @app.get('/health')
    def health(): return { 'status': 'ok' }