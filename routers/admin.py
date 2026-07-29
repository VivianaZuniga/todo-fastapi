from database import db_dependency
from pydantic import BaseModel, Field
from fastapi import APIRouter, HTTPException, Path, Depends
from starlette import status
from models import Todos
from .auth import get_current_user
from typing_extensions import Annotated


router = APIRouter(
    prefix= '/admin',
    tags=['admin'],
)

user_dependency = Annotated[dict, Depends(get_current_user)] 


@router.get("/todos", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependency, db: db_dependency):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failed, because you are not an admin")
    return db.query(Todos).all()


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
    if user is None or user.get('role') != 'admin':
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Authentication Failes, because you are not an admin")
    
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()

    if todo_model is None:
        raise HTTPException(status_code=404, detail="Todo not found")
    
    db.query(Todos).filter(Todos.id == todo_id).delete()
    db.commit()