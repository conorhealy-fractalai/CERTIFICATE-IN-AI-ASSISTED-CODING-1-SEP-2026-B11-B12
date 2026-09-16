"""ExpenseFlow FastAPI application entry point."""

from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db import init_db
from app.routes import router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Ensure the database schema exists before serving requests."""
    init_db()
    yield


app = FastAPI(
    title="ExpenseFlow",
    description="Expense submission and approval API",
    lifespan=lifespan,
)
app.include_router(router)
