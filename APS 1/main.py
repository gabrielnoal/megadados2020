from typing import Optional, List
from pydantic import BaseModel
from fastapi import Body, FastAPI, status

app = FastAPI()


class Task(BaseModel):
    task_id: str
    description: Optional[str] = None
    done: bool = False
    deleted: bool = False


class Task_Input(BaseModel):
    description: Optional[str] = ''
    done: Optional[bool] = False
    deleted: bool = False


tasks = {
    '0': Task(
      task_id = 0,
      description = 'Very nice description',
      done=True
    )
}


@app.get("/", response_model = List[Task])
def get_tasks():
    filteredTasks = []
    for task in tasks.values():
      print(task)
      if task.deleted == False:
        filteredTasks.append(task)
    return filteredTasks


@app.post("/task/", response_model=Task)
def create_task(
    body: Task_Input = Body(..., embed=True),
    example = { "description": "A very nice description" }
):
    task_dic = body.dict()
    new_id = len(tasks.keys())
    tasks[str(new_id)] = Task(task_id = new_id, **task_dic)
    return tasks[str(new_id)]


@app.patch("/task/{task_id}", response_model=Task)
def update_task(
  task_id: str,
  body: Task_Input = Body(..., embed=True),
):
    print(body)
    tasks[str(task_id)] = Task(task_id = task_id, **body.dict())

    return tasks[str(task_id)]

@app.patch('/task/delete/{task_id}', response_model = str)
def soft_delete_task(task_id = str):
    if tasks[task_id]:
      update_task(task_id, Task_Input(**tasks[task_id].dict(), deleted = True))
      
    return 'updateOk'


@app.delete("/task/{task_id}", response_model = str)
def delete_task(task_id: str):
    if tasks[task_id]:
      tasks.pop(str(task_id))

    return 'updateOk'
