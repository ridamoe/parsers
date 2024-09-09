import jidouteki
from jidouteki import Config, Metadata, Chapter
from jidouteki.utils import get

@jidouteki.register
class Mangadex(Config):
    @jidouteki.meta
    def _metadata(self) -> Metadata: 
        return Metadata(
            base='https://api.mangadex.org/',
            key='mangadex',
            display_name='Mangadex'
        )

    @jidouteki.match
    def _match(self):
        return [
            r"https://mangadex.org/title/(?P<series>[0-9a-f\-]*)",
            r"https://mangadex.org/chapter/(?P<chapter>[0-9a-f\-]*)"
        ]
    
    def _fetch_series(self, series):
        return self.fetch(f"/manga/{series}/?includes[]=cover_art")
    
    @jidouteki.series.title
    def _series_title(self, series):
        d = self._fetch_series(series).json()
        return list(get(d, ("data.attributes.title")).values()).pop()

    @jidouteki.series.cover
    def _series_cover(self, series):
        d = self._fetch_series(series).json()
        relationships = get(d, "data.relationships")
        cover_art = next((rel for rel in relationships if rel["type"] == "cover_art"), None)
        if cover_art:
            file = get(cover_art, "attributes.fileName")
            return f"https://uploads.mangadex.org/covers/{series}/{file}"
        
    @jidouteki.series.chapters
    def _series_chapters(self, series):
        chapters = []
        
        data = self.fetch(f"/manga/{series}/feed").json()
        for chapter in data["data"]:
            if chapter["type"] != "chapter": continue
            chapter = Chapter(
                params = { "chapter": get(chapter, "id") },
                volume = str(get(chapter, "attributes.volume")),
                chapter = str(get(chapter, "attributes.chapter")),
                title = get(chapter, "attributes.title"),
                language = get(chapter, "attributes.translatedLanguage"),
            )
            chapters.append(chapter)
        
        return chapters
    
    @jidouteki.images
    def _images(self, chapter):
        d = self.fetch(f"/at-home/server/{chapter}?includes[]=scanlation_group").json()
                
        images = []
        base = f"{get(d, 'baseUrl')}/data/{get(d, 'chapter.hash')}"
        for chapter_data in get(d, "chapter.data"):
            images.append(f"{base}/{chapter_data}")
        return images