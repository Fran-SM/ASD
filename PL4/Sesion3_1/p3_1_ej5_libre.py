import scrapy
from pydantic import BaseModel

# Definición del modelo
class Noticia(BaseModel):
    titular: str
    seccion: str
    enlace: str

class RtveSpider(scrapy.Spider):
    name = "rtve"
    start_urls = ["https://www.rtve.es/noticias/"]

    custom_settings = {
        'USER_AGENT': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)',
        'FEED_EXPORT_ENCODING': 'utf-8',
        'HTTPCACHE_ENABLED': True
    }

    def parse(self, response):
        """ Cada noticia está en un tag <article> con clase 'cell'"""

        articulos = response.xpath("//article[contains(@class, 'cell')]")

        for art in articulos:
            # Titular -> 'maintitle'
            titular = art.xpath(".//span[@class='maintitle']/text()").get()
            
            # Enlace -> <a> que envuelve al título
            enlace_rel = art.xpath(".//h3/a/@href").get()
            
            seccion = art.xpath("preceding::h2[contains(@class, 'secBox')][1]/a/span/text()").get()
            if not seccion:
                seccion = art.xpath("preceding::strong[contains(@class, 'secBox')][1]/a/span/text()").get()

            if titular and enlace_rel:
                enlace_abs = response.urljoin(enlace_rel)

                # Validar
                noticia_validada = Noticia(
                    titular=titular.strip(),
                    seccion=seccion.strip() if seccion else "General",
                    enlace=enlace_abs
                )

                yield noticia_validada.model_dump()
