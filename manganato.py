from jidouteki import Config, Metadata, Chapter, FetchedData
import jidouteki 

@jidouteki.register
class Manganato(Config):
    @jidouteki.meta
    def _meta(self):
        return Metadata(
        key = "manganato",
        display_name = "Manganato"
        )

    @jidouteki.match
    def _match(self, url):
        patterns = (
        r"https://chapmanganato\.to/manga-(?P<series>[a-z0-9]*)/chapter-(?P<chapter>.*?)(?:[/?#].*|)$",
        # - manganato.com chapter url?
        r"https://manganato\.com/manga-(?P<series>[a-z0-9]*)",
        r"https://chapmanganato\.to/manga-(?P<series>[a-z0-9]*)",
        )
        
        return jidouteki.utils.match_groups(patterns, url)

    def _fetch_series(self, series) -> FetchedData:
        return self.fetch([
            f"https://manganato.com/manga-{series}",
            f"https://chapmanganato.to/manga-{series}"
        ])

    @jidouteki.series.chapters
    def _series_chapters(self, series):
        for d in self._fetch_series(series):
            d = d.css(".row-content-chapter > li > a.chapter-name")
            
            chapters = []
            for el in d:
                params = self.match(el["href"])
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
    def _series_title(self, series):
        for d in self._fetch_series(series):
            d = d.css(".story-info-right > h1")
            for el in d:
                text = el.get_text()
                if text: return text
        return None

    @jidouteki.series.cover
    def _series_cover(self, series):
        for d in self._fetch_series(series):
            d = d.css(".story-info-left > .info-image > img")
            for el in d:
                if el["src"]: return el["src"]
        return None
    
    @jidouteki.images
    def _images(self, series, chapter):
        d = self.fetch(f"https://chapmanganato.to/manga-{series}/chapter-{chapter}")
        d = d.css(".container-chapter-reader > img")
        
        ret = []
        for el in d:
            url = el["src"]
            ret.append(self.proxy(url, headers={"referer": "https://chapmanganato.to/"}))
        return ret