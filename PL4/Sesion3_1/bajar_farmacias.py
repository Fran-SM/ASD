import urllib.request

u = urllib.request.urlopen("http://www.farmasturias.org/GESCOF/cms/Guardias/" +
                 "FarmaciaBuscar.asp?IdMenu=111")
contenido = u.read()
u.close()
f = open("pagina-farmacias.html", "wb")
f.write(contenido)
f.close()