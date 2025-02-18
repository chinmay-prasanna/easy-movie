import requests
from bs4 import BeautifulSoup
import asyncio
from torrentp import TorrentDownloader


class MovieDownloader():
    def __init__(self):
        self.base_url = "https://en.yts-official.mx"
        self.quality = "all"
        self.genre = "all"
        self.rating = "0"
        self.year = "0"
        self.order_by = "latest"
    
    def get_torrents(self, name: str):
        url = f"{self.base_url}/browse-movies?keyword={name}&quality={self.quality}&genre={self.genre}&rating={self.rating}&year={self.year}&order_by={self.order_by}"
        r = requests.get(url)

        soup = BeautifulSoup(r.text, 'html.parser')
        target_class = "browse-movie-wrap"
        divs = soup.select(f"div.{target_class}")

        res = {}
        if len(divs) > 0:
            for div in divs:
                title = div.find('a', class_="browse-movie-title")
                link = div.find('a', class_="browse-movie-link")

                res.update({
                    title.text: link.get("href")
                })

        return res
    
    def get_download_options(self, link):
        torrent_url = self.base_url + link
        r = requests.get(torrent_url)
        soup = BeautifulSoup(r.text, 'html.parser')
        target_id = "movie-info"
        div = soup.select(f"div#{target_id}")[0]

        download_links_div = div.find('p', class_="hidden-xs hidden-sm")
        download_links = download_links_div.find_all('a')

        res = {link.text: link.get("href") for link in download_links}

        return res
    
    def download_torrent(self, link):
        torrent_url = self.base_url + link
        filename = link.split("/")[-1]
        download = requests.get(url=f"{torrent_url}", stream=True)

        with open(filename, 'wb') as f:
            for chunk in download.iter_content(chunk_size=1024):
                if chunk:
                    f.write(chunk)

        torrent = TorrentDownloader(f"{filename}", ".")

        asyncio.run(torrent.start_download())