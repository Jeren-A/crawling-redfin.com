#import libraries
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from urllib.parse import urlparse
import threading
import queue
from bs4 import BeautifulSoup
from sitemap import SiteMapManager

class Menu:
    def __init__(self, name, items=None):
        self.name = name
        self.items = items or []

    def add_item(self, item):
        self.items.append(item)
        if item.parent != self:
            item.parent = self

    def remove_item(self, item):
        self.items.remove(item)
        if item.parent == self:
            item.parent = None

    def draw(self):
        print(self.name)
        for item in self.items:
            item.draw()

class Item:
    def __init__(self, name, function, parent=None):
        self.name = name
        self.function = function
        self.parent = parent
        if parent:
            parent.add_item(self) # use add_item instead of append, since who
                                  # knows what kind of complex code you'll have
                                  # in add_item() later on.

    def draw(self):
        # might be more complex later, better use a method.
        print("    " + self.name)
class Crawler(threading.Thread):
    def __init__(self, base_url, links_to_crawl, visited_links, inaccessible_links, url_lock):
        threading.Thread.__init__(self)
        print(f"Web Crawler worker {threading.current_thread()} has Started")
        self.domain = urlparse(base_url).netloc
        self.base_url = base_url # main url to crawl
        self.links_to_crawl = links_to_crawl # this is a Queue.queue which will be populated with links that are yet to be crawled.
        self.visited_links = visited_links # visited urls
        self.inaccessible_links = inaccessible_links # urls throwing errors
        self.url_lock = url_lock # to keep our threads safe

    def download_url(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }
        return requests.get(url, headers=headers).text

    def get_linked_urls(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            if path is None or path.startswith('#') or self.domain != urlparse(path).netloc:
                continue
            siteMapManager.add_url_connection(url, path)
            #TODO: add this path as (url, path) to Gokberk's sitemap manager's outgoing urls map
            yield path

    def add_asset_links(self, url, html):
        soup = BeautifulSoup(html, 'html.parser')
        testVariable = soup.find_all(['img', 'script', 'link'])
        for link in testVariable:
            srcExists = link.get('src')
            hrefExists = link.get('href')
            if srcExists is not None:
                assetLink = srcExists
            elif hrefExists is not None:
                assetLink = hrefExists
            else:
                continue
            #print('Asset link = ', assetLink)
            siteMapManager.add_asset_connection(url, assetLink)

    def add_url_to_visit(self, url):
        if url not in self.visited_links and url not in self.inaccessible_links:
            self.links_to_crawl.put(url)

    def crawl(self, url):
        html = self.download_url(url)
        self.add_asset_links(url, html)

        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    def run(self):
        while self.links_to_crawl:
            self.url_lock.acquire()
            url = self.links_to_crawl.get()
            self.url_lock.release()
            if url is None or len(self.visited_links) > 10:
                break
            self.url_lock.acquire()
            print('Crawling: ', url)
            self.url_lock.release()
            try:
                self.crawl(url)
            except Exception as e:
                #TODO: Add this url to dead links here using Gokberk's sitemap manager dead links list
                siteMapManager.add_dead_link(url)
                print('Failed to crawl: ', e)
                self.inaccessible_links.add(url)
            finally:
                self.links_to_crawl.task_done()
                self.visited_links.add(url)

siteMapManager = SiteMapManager()
answerMap = {}

def crawlWebpage():
    url = input("Please enter a URL to crawl: ")
    
    number_of_threads = input("Please Enter number of Threads: ")
    while number_of_threads.isdigit() == False:
        print("Number of Threads should be an integer ")
        number_of_threads = input("Please Enter number of Threads: ")


    getElements(url)

    links_to_crawl = queue.Queue()
    url_lock = threading.Lock()
    links_to_crawl.put(url)

    visited_links = set()
    crawler_threads = []
    inaccessible_links = set()

    for i in range(int(number_of_threads)):
        crawler = Crawler(base_url=url,
                        links_to_crawl=links_to_crawl,
                        visited_links=visited_links,
                        inaccessible_links=inaccessible_links,
                        url_lock=url_lock)

        crawler.start()
        crawler_threads.append(crawler)

    for crawler in crawler_threads:
        crawler.join()

    print(f"Total Number of pages visited are {len(visited_links)}")
    print(f"Total Number of Errornous links: {len(inaccessible_links)}")


def getElements(url):
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }

    r = requests.get(url, headers=headers)
    s = BeautifulSoup(r.content, "html.parser")
    address = s.find('h1', class_='homeAddress-variant').get_text()
    answerMap['address'] = address

    info_div = s.find('div', class_= 'home-main-stats-variant')
    
    price = info_div.find('div', class_= 'stat-block price-section').get_text()
    beds = info_div.find('div', class_= 'stat-block beds-section').get_text()
    baths = info_div.find('div', class_= 'stat-block baths-section').get_text()
    size = info_div.find('div', class_= 'stat-block sqft-section').get_text()
    answerMap['price'] = price
    answerMap['beds'] = beds
    answerMap['baths'] = baths
    answerMap['size'] = size  

    agentInfo = s.find('div', class_='agent-info-item').get_text()
    owner = agentInfo.find('div', class_='agent-basic-details font-color-gray-dark').get_text()
    phone = agentInfo.find('p', class_='phone-numbers').get_text()
    email = agentInfo.find('a', class_='phone-number-entry').get_text()
    
    answerMap['agentName'] = owner
    answerMap['agentPhone'] = phone
    answerMap['agentEmail'] = email
    

