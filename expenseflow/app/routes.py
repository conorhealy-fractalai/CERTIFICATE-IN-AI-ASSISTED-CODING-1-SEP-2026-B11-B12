"""API routes for ExpenseFlow: expense CRUD, approval workflow, insights, health."""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.db import get_db
from app.insights import generate_insight
from app.models import Expense
from app.schemas import ExpenseCreate, ExpenseOut, HealthOut, InsightOut

router = APIRouter()


def _ensure_not_terminal(expense: Expense) -> None:
    """Raise 409 if the expense is already approved or rejected."""
    if expense.status in ("approved", "rejected"):
        raise HTTPException(status_code=409, detail=f"Expense is already {expense.status}")


@router.post("/expenses", response_model=ExpenseOut)
def create_expense(payload: ExpenseCreate, db: Session = Depends(get_db)) -> Expense:
    """Submit a new expense. Status starts as 'pending'."""
    # TODO: replace with a real FX lookup (e.g. via httpx) once a rate source is chosen.
    amount_base_minor = payload.amount_minor

    expense = Expense(
        description=payload.description,
        submitted_by=payload.submitted_by,
        category=payload.category,
        amount_minor=payload.amount_minor,
        currency=payload.currency.upper(),
        amount_base_minor=amount_base_minor,
        status="pending",
    )
    db.add(expense)
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/expenses", response_model=list[ExpenseOut])
def list_expenses(
    status: str | None = None,
    category: str | None = None,
    db: Session = Depends(get_db),
) -> list[Expense]:
    """List expenses, optionally filtered by status and/or category."""
    query = db.query(Expense)
    if status is not None:
        query = query.filter(Expense.status == status)
    if category is not None:
        query = query.filter(Expense.category == category)
    return query.order_by(Expense.id).all()


@router.get("/expenses/{expense_id}", response_model=ExpenseOut)
def get_expense(expense_id: int, db: Session = Depends(get_db)) -> Expense:
    """Get a single expense by id, or 404 if it does not exist."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    return expense


@router.post("/expenses/{expense_id}/approve", response_model=ExpenseOut)
def approve_expense(expense_id: int, db: Session = Depends(get_db)) -> Expense:
    """Mark an expense as approved. 409 if it is already approved or rejected."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    _ensure_not_terminal(expense)
    expense.status = "approved"
    db.commit()
    db.refresh(expense)
    return expense


@router.post("/expenses/{expense_id}/reject", response_model=ExpenseOut)
def reject_expense(expense_id: int, db: Session = Depends(get_db)) -> Expense:
    """Mark an expense as rejected. 409 if it is already approved or rejected."""
    expense = db.get(Expense, expense_id)
    if expense is None:
        raise HTTPException(status_code=404, detail="Expense not found")
    _ensure_not_terminal(expense)
    expense.status = "rejected"
    db.commit()
    db.refresh(expense)
    return expense


@router.get("/reports/insights", response_model=InsightOut)
def get_insights(db: Session = Depends(get_db)) -> dict:
    """Return an AI-generated summary of spending across stored expenses."""
    expenses = db.query(Expense).all()
    expense_dicts = [
        {
            "amount_base_minor": e.amount_base_minor,
            "currency": e.currency,
            "category": e.category,
            "status": e.status,
        }
        for e in expenses
    ]
    return generate_insight(expense_dicts)


@router.get("/health", response_model=HealthOut)
def health(db: Session = Depends(get_db)) -> dict:
    """Health check: reports service status and the number of stored expenses."""
    count = db.query(func.count(Expense.id)).scalar()
    return {"status": "ok", "count": count}
