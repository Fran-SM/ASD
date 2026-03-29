import scrapy
import re
from urllib.parse import urlencode

class FarmaciaGPSSpider(scrapy.Spider):
    name = "farmacias_gps"
    start_urls = [
        "http://www.farmasturias.org/GESCOF/cms/Guardias/FarmaciaBuscar.asp?IdMenu=111"
    ]

    custom_settings = {
        'HTTPCACHE_ENABLED': True,  # CRUCIAL: Para no saturar el servidor con peticiones de mapas
        'FEED_EXPORT_ENCODING': 'utf-8',
    }

    def parse(self, response):
        """Este método es llamado con la respuesta HTML de cada URL en start_urls"""

        farmacias_nodos = response.xpath("//ul[@class='ListadoResultados']")
        for nodo in farmacias_nodos:
            
            # Datos básicos
            item = {
                "nombre": nodo.xpath(".//span[@class='TituloResultado']/text()").get().strip(),
                "poblacion": nodo.xpath("preceding::h6[@class='LocalidadGuardias'][1]/text()").get().strip(),
                "horario": nodo.xpath("preceding::h5[@class='HorarioGuardias'][1]/a/text()").get().strip(),
            }

            # Extraer la llamada JavaScript
            js_call = nodo.xpath(".//a[@class='VerMapa']/@href").get()
            
            if js_call:
                # Extraer parámetros
                params_raw = re.findall(r"VerMapa\((.*)\)", js_call)[0]
                p = [s.strip("'") for s in params_raw.split(',')]

                query = {
                    'Dir': p[0], 'Far': p[1], 'Dir2': p[2], 
                    'CP': p[3], 'Loc': p[4], 'IdF': p[5], 'IdG': p[6]
                }
                url_mapa = "https://www.farmasturias.org/GESCOF/cms/Guardias/openstreetmap.asp?" + urlencode(query)

                # Petición
                yield scrapy.Request(url=url_mapa, callback=self.parse_map, cb_kwargs={'item': item})

    def parse_map(self, response, item):
        """Segunda función: extrae el GPS del código fuente del mapa"""
        
        lat = re.search(r"var latitudfarma='(.*?)';", response.text)
        lon = re.search(r"var longitudfarma='(.*?)';", response.text)

        item['latitud'] = lat.group(1) if lat else "N/A"
        item['longitud'] = lon.group(1) if lon else "N/A"

        # Item completo, lo retornamos
        yield item