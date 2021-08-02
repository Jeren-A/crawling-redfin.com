
# commented block can be used if the we get error 403
# import urllib.request

# class AppURLopener(urllib.request.FancyURLopener):
#     version = "Mozilla/5.0"

# url = 'https://www.redfin.com/CA/Redwood-City/346-Hillview-Ave-94062/home/2002212'

# opener = AppURLopener()
# response = opener.open('url')


import requests

#url = 'https://www.redfin.com/'
#url = 'https://www.redfin.com/CA/Redwood-City/346-Hillview-Ave-94062/home/2002212'
url = 'https://www.sabanciuniv.edu/tr/2021-tercih-donemi-programi'

response = requests.get(url,  headers={'User-Agent': 'Mozilla/5.0'})

print(response.text)


# import requests
# # url = 'https://www.sabanciuniv.edu/tr/2021-tercih-donemi-programi'

# urll = 'http://api.scraperapi.com/?api_key=2d894527503d0745ec409664fde72c8a&url=https://www.sabanciuniv.edu/tr/2021-tercih-donemi-programi'
# r = requests.get(urll)
# print (r.status_code)

# import requests

# url = 'https://www.sabanciuniv.edu/tr/2021-tercih-donemi-programi'

# payload = {'api_key': '2d894527503d0745ec409664fde72c8a', 'url': url}
# r = requests.get('http://api.scraperapi.com', params=payload)
# print (r.status_code)

# from scraper_api import ScraperAPIClient
# client = ScraperAPIClient('2d894527503d0745ec409664fde72c8a')
# result = client.get(url = 'https://redfin.com/').text
# print(result)
from bs4 import BeautifulSoup
import requests


urls = []

def scrape(site):
    r = requests.get(site)
    
    s = BeautifulSoup(r.text, 'html.parser')
    for i in s.find_all('a'):
        href = i.attrs['href']
        if href.startwith('/'):
            site = site+href
            if site not in urls:
                urls.append(site)
                print(site)
                scrape(site)
    
if __name__ == "__main__":
    site = 'http://redfin.com//'
    scrape(site)

