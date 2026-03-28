from lxml import etree

# Sacar los datos del XML y guardarlos en una variable 
f = open("datos.xml", "rb")
arbol = etree.parse(f)

# Número total de libros de categoría WEB

libros_web = arbol.xpath("//book[@category='WEB']")
print(f"1. Número total de libros de categoría WEB: {len(libros_web)}")

# Título y el precio de todos los libros con más de un autor

libros_varios_autores = arbol.xpath("//book[author[2]]")
print(f"2. Libros con más de un autor:")
for libro in libros_varios_autores:
    titulo = libro.xpath("title/text()")[0]
    precio = libro.xpath("price/text()")[0]
    print(f"   - Título: {titulo} | Precio: {precio}")

# Precio total de todos los libros)

precio_total = arbol.xpath("sum(//book/price)")
print(f"3. Precio total de todos los libros: {precio_total}")
f.close()