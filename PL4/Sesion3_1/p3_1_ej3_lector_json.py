import json
from pydantic import BaseModel

# Definición del modelo
class Farmacia(BaseModel):
    nombre: str
    direccion: str
    codigo_postal: int
    telefono: str
    poblacion: str
    horario: str

# Leer el fichero JSON
with open("farmacias.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

# Validación
lista_objetos = []
for farmacia_dict in datos:
    farmacia = Farmacia.model_validate(farmacia_dict)
    lista_objetos.append(farmacia)

# Preguntar poblacion
poblacion_buscada = input("Introduce una población: ").upper()

# Buscar farmacias en esa población
encontradas = []
for f in lista_objetos:
    if f.poblacion.upper() == poblacion_buscada:
        encontradas.append(f)

# Imprimir resultados
if encontradas:
    print(f"Farmacias en {poblacion_buscada}:")
    for f in encontradas:
        print(f"- {f.nombre} ({f.telefono}): {f.horario}")
else:
    print("No se han encontrado farmacias.")