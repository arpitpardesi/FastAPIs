import shutil
from cgitb import reset
from http.client import responses

import uvicorn
from fastapi import FastAPI, Request, Form, UploadFile, File, Cookie, Header, Depends, HTTPException
from pydantic import BaseModel, Field
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Optional, Tuple
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
import requests, json

app = FastAPI()
templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")

origins = [
   "http://192.168.211.:8000",
   "http://localhost",
   "http://localhost:8080",
]
app.add_middleware(
   CORSMiddleware,
   allow_origins=origins,
   allow_credentials=True,
   allow_methods=["*"],
   allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get('/test')
async def test():
    return "Test"


@app.get("/weather/{city}&{country}")
async def weather(city, country):
    key = '7c72a8068348029a34834c9aa081e131'
    units = 'metric'
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&APPID={key}&units={units}"

    r = requests.get(api)

    if r.status_code == 200:
        response = r.json()
        # print(response)
        city = response["name"]
        temp = response['main']['temp']

        res = f"""City: {city}
        Temp: {temp}
        """
        return res
    else:
        return "Unable to fetch data"


@app.get("/weather")
async def weather(city: str, country: str):
    key = '7c72a8068348029a34834c9aa081e131'
    units = 'metric'
    api = f"https://api.openweathermap.org/data/2.5/weather?q={city},{country}&APPID={key}&units={units}"

    r = requests.get(api)

    if r.status_code == 200:
        response = r.json()
        # print(response)
        city = response["name"]
        temp = response['main']['temp']

        res = f"""City: {city}
        Temp: {temp}
        """
        return response
    else:
        return "Unable to fetch data"


class Employee(BaseModel):
    id: int
    name: str = Field(None, title="Employee Name", max_length=30)


@app.post("/emp")
async def emp(s1: Employee):
    return f"Hi {s1.name}, your ID is {s1.id}"


@app.get("/hello", response_class=HTMLResponse)
async def hello(request: Request):
    # html = ("""
    # <title>Test Page</title>
    # <div>
    # <p>Hello<br>
    # <h1>Arpit</h1>
    # </p>
    # </div>
    # """)

    # return HTMLResponse(content=html)
    return templates.TemplateResponse("hello.html", {"request": request})


@app.get("/hello/{name}", response_class=HTMLResponse)
async def static(request: Request, name: str):
    return templates.TemplateResponse("hello.html", {"request": request, "name": name})


@app.get("/login/", response_class=HTMLResponse)
async def login(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})


@app.post("/submit/")
async def submit(nm: str = Form(...), pwd: str = Form(...)):
    return {"username": nm}


@app.get("/upload/", response_class=HTMLResponse)
async def upload(request: Request):
    return templates.TemplateResponse("uploadfile.html", {"request": request})


@app.post("/uploader/")
async def create_upload_file(file: UploadFile = File(...), fileName: str = Form(...)):
    with open(f"uploads/{file.filename}", "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return {"filename": file.filename}



@app.post("/cookie/")
async def cookie():
    cont = {"message":"cookie set"}
    res = JSONResponse(content=cont)
    res.set_cookie(key="username", value="admin")
    return res

@app.get('/readcookie/')
async def read_cookie(username: str = Cookie(None)):
    return {"username":username}

@app.get("/headers/")
async def read_header(accept_language: Optional[str] = Header(None)):
   return {"Accept-Language": accept_language}

class student(BaseModel):
   id: int
   name :str = Field(None, title="name of student", max_length=10)
   marks: List[int] = []
   percent_marks: float
class percent(BaseModel):
   id:int
   name :str = Field(None, title="name of student", max_length=10)
   percent_marks: float
@app.post("/marks", response_model=percent)
async def get_percent(s1:student):
   s1.percent_marks=sum(s1.marks)/2
   return s1

class supplier(BaseModel):
   supplierID:int
   supplierName:str
class product(BaseModel):
   productID:int
   prodname:str
   price:int
   supp:supplier
class customer(BaseModel):
   custID:int
   custname:str
   prod:Tuple[product]

@app.post('/invoice')
async def getInvoice(c1:customer):
   return c1

class dependency:
   def __init__(self, id: str, name: str, age: int):
      self.id = id
      self.name = name
      self.age = age

# @app.get("/user/")
# async def user(dep: dependency = Depends(dependency)):
#    return dep
# @app.get("/admin/")
# async def admin(dep: dependency = Depends(dependency)):
#    return dep

async def validate(dep: dependency = Depends(dependency)):
   if dep.age > 18:
      raise HTTPException(status_code=400, detail="You are not eligible")
@app.get("/user/", dependencies=[Depends(validate)])
async def user():
   return {"message": "You are eligible"}

from flask import Flask
flask_app = Flask(__name__)
@flask_app.route("/")
def index_flask():
   return "Hello World from Flask!"

from fastapi.middleware.wsgi import WSGIMiddleware
app.mount("/flask", WSGIMiddleware(flask_app))

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)

