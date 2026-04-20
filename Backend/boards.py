from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from database import get_db, Board, BoardMember, Column, Task
from routers.auth import get_current_user, User

router = APIRouter()


class BoardCreate(BaseModel):
    title: str
    description: Optional[str] = None
    background_color: Optional[str] = "#0f172a"


class ColumnCreate(BaseModel):
    title: str
    color: Optional[str] = "#1e293b"


@router.get("/")
def list_boards(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    owned = db.query(Board).filter(Board.owner_id == current_user.id).all()
    member_boards = db.query(Board).join(BoardMember).filter(
        BoardMember.user_id == current_user.id,
        Board.owner_id != current_user.id
    ).all()

    def board_dict(b):
        return {
            "id": str(b.id),
            "title": b.title,
            "description": b.description,
            "background_color": b.background_color,
            "owner": {"id": str(b.owner.id), "name": b.owner.name},
            "task_count": db.query(Task).filter(Task.board_id == b.id).count(),
            "created_at": b.created_at.isoformat() if b.created_at else None,
        }

    return {"owned": [board_dict(b) for b in owned], "member": [board_dict(b) for b in member_boards]}


@router.post("/")
def create_board(data: BoardCreate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = Board(
        title=data.title,
        description=data.description,
        owner_id=current_user.id,
        background_color=data.background_color,
    )
    db.add(board)
    db.commit()
    db.refresh(board)

    # Colunas padrão
    default_cols = [("A Fazer", "#1e293b"), ("Em Andamento", "#1e3a5f"), ("Concluído", "#14291e")]
    for i, (title, color) in enumerate(default_cols):
        db.add(Column(board_id=board.id, title=title, position=i, color=color))
    db.commit()

    return {"id": str(board.id), "title": board.title, "description": board.description, "background_color": board.background_color}


@router.get("/{board_id}")
def get_board(board_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board não encontrado")

    is_owner = str(board.owner_id) == str(current_user.id)
    is_member = db.query(BoardMember).filter(BoardMember.board_id == board_id, BoardMember.user_id == current_user.id).first()
    if not is_owner and not is_member:
        raise HTTPException(status_code=403, detail="Acesso negado")

    columns_data = []
    for col in board.columns:
        tasks_data = []
        for task in sorted(col.tasks, key=lambda t: t.position):
            tasks_data.append({
                "id": str(task.id),
                "title": task.title,
                "description": task.description,
                "urgency": task.urgency,
                "completed": task.completed,
                "position": task.position,
                "due_date": task.due_date.isoformat() if task.due_date else None,
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
                "tags": [{"label": t.label, "color": t.color} for t in task.tags],
                "comments_count": len(task.comments),
            })
        columns_data.append({
            "id": str(col.id),
            "title": col.title,
            "color": col.color,
            "position": col.position,
            "tasks": tasks_data,
        })

    return {
        "id": str(board.id),
        "title": board.title,
        "description": board.description,
        "background_color": board.background_color,
        "owner": {"id": str(board.owner.id), "name": board.owner.name},
        "columns": columns_data,
    }


@router.delete("/{board_id}")
def delete_board(board_id: str, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    board = db.query(Board).filter(Board.id == board_id).first()
    if not board:
        raise HTTPException(status_code=404, detail="Board não encontrado")
    if str(board.owner_id) != str(current_user.id):
        raise HTTPException(status_code=403, detail="Apenas o dono pode excluir o board")
    db.delete(board)
    db.commit()
    return {"ok": True}
