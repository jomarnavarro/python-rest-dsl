from handler.request_handler import TypiBase
import json

API = TypiBase("https://jsonplaceholder.typicode.com")
response = API.posts.id(1).GET()
print(response.status_code)
print(response.json())

   
   

data = {
    "title": "foo",
    "userId": 1
} 

postResponse = API.posts.POST(data=data)
print(postResponse.status_code)
print(postResponse.json())