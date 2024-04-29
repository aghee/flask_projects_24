from typing import Optional
from fastapi import FastAPI
from fastapi.params import Body
from pydantic import BaseModel

app=FastAPI()

class Post(BaseModel):
    title:str
    content:str
    published:bool=False
    rating: Optional[int]=None

my_posts=[]

@app.get('/posts')
def get_posts():
    return {'data':'this is your post..'}

@app.get("/")
def root():
    return {"message": "Hi Agy"}

# @app.post("/createposts")
# def create_post(payload:dict= Body(...)):# take extract all fields from body convert to python dict then store in variable called payload
#     print(payload)
#     return {'new_message':f"title:{payload['title']} content:{payload['content']}"}

#title str, content str,category,Bool

@app.post("/posts")
def create_post(new_post:Post):
    # print(new_post.rating)
    print(new_post.model_dump())
    return {"data":new_post}