import scrapy

class FarmaciaSpider(scrapy.Spider):
    name = "farmacias"
    
    start_urls = [
        "http://www.farmasturias.org/GESCOF/cms/Guardias/FarmaciaBuscar.asp?IdMenu=111"
    ]

    custom_settings = {
        'HTTPCACHE_ENABLED': True,
        'FEED_EXPORT_ENCODING': 'utf-8', # Asegura que los acentos se guarden bien
    }

    def parse(self, response):
        
        """Este método es llamado con la respuesta HTML de cada URL en start_urls"""
        farmacias_nodos = response.xpath("//ul[@class='ListadoResultados']")

        #  Obtener los nodos <ul> de cada farmacia y sacar los datos pedidos
        for nodo in farmacias_nodos:
            nombre = nodo.xpath(".//span[@class='TituloResultado']/text()").get().strip()
            dir_raw = nodo.xpath(".//span[@class='ico-localizacion']/text()").get()
            direccion = dir_raw.replace("Dirección:", "").strip()
            cp_str = direccion.split("-")[-1].strip()
            codigo_postal = int(cp_str)
            tel_raw = nodo.xpath(".//span[@class='ico-telefono']/text()").get()
            telefono = tel_raw.replace("Teléfono:", "").strip()
            poblacion = nodo.xpath("preceding::h6[@class='LocalidadGuardias'][1]/text()").get().strip()
            horario = nodo.xpath("preceding::h5[@class='HorarioGuardias'][1]/a/text()").get().strip()

            # Retornar diccionario
            yield {
                "nombre": nombre,
                "direccion": direccion,
                "codigo_postal": codigo_postal,
                "telefono": telefono,
                "poblacion": poblacion,
                "horario": horario
            }