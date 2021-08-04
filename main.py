#import libraries
from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from urllib.parse import urlparse
import threading
import queue
from bs4 import BeautifulSoup
from sitemap import SiteMapManager
import yake


yesNoText = ""      # global variable to be used for searching the answer of yes/no questions in it

class Menu:   #menu as a class that adds, removes and displays the options also called as items 
    def __init__(self, name, items=None):
        self.name = name     #one option of the menu
        self.items = items or []  #array of combined options

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
        self.name = name   # menu content (ex: 1.crawl a webpage 2.print sitemap ...)
        self.function = function
        self.parent = parent
        if parent:
            parent.add_item(self)

    def draw(self):
        print("    " + self.name)

class Crawler(threading.Thread):    # crawls all internal links by implementing multithreading

    def __init__(self, base_url, links_to_crawl, visited_links, inaccessible_links, url_lock): #constructor
        threading.Thread.__init__(self)

        print(f"Web Crawler worker {threading.current_thread()} has Started")

        self.domain = urlparse(base_url).netloc
        self.base_url = base_url     # main url to crawl
        self.links_to_crawl = links_to_crawl # this is a Queue.queue which will be populated with links that are yet to be crawled
        self.visited_links = visited_links # visited urls
        self.inaccessible_links = inaccessible_links # dead links
        self.url_lock = url_lock  # to keep our threads safe

    def download_url(self, url): # read a url 
        headers = {
            'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
        }
        return requests.get(url, headers=headers).text

    # extract outgoing urls from given link which are in the same domain
    def get_linked_urls(self, url, html): 
        soup = BeautifulSoup(html, 'html.parser')
        for link in soup.find_all('a'):
            path = link.get('href')
            if path and path.startswith('/'):
                path = urljoin(url, path)
            if path is None or path.startswith('#') or self.domain != urlparse(path).netloc:
                continue
            siteMapManager.add_url_connection(url, path) 
            yield path

    # extract static assets (img, link, script) from given webpage and store their url addresses
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
            siteMapManager.add_asset_connection(url, assetLink)

    # add a new url to queue to visit
    def add_url_to_visit(self, url):
        if url not in self.visited_links and url not in self.inaccessible_links:
            self.links_to_crawl.put(url)

    # call add asset links and add outgoing urls to queue functions for given url
    def crawl(self, url):
        html = self.download_url(url)
        self.add_asset_links(url, html)

        for url in self.get_linked_urls(url, html):
            self.add_url_to_visit(url)

    # get url from queue thread safe, crawl that webpage, add it to visited urls
    def run(self):
        while self.links_to_crawl:
            self.url_lock.acquire()
            url = self.links_to_crawl.get()
            self.url_lock.release()
            if url is None or len(self.visited_links) > 500:
                break
            self.url_lock.acquire()
            print('Crawling: ', url)
            self.url_lock.release()
            try:
                self.crawl(url)
            except Exception as e:
                siteMapManager.add_dead_link(url)
                print('Failed to crawl: ', e)
                self.inaccessible_links.add(url)
            finally:
                self.links_to_crawl.task_done()
                self.visited_links.add(url)

# define global site map manager and question answerer classes
siteMapManager = SiteMapManager()
answerMap = {}
yesNoMap = {}


def crawlWebpage(): #funtion where Crawler class is called
    url = input("Please enter a URL to crawl: ")
    
    number_of_threads = input("Please Enter number of Threads: ")
    while number_of_threads.isdigit() == False:
        print("Number of Threads should be an integer ")
        number_of_threads = input("Please Enter number of Threads: ")


    getElements(url)

    links_to_crawl = queue.Queue()  #stores links to be crawled
    url_lock = threading.Lock()  # will be used to prevent threads from simultaneously accessing a shared data
    links_to_crawl.put(url)  

    visited_links = set()   
    crawler_threads = []
    inaccessible_links = set()

    for i in range(int(number_of_threads)): #running the crawler with threads
        crawler = Crawler(base_url=url,
                        links_to_crawl=links_to_crawl,
                        visited_links=visited_links,
                        inaccessible_links=inaccessible_links,
                        url_lock=url_lock)

        crawler.start()
        crawler_threads.append(crawler)

    for crawler in crawler_threads: #ending all threads
        crawler.join()

    print(f"Total Number of pages visited are {len(visited_links)}")
    print(f"Total Number of Errornous links: {len(inaccessible_links)}")


