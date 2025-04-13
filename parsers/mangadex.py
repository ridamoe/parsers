import jidouteki
from jidouteki import *
from jidouteki.utils import get
import re
import urllib.parse

class Mangadex(WebsiteParser):
    @property
    def meta(self) -> Metadata: 
        return Metadata(
            domains=[
                Domain('https://mangadex.org', 'https://api.mangadex.org/')
            ],
            key='mangadex',
            display_name='Mangadex'
        )

    @jidouteki.test(
        "https://mangadex.org/chapter/ff15cb79-b233-4721-9cf7-bb045a8e1e39", 
        {"series": "85b3504c-62e8-49e7-9a81-fb64a3f51def", "chapter": "ff15cb79-b233-4721-9cf7-bb045a8e1e39"})
    @jidouteki.test(
        "https://mangadex.org/title/6bf844c8-2ce4-401a-a761-3151042efe30/tokidoki-bosotto-roshia-go-de-dereru-tonari-no-alya-san", {"series": "6bf844c8-2ce4-401a-a761-3151042efe30"})
    @jidouteki.map.match
    def match(self, url):
        SERIES_MATCH = r"https://mangadex.org/title/(?P<series>[0-9a-f\-]*)"
        if (m := re.match(SERIES_MATCH, url)): return m.groupdict()

        CHAPTER_MATCH = r"https://mangadex.org/chapter/(?P<chapter>[0-9a-f\-]*)"
        if (m := re.match(CHAPTER_MATCH, url)):
            match = m.groupdict()
            
            d  = self.fetch(f"/chapter/{match.get("chapter")}").json()
            relationships = get(d, "data.relationships")
            manga = next((rel for rel in relationships if rel["type"] == "manga"), {})
            
            return  {
                **match,
                "series": manga.get("id")
            }
    
    def fetch_series(self, series):
        return self.fetch(f"/manga/{series}/?includes[]=cover_art")
    
    @jidouteki.test(
            {"series": "e1b08943-1195-4eab-85a4-a7bfc0766eed"}
    )
    @jidouteki.map.series.title
    def series_title(self, series):
        d = self.fetch_series(series).json()
        return list(get(d, ("data.attributes.title")).values()).pop()

    @jidouteki.test(
            {"series": "e1b08943-1195-4eab-85a4-a7bfc0766eed"}
    )
    @jidouteki.map.series.cover
    def series_cover(self, series):
        d = self.fetch_series(series).json()
        relationships = get(d, "data.relationships")
        cover_art = next((rel for rel in relationships if rel["type"] == "cover_art"), None)
        if cover_art:
            file = get(cover_art, "attributes.fileName")
            return f"https://uploads.mangadex.org/covers/{series}/{file}"
        
    @jidouteki.test(
        {"series": "e1b08943-1195-4eab-85a4-a7bfc0766eed"}
    )
    @jidouteki.test(
        {"series": "85b3504c-62e8-49e7-9a81-fb64a3f51def"} # paginated
    ) 
    @jidouteki.map.series.chapters
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
        d = self.fetch(url).json()
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
            
            yield self.fetch(new_url).json()
        
    @jidouteki.test({"chapter": "578eb707-acf3-4fcd-a383-054d116cdf00"})
    @jidouteki.map.images
    def images(self, chapter):
        d = self.fetch(f"/at-home/server/{chapter}?includes[]=scanlation_group").json()
                
        images = []
        base = f"{get(d, 'baseUrl')}/data/{get(d, 'chapter.hash')}"
        for chapter_data in get(d, "chapter.data"):
            url = f"{base}/{chapter_data}"
            
            # Hotlinking mostly works but it's forbidden by mangadex policies
            # see: https://api.mangadex.org/docs/2-limitations/#general-connection-requirements
            proxied = self.proxy(url, headers={"referer": "https://mangadex.org/"})
            
            images.append(proxied)
        return images