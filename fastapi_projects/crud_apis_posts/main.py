from typing import Optional
from fastapi import FastAPI,Response,status,HTTPException
from fastapi.params import Body
from pydantic import BaseModel
from random import randrange

app=FastAPI()

# schema
class Post(BaseModel):
    title:str
    content:str
    published:bool=False
    rating: int | None =None

my_posts=[{"title":"endmonth training","content":"dinner planner meeting","id":1},
          {"title":"viola davis movies","content":"How to get away with murder","id":2},{"title":"Floods in kenya",
"content":"Elnino in kenya is here","id":3}]

@app.get('/posts')
def get_posts():
    return {'data':my_posts}


@app.get("/")
def root():
    return {"message": "Hi Agy"}

@app.post("/posts",status_code=status.HTTP_201_CREATED)
def create_post(new_post:Post):
    dict_post=new_post.model_dump()
    dict_post['id']=randrange(0,25000)
    my_posts.append(dict_post)
    print(dict_post)
    return {"data":dict_post}

def find_one_post(id):
    for post in my_posts:
        if post['id'] == id:
            return post
     
@app.get("/posts/{id}")
def get_one_post(id:int,response:Response):
    one_post=find_one_post(id)
    if not one_post:
        # response.status_code=404
        # response.status_code=status.HTTP_404_NOT_FOUND
        # return {"info":"post with {} missing".format(id)}
        raise HTTPException(status.HTTP_404_NOT_FOUND,detail="post with id {} missing".format(id))
    return {"about_post":one_post}

# def delete_item(id):
#     for index,item in enumerate(my_posts,0):
#         if item["id"] ==id:
#             my_posts.pop(index)

def find_index(id):
    for index,item in enumerate(my_posts):
        if item['id'] ==id:
            return index

@app.delete('/posts/{id}',status_code=status.HTTP_204_NO_CONTENT)
def delete_posts(id:int):
    # delete_item(id)
    item_index=find_index(id)
    if item_index ==None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="post with id {} does not exist".format(id))
    my_posts.pop(item_index)
    return Response(status_code=status.HTTP_204_NO_CONTENT)






# @app.post("/createposts")
# def create_post(payload:dict= Body(...)):# take extract all fields from body 
# convert to python dict then store in variable called payload
#     print(payload)
#     return {'new_message':f"title:{payload['title']} content:{payload['content']}"}

#title str, content str,category,Bool