#assigns key-words to -answerMap- (used to answer WH questions)
def key_allocation(arr, val):
    for i in arr:
        answerMap[i] = val.get_text() 

def getElements(url):    #getting possible elements from the provided page (ex: price, contact info, and etc)
   
    #getting data from url
    headers = {
        'User-Agent': 'Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)'
    }

    r = requests.get(url, headers=headers)
    s = BeautifulSoup(r.content, "html.parser")
    
    #extracting address
    
    address = s.find('h1', class_='homeAddress-variant')
    address_array = ['address', 'location', 'where', 'place', 'site']
    if address is not None:
        key_allocation(address_array, address)

    #extracting price, beds, baths and size info
    info_div = s.find('div', class_= 'home-main-stats-variant')
    if info_div is not None:
        price = info_div.find('div', class_= 'stat-block price-section')
        beds = info_div.find('div', class_= 'stat-block beds-section')
        baths = info_div.find('div', class_= 'stat-block baths-section')
        size = info_div.find('div', class_= 'stat-block sqft-section')

        price_array = ['price', 'cost', 'fee', 'payment', 'amount', 'worth', 'how much']
        if price is not None:
            for i in price_array:
                answerMap[i] = price.get_text()[:-5] 
            
        if beds is not None:
            answerMap['bed'] = beds.get_text()[:-4]+" beds"
            answerMap['bath']=baths.get_text()[:-5]+" baths"

        size_array = ['size', 'dimension', 'width', 'capacity']
        if size is not None:
            for i in size_array:
                answerMap[i] = size.get_text()[:-5] + " Sq Ft"
  

    #extracting info about owner
    agentInfo = s.find('div', class_='agent-info-item')
    if agentInfo is not None:
        owner = agentInfo.find('div', class_='agent-basic-details font-color-gray-dark')
        owner_clean = owner.select("span a")[0]
        
        #extracting contact info
        phoneElement = agentInfo.find('p', class_='phone-numbers')
        if phoneElement is not None:
            answerMap['phone'] = phoneElement.get_text()
            answerMap['number'] = phoneElement.get_text()
        
        
        emailElement = agentInfo.find('a', class_='phone-number-entry')
        if emailElement is not None:
            answerMap['email'] = emailElement.get_text()
            
        if phoneElement is not None and emailElement is not None:
            answerMap['contact'] = "phone number "+phoneElement.get_text() + "  " + "email is "+emailElement.get_text()
        
        owner_array=['owner', 'agent', 'who']
        key_allocation(owner_array, owner_clean)
        

    #text used to search for keywords to aswer yes/no questions
    global yesNoText
    yesNoContent = s.find('div', class_= 'amenities-container')
    if yesNoContent is not None:
        yesNoText = yesNoContent.get_text().lower()
    #print(yesNoText)

def drawSitemap():
    siteMapManager.print_sitemap()
    return

def outputDeadLinks():
    siteMapManager.print_dead_links()
    return


def answerWHQuestion():
    WHQuestion = input("Please enter a WH question: ").lower()
    isAnswered = False
    for keyword in answerMap:
        if keyword in WHQuestion:
            isAnswered = True
            print('Your answer: ', answerMap[keyword])
            break
    if not isAnswered:
        print('Sorry, I do not know the answer for that question. ')

def answerYesNoQuestion():

    yesNoQuestion = input("Please enter a yes/no question: ")
     
    if len(yesNoText) < 1:
        print('I could not answer it.')
        return

    # define configuration variables for yake library's custom keyword extractor 
    language = "en"
    max_ngram_size = 3
    deduplication_threshold = 0.9
    numOfKeywords = 5

    # create the custom keyword extractor
    custom_kw_extractor = yake.KeywordExtractor(lan=language, n=max_ngram_size, dedupLim=deduplication_threshold, top=numOfKeywords, features=None)
    
    # extract keywords from yes/no question
    keywords = custom_kw_extractor.extract_keywords(yesNoQuestion)
    
    # answer yes if extracted keywords exist in yes/no text 
    isNo = True
    for kw in keywords:
        if kw[0] in yesNoText: 
            print('YES')
            isNo = False
            break
    if isNo:
        print('NO')

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
    while userInput.isdigit() == False or int(userInput)<1 or int(userInput)>6:
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
    userInput = int(isInputValid(userInput))


