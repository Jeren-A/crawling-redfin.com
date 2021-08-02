import requests

url = 'https://www.redfin.com/'

response = requests.get(url)

print(response)