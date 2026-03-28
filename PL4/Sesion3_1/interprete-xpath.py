# coding: utf-8
# Este fichero está inspirado en el tutorial
# http://www.w3schools.com/xpath/xpath_syntax.asp

# Carga un documento de ejemplo y permite al usuario introducir expresiones
# xpath, tras lo cual le muestra el resultado de evaluar esas expresiones

# El documento de ejemplos sobre el que se hacen las consultas:

documento = """\
<?xml version="1.0" encoding="ISO-8859-1"?>

<bookstore>

<book category="COOKING">
  <title lang="en">Everyday Italian</title>
  <author>Giada De Laurentiis</author>
  <year>2005</year>
  <price>30.00</price>
</book>

<book category="CHILDREN">
  <title lang="en">Harry Potter</title>
  <author>J K. Rowling</author>
  <year>2005</year>
  <price>29.99</price>
</book>

<book category="WEB">
  <title lang="en">XQuery Kick Start</title>
  <author>James McGovern</author>
  <author>Per Bothner</author>
  <author>Kurt Cagle</author>
  <author>James Linn</author>
  <author>Vaidyanathan Nagarajan</author>
  <year>2003</year>
  <price>49.99</price>
</book>

<book category="WEB">
  <title lang="en">Learning XML</title>
  <author>Erik T. Ray</author>
  <year>2003</year>
  <price>39.95</price>
</book>

</bookstore>
"""

# Función de utilidad, para mostrar los resultados de Xpath
def mostrar_resultado_xpath(elemento):
    """Esta función muestra un elemento y todos sus hijos"""
    if type(elemento) == list:
        if len(elemento) == 0:
            print("NO HAY RESULTADOS")
        else:
            print("Encontrados", len(elemento), "elementos")
        for i in range( len(elemento) ):
            print("Elemento", i, "-"*40)
            mostrar_resultado_xpath(elemento[i])  # Recursivamente
        return
    else:
        # Si no es una lista, es un nodo, que según la expresión
        # XPath usada podrá ser un booleano, string, float, 
        # o bien un Element 
        if etree.iselement(elemento):
            # Si es un Elemento, hacemos uso de una función de utilida
            # que muestra el "código fuente" de ese elemento (su XML)
            print(etree.tostring(elemento))
        elif isinstance(elemento, bytes):
            print(elemento.decode("utf-8"))
        else:
            # Si no, imprimimos directamente su valor, del tipo que sea
            print(elemento)


# Función que recibe como parámetro una cadena xpath y la aplica
# sobre el documento dado, tras lo cual muestra el resultado
def XpathEjemplo(expresion, arbol):
    """Esta función aplica una expresión xpath a un arbol ya parseado,
    y muestra por pantalla el resultado"""
    resultado = arbol.xpath(expresion)
    print(expresion, "="* (80 -len(expresion)))
    mostrar_resultado_xpath(resultado)

# Programa principal
from lxml import etree, html
import readline        # Para que haya "recuperación de comandos"
import sys

if len(sys.argv)<2:
    print("Uso: %s fichero.xml" % sys.argv[0])
    print("  Este programa carga el fichero.xml especificado como parámetro")
    print("  y permite aplicarle interactivamente expresiones XPath mostrando")
    print("  los resultados")
    sys.exit()

f=open(sys.argv[1])
if sys.argv[1].endswith("xml"):
    arbol = etree.parse(f)
elif sys.argv[1].endswith("html"):
    arbol = html.parse(f)
else:
    print(f"Error, el archivo '{sys.argv[1]}' no es XML ni HTML")
    quit()


# Bucle principal
while True:
    cadena = input("\nIntroduce una xpath para evaluar: ")
    if cadena == "":
        break;
    try:
        XpathEjemplo(cadena, arbol)
    except Exception as e:
        print("Ha ocurrido algún error. Probablemente la sintaxis ha sido incorrecta")
        print(e)



