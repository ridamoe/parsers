from jidouteki import Metadata, Config, Chapter
import jidouteki

@jidouteki.register
class Rawkuma(Config):
    
  @jidouteki.meta
  def _meta(self):
    return Metadata(
      key = "rawkuma",
      display_name = "Rawkuma",
      base = "https://rawkuma.com/"
    )
  
  @jidouteki.match
  def _match(self, url):
    patterns =  (
      r"https://rawkuma\.com/(?P<series>.*?)-chapter-(?P<chapter>.*?)(?:[/?].*|)$",
      r"https://rawkuma\.com/manga/(?P<series>.*?)(?:[/?].*|)$"
    )
    
    return jidouteki.utils.match_groups(patterns, url)

  def _fetch_series(self, series):
    return self.fetch(f"/manga/{series}")
   
  @jidouteki.series.chapters
  def _chapters(self, series):
      d = self._fetch_series(series)
      
      ret = []
      for el in d.css("#chapterlist li"):
        chapter = Chapter(
          params = { "chapter": el["data-num"]},
          chapter =  el["data-num"]
        )
        ret.append(chapter)
      return list(reversed(ret))
  
  
  @jidouteki.series.cover
  def _cover(self, series):
      d = self._fetch_series(series).css(".thumbook .thumb img")
      for el in d:
        return el["src"]


  @jidouteki.series.title
  def _title(self, series):
      d = self._fetch_series(series)
      d = d.css(".ts-breadcrumb.bixbox > div > span:last-child > a > span[itemprop=name]")
      for el in d: 
        return el.get_text("text")
      return None
  
  @jidouteki.images
  def _images(self, series, chapter):
      d = self.fetch(f"/{series}-chapter-{chapter}")
      d = d.css("#readerarea img")
      return [el["src"] for el in d] 
      
  # search:
  #   fetcher:
  #     params:
  #       - query
  #     type: request
  #     urls: 
  #       - /?s={query}
  #   series:
  #     selector:
  #       type: css
  #       query: .bs > .bsx a
  #       pipeline:
  #         - props: 
  #           - href
  #         - regex: https://rawkuma\.com/manga/(.*?)/