import jidouteki
from jidouteki import ProviderConfig, Metadata, Chapter
from jidouteki.utils import get
import re
import urllib.parse

class Mangadex(ProviderConfig):
    @property
    def meta(self) -> Metadata: 
        return Metadata(
            base='https://api.mangadex.org/',
            key='mangadex',
            display_name='Mangadex'
        )

    @jidouteki.match
    def match(self, url):
        SERIES_MATCH = r"https://mangadex.org/title/(?P<series>[0-9a-f\-]*)"
        if (m := re.match(SERIES_MATCH, url)): return m.groupdict()

        CHAPTER_MATCH = r"https://mangadex.org/chapter/(?P<chapter>[0-9a-f\-]*)"
        if (m := re.match(CHAPTER_MATCH, url)):
            match = m.groupdict()
            
            d  = self.utils.fetch(f"/chapter/{match.get("chapter")}").json()
            relationships = get(d, "data.relationships")
            manga = next((rel for rel in relationships if rel["type"] == "manga"), {})
            
            return  {
                **match,
                "series": manga.get("id")
            }
    
    def fetch_series(self, series):
        return self.utils.fetch(f"/manga/{series}/?includes[]=cover_art")
    
    @jidouteki.series.title
    def series_title(self, series):
        d = self.fetch_series(series).json()
        return list(get(d, ("data.attributes.title")).values()).pop()

    @jidouteki.series.cover
    def series_cover(self, series):
        d = self.fetch_series(series).json()
        relationships = get(d, "data.relationships")
        cover_art = next((rel for rel in relationships if rel["type"] == "cover_art"), None)
        if cover_art:
            file = get(cover_art, "attributes.fileName")
            return f"https://uploads.mangadex.org/covers/{series}/{file}"
        
    @jidouteki.series.chapters
    def series_chapters(self, series):
        chapters = []
        
        for data in self.paginate(f"/manga/{series}/feed"):
            for chapter in data["data"]:
                if chapter["type"] != "chapter": continue
                chapter = Chapter(
                    params = { "chapter": get(chapter, "id") },
                    volume = get(chapter, "attributes.volume"),
                    chapter = get(chapter, "attributes.chapter"),
                    title = get(chapter, "attributes.title"),
                    language = get(chapter, "attributes.translatedLanguage"),
                )
                chapters.append(chapter)
        
        return chapters
    
    def paginate(self, url):
        # Some endpoints are paginated.
        # see: https://api.mangadex.org/docs/01-concepts/pagination/
        d = self.utils.fetch(url).json()
        yield d
        
        limit = d["limit"]
        total = d["total"]
        
        url_parts = urllib.parse.urlparse(url)
        query = urllib.parse.parse_qsl(url_parts.query)
        for current_offset in range(limit, total, limit):
            new_query = query
            new_query.append(("offset", current_offset))            
            enc_query = urllib.parse.urlencode(new_query, doseq=True) 
            new_url = url_parts._replace(query=enc_query).geturl()
            
            yield self.utils.fetch(new_url).json()
        
    @jidouteki.images
    def images(self, chapter):
        d = self.utils.fetch(f"/at-home/server/{chapter}?includes[]=scanlation_group").json()
                
        images = []
        base = f"{get(d, 'baseUrl')}/data/{get(d, 'chapter.hash')}"
        for chapter_data in get(d, "chapter.data"):
            url = f"{base}/{chapter_data}"
            
            # Hotlinking mostly works but it's forbidden by mangadex policies
            # see: https://api.mangadex.org/docs/2-limitations/#general-connection-requirements
            proxied = self.utils.proxy(url, headers={"referer": "https://mangadex.org/"})
            
            images.append(proxied)
        return images