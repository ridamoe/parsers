from jidouteki import *
import jidouteki

class Retsu(WebsiteParser):
    @property
    def meta(self):
        return Metadata(
            key = "retsuorg",
            display_name = "Retsu.org",
            domains = [
                Domain("https://retsu.org/"),
            ]
        )
    
    @jidouteki.test(
        "https://retsu.org/manga/ao-no-hako/ch-130/", 
        {"series": "ao-no-hako", "chapter": "130"}
    )
    @jidouteki.test(
        "https://retsu.org/manga/haruka-reset/chapter-71/", 
        {"series": "haruka-reset", "chapter": "71"}
    )
    @jidouteki.map.match
    def match(self, url):
        patterns = (
            r"https://retsu\.org/manga/(?P<series>.*?)/(?:ch|chapter)-(?P<chapter>.*?)(?:[/?].*|)$",
            r"https://retsu\.org/manga/(?P<series>.*?)(?:[/?].*|)$"
        )
        
        return jidouteki.utils.match_groups(patterns, url)

    def fetch_series(self, series):
        return self.fetch(f"/manga/{series}")
    
    @jidouteki.test({"series": "haruka-reset"})
    @jidouteki.map.series.cover
    def series_cover(self, series): 
        d = self.fetch_series(series)
        d = d.css(".summary_image img")
        for el in d:
            return el["data-src"]
    
    @jidouteki.test({"series": "haruka-reset"})
    @jidouteki.map.series.title
    @jidouteki.test({"series": "haruka-reset"})
    def series_title(self, series): 
        d = self.fetch_series(series)
        d = d.css("h1.post-title").pop()        
        return d.get_text()

    @jidouteki.test({"series": "haruka-reset"})
    @jidouteki.map.series.chapters
    def chapters(self, series):
        d = self.fetch_series(series)
        d = d.css(".wp-manga-chapter > a")
        chapters = []
        for el in d:
            chap_val = self.match(el["href"])["chapter"]
            chapter = Chapter(
            params = { "chapter": chap_val }, 
            chapter = chap_val,
            language = "en",
            )
            chapters.append(chapter)
        return chapters
    
    @jidouteki.test({"series": "haruka-reset", "chapter": "71"})
    @jidouteki.map.images
    def images(self, series, chapter):
        for d in self.fetch(f"/manga/{series}/", [f"ch-{chapter:0>3}",  f"chapter-{chapter}"]):
            d = d.css(".reading-content img")

            images = []
            for el in d:
                image = el["data-src"].replace("\t", '').replace("\n", '')
                images.append(image)
            if images: return images
        return None

# search:
#   fetcher:
#     params:
#           - query
#     type: request
#     urls: 
#       - /?s={query}&post_type=wp-manga

#   series:
#     selector:
#       type: css
#       query: .manga__item > .manga__content a
#       pipeline:
#         - props: 
#           - href
#         - regex: https://retsu\.org/manga/(.*?)/