import enum
import databases
import sqlalchemy
from typing import Optional
from datetime import datetime
from decouple import config
from pydantic import BaseModel, validator
from fastapi import FastAPI, Request
from passlib.context import CryptContext
from email_validator import validate_email as validate_e, EmailNotValidError

# Mine is this, please change for your credentials
# DATABASE_URL = "postgresql://postgres:ines123@localhost:5433/store"

# DATABASE_URL = "postgresql://{place your db user}:{db password}@localhost:{your port}/{db name}"

DATABASE_URL = f"postgresql://{config('DB_USER')}:{config('DB_PASSWORD')}@localhost:5432/store"

database = databases.Database(DATABASE_URL)

metadata = sqlalchemy.MetaData()

books = sqlalchemy.Table(
    "books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("title", sqlalchemy.String),
    sqlalchemy.Column("author", sqlalchemy.String),
)

readers = sqlalchemy.Table(
    "readers",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("first_name", sqlalchemy.String),
    sqlalchemy.Column("last_name", sqlalchemy.String),
)

readers_books = sqlalchemy.Table(
    "readers_books",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy. Column("book_id", sqlalchemy.ForeignKey("books.id"), nullable=False, index=True),
    sqlalchemy.Column("reader_id", sqlalchemy.ForeignKey("readers.id"), nullable=False, index=True),
)


users = sqlalchemy.Table(
    "users",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("email", sqlalchemy.String(120), unique=True),
    sqlalchemy.Column("password", sqlalchemy.String(255)),
    sqlalchemy.Column("full_name", sqlalchemy.String(200)),
    sqlalchemy.Column("phone", sqlalchemy.String(13)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


class ColorEnum(enum.Enum):
    pink = "pink"
    black = "black"
    white = "white"
    yellow = "yellow"


class SizeEnum(enum.Enum):
    xs = "xs"
    s = "s"
    m = "m"
    l = "l"
    xl = "xl"
    xxl = "xxl"


clothes = sqlalchemy.Table(
    "clothes",
    metadata,
    sqlalchemy.Column("id", sqlalchemy.Integer, primary_key=True),
    sqlalchemy.Column("name", sqlalchemy.String(120)),
    sqlalchemy.Column("color", sqlalchemy.Enum(ColorEnum), nullable=False),
    sqlalchemy.Column("size", sqlalchemy.Enum(SizeEnum), nullable=False),
    sqlalchemy.Column("photo_url", sqlalchemy.String(255)),
    sqlalchemy.Column("created_at", sqlalchemy.DateTime, nullable=False, server_default=sqlalchemy.func.now()),
    sqlalchemy.Column(
        "last_modified_at",
        sqlalchemy.DateTime,
        nullable=False,
        server_default=sqlalchemy.func.now(),
        onupdate=sqlalchemy.func.now(),
    ),
)


class EmailField(str):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v) -> str:
        try:
            validate_e(v)
            return v
        except EmailNotValidError:
            raise ValueError("Email is not valid!")


class BaseUser(BaseModel):
    # email: str
    email: EmailField
    full_name: str

    # @validator('email')
    # def validate_email(cls, v):
    #     try:
    #         validate_e(v)
    #         return v
    #     except EmailNotValidError:
    #         raise ValueError("Email is not valid!")


class UserSignIn(BaseUser):
    password: str


class UserSignOut(BaseUser):
    phone: Optional[str]
    created_at: datetime
    last_modified_at: datetime


# engine = sqlalchemy.create_engine(DATABASE_URL)
# metadata.create_all(engine)

app = FastAPI()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@app.on_event("startup")
async def startup():
    await database.connect()


@app.on_event("shutdown")
async def shutdown():
    await database.disconnect()


@app.post("/register", status_code=201, response_model=UserSignOut)
async def create_user(user: UserSignIn):
    user.password = pwd_context.hash(user.password)
    q = users.insert().values(**user.dict())
    id_ = await database.execute(q)
    user = await database.fetch_one(users.select().where(users.c.id == id_))
    return user


@app.get("/books/")
async def read_books():
    query = books.select()
    return await database.fetch_all(query)


@app.post("/books/")
async def create_book(request: Request):
    data = await request.json()
    query = books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}


@app.post("/readers/")
async def create_reader(request: Request):
    data = await request.json()
    query = readers.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}


@app.post("/read/")
async def read_book(request: Request):
    data = await request.json()
    query = readers_books.insert().values(**data)
    last_record_id = await database.execute(query)
    return {"id": last_record_id}


"""
pip install alembic

alembic init migrations

Need to configure the env.py file:
from main import metadata

target_metadata = metadata


alembic revision --autogenerate -m "initial"
alembic upgrade head

"""