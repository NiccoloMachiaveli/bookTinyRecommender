from fastapi import FastAPI, HTTPException
import uvicorn
from pydantic import BaseModel, Field, EmailStr

app = FastAPI()


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    age: int = Field(ge=0, le=120)
    interests: str | None = Field(max_length=500)


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

users = []


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


@app.post("/users",
          tags=["Пользователь"],
          summary="Добавление пользователя")
def add_users(user: UserSchema):
    users.append(user)
    return {"success": True, "message": "Пользователь успешно добавлен"}


@app.get("/users",
         tags=["Пользователь"],
         summary="Получение всех пользователей")
def get_users() -> list[UserSchema]:
    return users


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