def drawSitemap():
    siteMapManager.print_sitemap()
    return

deadLinks = []
def outputDeadLinks():
    # We can have a list of dead links for the whole crawling process
    for deadLink in deadLinks:
        print(deadLink)

# to answer questions
# 1 - scrape only first webpage and retrieve certain information from that page whose location on page is previously known
    # we can retrieve those elements by locating them on browser devtools and calling their paths on code
# 2 - put these certain information to a map where key is preknown information keyword, and value is scraped information
# Example = {["beds":3], ["price":1540000]}

def answerWHQuestion():
    WHQuestion = input("Please enter a WH question: ").lower()
    #i suggest to have menu for this as well, like: 1. What is the contact info of the owner or 2. Where is the estate located? 
    # Who is the ownere of the house? ....
    
    #if WHQuestion
    # If where is included -> return address taken from user
    # If what or which or how is included -> for all(?) words in the question return value of keyword in map if exists
    # if old/year/age is included, return age of house or its built year

def answerYesNoQuestion():
    yesNoQuestion = input("Please enter a yes/no question: ")
    # TODO find yes no questions that we can answer, they also need to be taken from kind of a map which should be filled while scraping first url 

def exitProgram():
    return

main = Menu("mainMenu")

# Add items to menu which is named as 'main'
crawlItem = Item("1. Crawl given webpage", crawlWebpage, main)
sitemapItem = Item("2. Print sitemap with static assets and URLs", drawSitemap, main)
deadLinksItem = Item("3. Print inaccessible/dead links", outputDeadLinks, main)
whQuestionItem = Item("4. Ask a WH question", answerWHQuestion, main)
yesNoQuestionItem = Item("5. Ask a yes/no question", answerYesNoQuestion, main)
exitItem = Item("6. Exit program", exitProgram, main)

def isInputValid(userInput):
    while userInput.isdigit() == False or int(userInput)<0 or int(userInput)>6:
        print("Wrong choice")
        userInput = input("Please enter your choice: ")
    return userInput
    
    
main.draw()
userInput = input("Please enter your choice: ") #check whether user inputs integer or not
userInput = int(isInputValid(userInput))


while(userInput != 6 ): # 6 can be defined at top 
    if(userInput == 1):
        crawlItem.function()
    elif(userInput == 2):
        sitemapItem.function()
    elif(userInput == 3):
        deadLinksItem.function()
    elif(userInput == 4):
        whQuestionItem.function()
    elif(userInput == 5):
        yesNoQuestionItem.function()
    else:
        break

    main.draw()
    userInput = input("Please enter your choice: ") #check whether user inputs integer or not
    userInput = isInputValid(userInput)


