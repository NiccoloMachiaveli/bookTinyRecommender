from typing import Annotated

from fastapi import FastAPI, HTTPException, Depends, Response
import uvicorn
from pydantic import BaseModel, Field, EmailStr

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column

from authx import AuthX, AuthXConfig

app = FastAPI()

config = AuthXConfig()
config.JWT_SECRET_KEY = "SECRET_KEY"
config.JWT_ACCESS_COOKIE_NAME = "my_access_token"
config.JWT_TOKEN_LOCATION = ["cookies"]

security = AuthX(config=config)


engine = create_async_engine('sqlite+aiosqlite:///books.db')

new_session = async_sessionmaker(engine, expire_on_commit=False)


async def get_session():
    async with new_session() as session:
        yield session


SessionDep = Annotated[AsyncSession, Depends(get_session)]


class Base(DeclarativeBase):
    pass


class BookModel(Base):
    __tablename__ = "books"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str]
    author: Mapped[str]


@app.post("/setup_database")
async def setup_database():
    async with engine.begin() as connect:
        await connect.run_sync(Base.metadata.drop_all)
        await connect.run_sync(Base.metadata.create_all)
    return {"success": True, "message": "База данных настроенна"}


class BookAddSchema(BaseModel):
    title: str
    author: str


class BookSchema(BookAddSchema):
    id: int


class UserSchema(BaseModel):
    id: int
    email: EmailStr
    age: int = Field(ge=0, le=120)
    interests: str | None = Field(max_length=500)
    password: str


class UserLoginSchema(BaseModel):
    email: str
    password: str


users = []


@app.post("/login")
def login(creds: UserLoginSchema, response: Response):
    _id = 0
    for user in users:
        user_id = 0
        if creds.email == user.email:
            _id = user_id
            break
        user_id += 1
    else:
        raise HTTPException(status_code=404, detail="User not found")

    user = users[_id]

    if creds.email == user.email and creds.password == user.password:
        token = security.create_access_token(uid=str(user.id))
        response.set_cookie(config.JWT_ACCESS_COOKIE_NAME, token)
        return {"access_token": token}
    return HTTPException(status_code=401, detail="Incorrect email or password")


@app.post("/books",
          tags=["Книги"],
          summary="Добавление новой книги в базу данных",
          dependencies=[Depends(security.access_token_required)])
async def create_book(data: BookAddSchema, session: SessionDep):
    new_book = BookModel(
        title=data.title,
        author=data.author
    )
    session.add(new_book)
    await session.commit()
    return {"success": True, "message": "Книга успешно добавлена"}


@app.get("/books",
         tags=["Книги"],
         summary="Получить все книги")
async def read_books(session: SessionDep):
    query = select(BookModel)
    result = await session.execute(query)
    return result.scalars().all()


@app.get("/books/{id}",
         tags=["Книги"],
         summary="Получить конкретную книгу из базы данных")
async def get_book(id: int, session: SessionDep):
    books = await read_books(session)

    for book in books:
        if id == book.id:
            return book
    raise HTTPException(status_code=404, detail="Книга не найдена")


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
