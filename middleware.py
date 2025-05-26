import time
from fastapi import FastAPI, Request
app = FastAPI()
@app.middleware("http")
async def addmiddleware(request: Request, call_next):
   print("Middleware works!")
   response = await call_next(request)
   return response
@app.get("/")
async def index():
   return {"message":"Hello World"}
@app.get("/{name}")
async def hello(name:str):
   return {"message":"Hello "+name}