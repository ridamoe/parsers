import jidouteki
from jidouteki import *

class GDrive(ProviderConfig):
    @jidouteki.meta
    def meta(self):
        return Metadata(
            base = 'https://drive.google.com/',
            key = 'google-drive',
            display_name = 'Google drive'
        )

    @jidouteki.match
    def match(self, url):
        patterns = (
            r"https://drive\.google\.com/drive/folders/(?P<folderId>.*?)(?:[/?].*|)$",
        )
        
        return jidouteki.utils.match_groups(patterns, url)
  
    @jidouteki.images
    def images(self, folderId):
        d = self.utils.fetch(f"/drive/folders/{folderId}")
        d = d.css("c-wiz > div[data-id]")
        
        images = []
        for el in d:
            data_id = el["data-id"]
            images.append(f"https://lh3.googleusercontent.com/d/{data_id}")
        return images