from fastapi import FastAPI, Depends, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session



DATABASE_URL = "sqlite:///./tareas.db"

engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()



class TaskDB(Base):
    __tablename__ = "tasks"
    id = Column(Integer, primary_key=True, index=True)
    descripcion = Column(String, index=True)
    completada = Column(Boolean, default=False)

# Crea el fichero .db y las tablas si no existen
Base.metadata.create_all(bind=engine)

# 3. Esquema de datos

class TaskData(BaseModel):
    descripcion: str
    completada: bool = False

class Task(TaskData):
    id: int
    # Permite a Pydantic leer atributos de objetos SQLAlchemy (TaskDB)
    model_config = ConfigDict(from_attributes=True)

# Capa de datos

class TaskRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_all(self) -> list[TaskDB]:
        """Retorna la lista con todas las tareas desde la DB"""
        return self.db.query(TaskDB).all()

    def get_by_id(self, id: int) -> TaskDB | None:
        """Busca y retorna una tarea por su id. Si no existe, retorna None"""
        return self.db.query(TaskDB).filter(TaskDB.id == id).first()

    def add(self, task_data: TaskData) -> TaskDB:
        """Crea una nueva tarea en la DB"""
        nueva_tarea = TaskDB(**task_data.model_dump())
        self.db.add(nueva_tarea)
        self.db.commit()
        self.db.refresh(nueva_tarea)
        return nueva_tarea

    def update(self, id: int, task_data: TaskData) -> TaskDB | None:
        """Actualiza los datos de una tarea en la DB"""
        tarea_existente = self.get_by_id(id)
        if tarea_existente:
            # Actualizamos campo por campo
            for key, value in task_data.model_dump().items():
                setattr(tarea_existente, key, value)
            self.db.commit()
            self.db.refresh(tarea_existente)
            return tarea_existente
        return None

    def delete(self, id: int) -> bool:
        """Elimina una tarea de la DB"""
        tarea_existente = self.get_by_id(id)
        if tarea_existente:
            self.db.delete(tarea_existente)
            self.db.commit()
            return True
        return False


# Inyección recursiva


def get_db():
    """Generador de sesiones de base de datos"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def get_repo(db: Session = Depends(get_db)) -> TaskRepository:
    """Inyecta la sesión en el repositorio y lo retorna"""
    return TaskRepository(db)

# Inicializacion y Rutas de la API

app = FastAPI()

# Añadimos soporte para CORS (para poder probar la API con el frontend)
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