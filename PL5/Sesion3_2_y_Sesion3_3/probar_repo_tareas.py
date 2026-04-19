from p3_2_ej1_api_fase1 import TaskData, TaskRepository

# Instancia global del repositorio (simulando una conexión a DB)
repo = TaskRepository()

# 1. Crear algunas tareas de ejemplo
t1 = repo.add(TaskData(descripcion="Comprar leche", completada=False))
t2 = repo.add(TaskData(descripcion="Estudiar para el examen", completada=False))
t3 = repo.add(TaskData(descripcion="Pasear al perro", completada=True))

# 2. Probar a obtener la lista completa
print("--- Todas las tareas ---")
todas = repo.get_all()
for t in todas:
    print(f"ID: {t.id}, Desc: {t.descripcion}, Comp: {t.completada}")

# 3. Probar a obtener una tarea concreta, la primera que se creó
print(f"\n--- Tarea {t1.id} ---")
tarea_1 = repo.get_by_id(t1.id)
if tarea_1:
    print(f"Encontrada: {tarea_1.descripcion}")

# Probar a obtener una tarea que no existe
print("\n--- Tarea 999 (no existe) ---")
tarea_999 = repo.get_by_id(999)
if tarea_999 is None:
    print("No encontrada (como se esperaba)")

# 4. Probar a actualizar una tarea
print(f"\n--- Actualizar tarea {t1.id} ---")
tarea_actualizada = repo.update(
    t1.id, TaskData(descripcion="Comprar leche y pan", completada=True)
)
if tarea_actualizada:
    print(
        f"Actualizada: {tarea_actualizada.descripcion}, {tarea_actualizada.completada}"
    )

# 5. Probar a borrar una tarea
print(f"\n--- Borrar tarea {t2.id} ---")
borrada = repo.delete(t2.id)
print(f"¿Se borró?: {borrada}")

# 6. Probar a obtener la lista completa de tareas para ver que se ha borrado la segunda
print("\n--- Todas las tareas después de borrar ---")
for t in repo.get_all():
    print(f"ID: {t.id}, Desc: {t.descripcion}, Comp: {t.completada}")