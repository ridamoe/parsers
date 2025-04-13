import jidouteki
from jidouteki import *

class GDrive(WebsiteParser):
    @property
    def meta(self):
        return Metadata(
            domains = [
                Domain('https://drive.google.com/')
            ],
            key = 'google-drive',
            display_name = 'Google drive'
        )
    
    @jidouteki.test(
        "https://drive.google.com/drive/folders/1VgP78U0tZtyfz9zVnXbghyFooAZ-UuxD?usp=drive_link", 
        {"folderId": "1VgP78U0tZtyfz9zVnXbghyFooAZ-UuxD"}
    )
    @jidouteki.map.match
    def match(self, url):
        patterns = (
            r"https://drive\.google\.com/drive/folders/(?P<folderId>.*?)(?:[/?].*|)$",
        )
        
        return jidouteki.utils.match_groups(patterns, url)
    
    @jidouteki.test({"folderId": "1VgP78U0tZtyfz9zVnXbghyFooAZ-UuxD"})
    @jidouteki.map.images
    def images(self, folderId):
        d = self.fetch(f"/drive/folders/{folderId}")
        d = d.css("c-wiz > div[data-id]")
        
        images = []
        for el in d:
            data_id = el["data-id"]
            images.append(f"https://lh3.googleusercontent.com/d/{data_id}")
        return images