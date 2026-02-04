from fastapi import FastAPI
import uvicorn

app = FastAPI()

books = [
    {
        "id": 1,
        "title": "Идиот",
        "author": "Достоевский",
    },
    {
        "id": 2,
        "title": "Вишневый сад",
        "author": "Чехов",
    },
]


@app.get("/books")
def read_books():
    return books


if __name__ == "__main__":
    uvicorn.run("main.py", reload=True)
