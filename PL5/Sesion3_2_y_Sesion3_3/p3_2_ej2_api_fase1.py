from fastapi import FastAPI, Depends, HTTPException, Response
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

# Función para la inyección de dependencias
def get_repo() -> TaskRepository:
    return repo

@app.get("/")
def read_root():
    return {"mensaje": "¡Hola mundo!"}


# Rutas de la API

@app.get("/tasks", response_model=list[Task])
def list_tasks(repo: TaskRepository = Depends(get_repo)) -> list[Task]:
    return repo.get_all()

@app.post("/tasks", response_model=Task, status_code=201)
def create_task(task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    return repo.add(task_in)

@app.get("/tasks/{id}", response_model=Task)
def get_task(id: int, repo: TaskRepository = Depends(get_repo)) -> Task:
    task = repo.get_by_id(id)
    if not task:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return task

@app.put("/tasks/{id}", response_model=Task)
def update_task(id: int, task_in: TaskData, repo: TaskRepository = Depends(get_repo)) -> Task:
    tarea_actualizada = repo.update(id, task_in)
    if not tarea_actualizada:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return tarea_actualizada

@app.delete("/tasks/{id}", status_code=204)
def delete_task(id: int, repo: TaskRepository = Depends(get_repo)):
    borrada = repo.delete(id)
    if not borrada:
        raise HTTPException(status_code=404, detail="Tarea no encontrada")
    return Response(status_code=204)