class DBSession:
    tasks = {}

    def __init__(self):
        self.tasks = DBSession.tasks

    def delete_task_by_id(self, task_id):
        del self.tasks[task_id]


def get_db():
    return DBSession()
