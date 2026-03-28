import json
from lxml import html
from pydantic import BaseModel

# Definición del modelo
class Farmacia(BaseModel):
    nombre: str
    direccion: str
    codigo_postal: int
    telefono: str
    poblacion: str
    horario: str
lista_farmacias = []

# Sacar los datos del XML y guardarlos en una variable 

f = open("pagina-farmacias.html", "rb")
arbol = html.parse(f)

#  Obtener los nodos <ul> de cada farmacia y sacar los datos pedidos

farmacias_nodos = arbol.xpath("//ul[@class='ListadoResultados']")
for nodo in farmacias_nodos:
    nombre = nodo.xpath(".//span[@class='TituloResultado']/text()")[0].strip()
    dir_completa = nodo.xpath(".//span[@class='ico-localizacion']/text()")[0]
    direccion = dir_completa.replace("Dirección:", "").strip()
    cp_str = direccion.split("-")[-1].strip()
    codigo_postal = int(cp_str)
    telefono = (nodo.xpath(".//span[@class='ico-telefono']/text()")[0]).replace("Teléfono:", "").strip()
    poblacion = nodo.xpath("preceding::h6[@class='LocalidadGuardias'][1]/text()")[0].strip()
    horario = nodo.xpath("preceding::h5[@class='HorarioGuardias'][1]/a/text()")[0].strip()

    # Crear el objeto de cada farmacia y guardarlo
    f_obj = Farmacia(
        nombre=nombre,
        direccion=direccion,
        codigo_postal=codigo_postal,
        telefono=telefono,
        poblacion=poblacion,
        horario=horario
    )
    lista_farmacias.append(f_obj)

# Exportar a JSON

lista_dicts = []
for farmacia in lista_farmacias:
    lista_dicts.append(farmacia.model_dump())

with open("farmacias.json", "w", encoding="utf-8") as f_out:
    json.dump(lista_dicts, f_out, indent=2, ensure_ascii=False)