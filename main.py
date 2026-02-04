from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel

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


@app.get("/books",
         tags=["Книги"],
         summary="Получить все книги")
def read_books():
    return books


@app.get("/books/{id}",
         tags=["Книги"],
         summary="Получить конкретную книгу")
def get_book(id: int):
    for book in books:
        if id == book["id"]:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


class NewBook(BaseModel):
    title: str
    author: str


@app.post("/books",
          tags=["Книги"],
          summary="Добавление новой книги")
def create_book(new_book: NewBook):
    books.append({
        "id": len(books) + 1,
        "title": new_book.title,
        "author": new_book.author,
    })
    return {"success": True, "message": "Книга успешно добавлена"}


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
