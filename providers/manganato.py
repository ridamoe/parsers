import jidouteki 
from jidouteki import *

class Manganato(ProviderConfig):
    @jidouteki.meta
    def _meta(self):
        return Metadata(
            key = "manganato",
            display_name = "Manganato"
        )

    @jidouteki.match
    def match(self, url):
        patterns = (
        r"https://natomanga\.com/manga-(?P<series>[a-z0-9]*)/chapter-(?P<chapter>.*?)(?:[/?#].*|)$",
        r"https://natomanga\.com/manga-(?P<series>[a-z0-9]*)",
        )
        
        return jidouteki.utils.match_groups(patterns, url)

    def fetch_series(self, series) -> FetchedData:
        return self.utils.fetch(
            f"https://natomanga.com/manga-{series}",
        )

    @jidouteki.series.chapters
    def series_chapters(self, series):
        for d in self.fetch_series(series):
            d = d.css(".row-content-chapter > li > a.chapter-name")
            
            chapters = []
            for el in d:
                params = self.utils.provider.match(el["href"])
                chapter = Chapter(
                    params=params,
                    chapter=params["chapter"],
                    volume=None,
                    title=None,
                    language="en"
                )
                chapters.append(chapter)
            if chapters: return chapters
            
        return []
        
    @jidouteki.series.title
    def series_title(self, series):
        for d in self.fetch_series(series):
            d = d.css(".story-info-right > h1")
            for el in d:
                text = el.get_text()
                if text: return text
        return None

    @jidouteki.series.cover
    def series_cover(self, series):
        for d in self.fetch_series(series):
            d = d.css(".story-info-left > .info-image > img")
            for el in d:
                if el["src"]: return el["src"]
        return None
    
    @jidouteki.images
    def images(self, series, chapter):
        d = self.utils.fetch(f"https://natomanga.com/manga-{series}/chapter-{chapter}")
        d = d.css(".container-chapter-reader > img")
        
        ret = []
        for el in d:
            url = el["src"]
            ret.append(self.utils.proxy(url, headers={"referer": "https://natomanga.com/"}))
        return ret