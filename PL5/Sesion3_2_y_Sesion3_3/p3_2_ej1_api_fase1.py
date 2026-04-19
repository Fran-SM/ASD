from fastapi import FastAPI
from pydantic import BaseModel

class TaskData(BaseModel):
    descripcion: str
    completada: bool = False
class Task(TaskData):
    id: int

# Capa de datos

class TaskRepository:
    def __init__(self):
        self.tasks: list[Task] = []
        self.next_id = 1

    def _buscar_indice(self, id: int) -> int | None:
        """ Método para encontrar el índice de una tarea en la lista. Retorna el índice si la encuentra, o None si no existe"""
        for i, task in enumerate(self.tasks):
            if task.id == id:
                return i
        return None

    def get_all(self) -> list[Task]:
        """Retorna la lista con todas las tareas"""
        return self.tasks

    def get_by_id(self, id: int) -> Task | None:
        """Busca y retorna una tarea por su id. Si no existe, retorna None"""
        idx = self._buscar_indice(id)
        if idx is not None:
            return self.tasks[idx]
        return None

    def add(self, task_data: TaskData) -> Task:
        """Crea una nueva tarea, le asigna un id y la añade a la lista"""
        nueva_tarea = Task(id=self.next_id, **task_data.model_dump())
        self.tasks.append(nueva_tarea)
        self.next_id += 1
        return nueva_tarea

    def update(self, id: int, task_data: TaskData) -> Task | None:
        """Actualiza los datos de una tarea existente"""
        idx = self._buscar_indice(id)
        if idx is not None:
            tarea_actualizada = Task(id=id, **task_data.model_dump())
            self.tasks[idx] = tarea_actualizada
            return tarea_actualizada
        return None

    def delete(self, id: int) -> bool:
        """Elimina una tarea. Retorna True si se eliminó, False si no existía"""
        idx = self._buscar_indice(id)
        if idx is not None:
            self.tasks.pop(idx)
            return True
        return False


# Inicializacion


app = FastAPI()
repo = TaskRepository()

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola mundo!"}