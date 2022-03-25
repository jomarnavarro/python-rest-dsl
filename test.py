from handler.request_handler import TypiBase

API = TypiBase("https://jsonplaceholder.typicode.com")
response = API.posts.id(1).GET()
print(response.status_code)
print(response.json())