"""ExpenseFlow FastAPI application entry point."""

from fastapi import FastAPI

from app.db import init_db
from app.routes import router

app = FastAPI(title="ExpenseFlow", description="Expense submission and approval API")
app.include_router(router)


@app.on_event("startup")
def on_startup() -> None:
    """Ensure the database schema exists before serving requests."""
    init_db()
