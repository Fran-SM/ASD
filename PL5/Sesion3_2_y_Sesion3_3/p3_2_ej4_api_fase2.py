from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlmodel import SQLModel, Field, create_engine, Session, select


DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

def create_db_and_tables():
    """Crea las tablas en la base de datos, si no existían ya"""
    SQLModel.metadata.create_all(engine)

# Esquema de datos

class TaskBase(SQLModel):
    descripcion: str
    completada: bool = False

class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)

class TaskData(TaskBase):
    pass


# Capa de datos

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[Task]:
        """Obtiene todas las tareas"""
        return self.db.exec(select(Task)).all()

    def get_by_id(self, id: int) -> Task | None:
        """Obtiene una tarea por su ID"""
        return self.db.get(Task, id)

    def add(self, task_data: TaskData) -> Task:
        """Crea y guarda una nueva tarea"""
        tarea = Task.model_validate(task_data)
        self.db.add(tarea)
        self.db.commit()
        self.db.refresh(tarea)
        return tarea

    def update(self, id: int, task_data: TaskData) -> Task | None:
        """Actualiza una tarea existente"""
        db_task = self.db.get(Task, id)
        if db_task:
            db_task.descripcion = task_data.descripcion
            db_task.completada = task_data.completada
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        return None

    def delete(self, id: int) -> bool:
        """Elimina una tarea"""
        db_task = self.db.get(Task, id)
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            return True
        return False

# Inyección recursiva

def get_db():
    with Session(engine) as db:
        yield db

def get_repo(db: Session = Depends(get_db)) -> TaskRepository:
    return TaskRepository(db)

# Nos aseguramos de que la base de datos y las tablas se han creado
create_db_and_tables()

# Inicializacion y Rutas de la API

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

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