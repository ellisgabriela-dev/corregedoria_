from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from datetime import date
import uuid
from database import get_db, Task, Column, Board, BoardMember, ActivityLog
from routers.auth import get_current_user, User

router = APIRouter()


class TaskCreate(BaseModel):
    column_id: str
    title: str
    description: Optional[str] = None
    demand_type_id: Optional[str] = None
    urgency: str = "medio"
    assignee_id: Optional[str] = None
    due_date: Optional[date] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    description: Optional[str] = None
    demand_type_id: Optional[str] = None
    urgency: Optional[str] = None
    assignee_id: Optional[str] = None
    due_date: Optional[date] = None
    column_id: Optional[str] = None
    completed: Optional[bool] = None
    position: Optional[int] = None


def check_board_access(board_id: str, user_id: str, db: Session):
    is_member = db.query(BoardMember).filter(
        BoardMember.board_id == board_id,
        BoardMember.user_id == user_id
    ).first()
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board or (str(board.owner_id) != str(user_id) and not is_member):
        raise HTTPException(status_code=403, detail="Acesso negado a este board")
    return board


def task_to_dict(task: Task):
    return {
        "id": str(task.id),
        "column_id": str(task.column_id),
        "board_id": str(task.board_id),
        "title": task.title,
        "description": task.description,
        "urgency": task.urgency,
        "completed": task.completed,
        "position": task.position,
        "due_date": task.due_date.isoformat() if task.due_date else None,
        "created_at": task.created_at.isoformat() if task.created_at else None,
        "demand_type": {
            "id": str(task.demand_type.id),
            "name": task.demand_type.name,
            "color": task.demand_type.color,
            "icon": task.demand_type.icon,
        } if task.demand_type else None,
        "assignee": {
            "id": str(task.assignee.id),
            "name": task.assignee.name,
            "avatar_color": task.assignee.avatar_color,
        } if task.assignee else None,
        "created_by": {
            "id": str(task.created_by_user.id),
            "name": task.created_by_user.name,
        } if task.created_by_user else None,
        "tags": [{"id": str(t.id), "label": t.label, "color": t.color} for t in task.tags],
        "comments_count": len(task.comments),
    }


@router.post("/")
def create_task(data: TaskCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    column = db.query(Column).filter(Column.id == data.column_id).first()
    if not column:
        raise HTTPException(status_code=404, detail="Coluna não encontrada")

    check_board_access(str(column.board_id), str(current_user.id), db)

    max_pos = db.query(Task).filter(Task.column_id == data.column_id).count()

    task = Task(
        column_id=data.column_id,
        board_id=column.board_id,
        title=data.title,
        description=data.description,
        demand_type_id=data.demand_type_id,
        urgency=data.urgency,
        assignee_id=data.assignee_id,
        due_date=data.due_date,
        created_by=current_user.id,
        position=max_pos,
    )
    db.add(task)
    db.commit()
    db.refresh(task)

    db.add(ActivityLog(
        board_id=column.board_id,
        task_id=task.id,
        user_id=current_user.id,
        action="task_created",
        details={"title": task.title}
    ))
    db.commit()

    return task_to_dict(task)


@router.patch("/{task_id}")
def update_task(task_id: str, data: TaskUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    check_board_access(str(task.board_id), str(current_user.id), db)

    for field, value in data.dict(exclude_none=True).items():
        setattr(task, field, value)

    db.commit()
    db.refresh(task)
    return task_to_dict(task)


@router.delete("/{task_id}")
def delete_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")

    check_board_access(str(task.board_id), str(current_user.id), db)
    db.delete(task)
    db.commit()
    return {"ok": True}


@router.get("/{task_id}")
def get_task(task_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    task = db.query(Task).filter(Task.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Tarefa não encontrada")
    check_board_access(str(task.board_id), str(current_user.id), db)
    return task_to_dict(task)
