import uuid

from typing import Optional, Dict

from fastapi import HTTPException, Depends, APIRouter
from ..database import DBSession, get_db
from ..models import Task

router = APIRouter()

@router.get(
    '',
    summary='Reads task list',
    description='Reads the whole task list.',
    response_model=Dict[uuid.UUID, Task],
)
async def read_tasks(
    completed: bool = None,
    db: DBSession = Depends(get_db)
):
    if completed is None:
        return db.tasks
    return {
        uuid_: item
        for uuid_, item in db.tasks.items() if item.completed == completed
    }


@router.post(
    '',
    summary='Creates a new task',
    description='Creates a new task and returns its UUID.',
    response_model=uuid.UUID,
)
async def create_task(
    item: Task,
    db: DBSession = Depends(get_db)
    ):
    # if type(item) != Task:
    #   pass
    uuid_ = uuid.uuid4()
    db.tasks[uuid_] = item
    return uuid_


@router.get(
    '/{uuid_}',
    summary='Reads task',
    description='Reads task from UUID.',
    response_model=Task,
)
async def read_task(
    uuid_: uuid.UUID,
    db: DBSession = Depends(get_db),
):

    try:
        if db.tasks[uuid_]:
            return db.tasks[uuid_]
        else:
            raise KeyError
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.put(
    '/{uuid_}',
    summary='Replaces a task',
    description='Replaces a task identified by its UUID.',
)
async def replace_task(
    uuid_: uuid.UUID,
    item: Task,
    db: DBSession = Depends(get_db)
):
    try:
        if db.tasks[uuid_]:
            db.tasks[uuid_] = item
            return db.tasks[uuid_]
        else:
            raise KeyError  
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.patch(
    '/{uuid_}',
    summary='Alters task',
    description='Alters a task identified by its UUID',
)
async def alter_task(
    uuid_: uuid.UUID,
    item: Task,
    db: DBSession = Depends(get_db)
):
    try:
        update_data = item.dict(exclude_unset=True)
        db.tasks[uuid_] = db.tasks[uuid_].copy(update=update_data)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception


@router.delete(
    '/{uuid_}',
    summary='Deletes task',
    description='Deletes a task identified by its UUID',
)
async def remove_task(
    uuid_: uuid.UUID,
    db: DBSession = Depends(get_db)
):
    try:
        db.delete_task_by_id(uuid_)
    except KeyError as exception:
        raise HTTPException(
            status_code=404,
            detail='Task not found',
        ) from exception
