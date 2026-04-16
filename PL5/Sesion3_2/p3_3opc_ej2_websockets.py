
import os
import bcrypt
from datetime import datetime, timedelta, timezone
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from fastapi import FastAPI, Depends, HTTPException, status, Response, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, ConfigDict
from sqlalchemy import create_engine, Column, Integer, String, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker, Session
from sqlmodel import SQLModel, Field, Relationship, create_engine, Session, select


DATABASE_URL = "sqlite:///./tareas.db"
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

SECRET_KEY = os.getenv("SECRET_KEY", "secreto_super_seguro")
ALGORITHM = "HS256"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Esquema de los datos

class User(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    username: str = Field(unique=True, index=True)
    hashed_password: str
    tasks: list["Task"] = Relationship(back_populates="owner")

class TaskBase(SQLModel):
    descripcion: str
    completada: bool = False

class Task(TaskBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    owner_id: int | None = Field(default=None, foreign_key="user.id")
    owner: User | None = Relationship(back_populates="tasks")

class TaskData(TaskBase):
    pass

class UserData(SQLModel):
    username: str
    password: str

class Token(SQLModel):
    access_token: str
    token_type: str

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)

# Funciones de seguridad

def get_password_hash(password: str):
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")

def verify_password(plain_password: str, hashed_password: str):
    return bcrypt.checkpw(plain_password.encode("utf-8"), hashed_password.encode("utf-8"))

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Inyección recursiva

def get_db():
    with Session(engine) as session:
        yield session

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception from None
        
    statement = select(User).where(User.username == username)
    user = db.exec(statement).first()
    if user is None:
        raise credentials_exception
    return user

# Capa de datos

class TaskRepository:
    def __init__(self, db: Session, user_id: int):
        self.db = db
        self.user_id = user_id

    def get_all(self) -> list[Task]:
        statement = select(Task).where(Task.owner_id == self.user_id)
        return list(self.db.exec(statement).all())

    def get_by_id(self, id: int) -> Task | None:
        # Busca por ID de tarea Y TAMBIÉN que el owner sea el usuario actual
        statement = select(Task).where(Task.id == id, Task.owner_id == self.user_id)
        return self.db.exec(statement).first()

    def add(self, task_data: TaskData) -> Task:
        tarea = Task.model_validate(task_data)
        # Asignamos la tarea al usuario actual antes de guardarla
        tarea.owner_id = self.user_id
        self.db.add(tarea)
        self.db.commit()
        self.db.refresh(tarea)
        return tarea

    def update(self, id: int, task_data: TaskData) -> Task | None:
        db_task = self.get_by_id(id)
        if db_task:
            db_task.descripcion = task_data.descripcion
            db_task.completada = task_data.completada
            self.db.add(db_task)
            self.db.commit()
            self.db.refresh(db_task)
            return db_task
        return None

    def delete(self, id: int) -> bool:
        db_task = self.get_by_id(id)
        if db_task:
            self.db.delete(db_task)
            self.db.commit()
            return True
        return False

def get_repo(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)) -> TaskRepository:
    assert current_user.id is not None
    return TaskRepository(db, current_user.id)

# Inicializacion

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

create_db_and_tables()

# Autenticación y gestión de usuarios

@app.post("/users", status_code=201)
def register_user(user_in: UserData, db: Session = Depends(get_db)):
    hashed_pwd = get_password_hash(user_in.password)
    db_user = User(username=user_in.username, hashed_password=hashed_pwd)
    try:
        db.add(db_user)
        db.commit()
    except Exception:
        db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists") from None
    return {"msg": "User created"}

@app.post("/token", response_model=Token)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> Token:
    statement = select(User).where(User.username == form_data.username)
    user = db.exec(statement).first()
    
    if not user or not verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(data={"sub": user.username}, expires_delta=access_token_expires)
    return Token(access_token=access_token, token_type="bearer")


# Rutas de tareas

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

# Clase para el chat

class ChatManager:
    def __init__(self):
        # Guardamos una lista de conexiones activas
        self.active_connections: list[WebSocket] = []

    async def accept(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: str):
        # Enviamos el mensaje a TODOS los conectados
        for connection in self.active_connections:
            await connection.send_text(message)

# Instanciamos el manager global
manager = ChatManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, token: str | None = None):
    # Verificar si hay token
    if token is None:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    
    # Obtener el token para sacar el nombre de usuario
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str | None = payload.get("sub")
        if username is None:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return

    # Si el token es válido, aceptamos la conexión
    await manager.accept(websocket)
    await manager.broadcast(f"{username} se ha unido al chat")
    
    try:

        while True:
            data = await websocket.receive_text()
            mensaje_formateado = f"{username}: {data}"
            await manager.broadcast(mensaje_formateado)
            
    except WebSocketDisconnect:

        manager.disconnect(websocket)
        await manager.broadcast(f"{username} ha abandonado el chat")