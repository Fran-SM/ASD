import scrapy
import re
from urllib.parse import urlencode

class FarmaciaGPSSpider(scrapy.Spider):
    name = "farmacias_gps"
    start_urls = [
        "http://www.farmasturias.org/GESCOF/cms/Guardias/FarmaciaBuscar.asp?IdMenu=111"
    ]

    custom_settings = {
        'HTTPCACHE_ENABLED': True,
        'FEED_EXPORT_ENCODING': 'utf-8',
        'DOWNLOAD_DELAY': 0.25,
        'CONCURRENT_REQUESTS': 1,
        'RETRY_TIMES': 2,  
        'DEFAULT_REQUEST_HEADERS': {
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
    }

    def parse(self, response):
        farmacias_nodos = response.xpath("//ul[@class='ListadoResultados']")

        for nodo in farmacias_nodos:
            item = {
                "nombre": nodo.xpath(".//span[@class='TituloResultado']/text()").get().strip(),
                "poblacion": nodo.xpath("preceding::h6[@class='LocalidadGuardias'][1]/text()").get().strip(),
                "horario": nodo.xpath("preceding::h5[@class='HorarioGuardias'][1]/a/text()").get().strip(),
                "latitud": "N/A",
                "longitud": "N/A"
            }

            js_call = nodo.xpath(".//a[@class='VerMapa']/@href").get()
            if js_call:
                p = re.findall(r"'(.*?)'", js_call)
                if len(p) >= 7:
                    query = {'Dir': p[0], 'Far': p[1], 'Dir2': p[2], 'CP': p[3], 'Loc': p[4], 'IdF': p[5], 'IdG': p[6]}
                    url_mapa = f"https://www.farmasturias.org/GESCOF/cms/Guardias/openstreetmap.asp?{urlencode(query)}"

                    
                    yield scrapy.Request(
                        url=url_mapa, 
                        callback=self.parse_map, 
                        errback=self.error_mapa,
                        cb_kwargs={'item': item}
                    )
            else:
                yield item

    def parse_map(self, response, item):

        lat = re.search(r"var latitudfarma\s*=\s*'(.*?)';", response.text)
        lon = re.search(r"var longitudfarma\s*=\s*'(.*?)';", response.text)
        if lat: item['latitud'] = lat.group(1)
        if lon: item['longitud'] = lon.group(1)
        yield item

    def error_mapa(self, failure):
        # Si el servidor da Error 500, recuperamos el item

        item = failure.request.cb_kwargs['item']
        self.logger.error(f"Fallo en mapa para {item['nombre']} (Error 500)")
        yield item