import jidouteki
from jidouteki import *

@jidouteki.register
class GDrive(Config):
    @jidouteki.meta
    def _meta(self):
        return Metadata(
            base = 'https://drive.google.com/',
            key = 'google-drive',
            display_name = 'Google drive'
        )

    @jidouteki.match
    def _match(self):
        return (
            r"https://drive\.google\.com/drive/folders/(?P<folderId>.*?)(?:[/?].*|)$",
        )
  
    @jidouteki.images
    def _images(self, folderId):
        d = self.fetch(f"/drive/folders/{folderId}")
        d = d.css("c-wiz > div[data-id]")
        
        images = []
        for el in d:
            data_id = el["data-id"]
            images.append(f"https://lh3.googleusercontent.com/d/{data_id}")
        return images