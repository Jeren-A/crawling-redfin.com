from bs4 import BeautifulSoup
import requests

class Menu:
    def __init__(self, name, items=None):
        self.name = name
        self.items = items or []
        # self. = label or []

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
            # print("drawing an item")
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


    # urls = []
    
    # url = input("Please enter a URL to crawl: ")
    
    # headers = {
    #     'User-Agent': 'Mozilla/5.0'
    # }
    
    # req = requests.get(url, headers=headers)
    # reqContent = BeautifulSoup(req.content, "html.parser").encode("utf-8")
    # reqContent = req.content
    # bedCount = reqContent.select_one("#content > div.aboveBelowTheRail > div.alongTheRail > div:nth-child(6) > div > div > div > div > div.address-map-section > div.top-stats > div > div.stat-block.beds-section > div")

    # print('Bed count = ', bedCount.getText())

def crawlWebpage():
    
    urls = []
    
    url = input("Please enter a URL to crawl: ")

    headers = {
        'User-Agent': 'Mozilla/5.0'
    }

    # TODO We also need to ask the user to give us address of the house if this is a link for a house

    r = requests.get(url, headers=headers)
    s = BeautifulSoup(r.content, "html.parser").encode("utf-8")
    # s = BeautifulSoup(r.text())
    print(s)

    t = s.find('div', {'class':'statsValue'})
    

 

''''
url = input("Please enter a URL to crawl: ")

headers = requests.utils.default_headers()

headers.update(
    {
        'User-Agent': 'Mozilla/5.0',
    }
)

response = requests.get(url, headers=headers)
print(response)

'''

#####################################################crawler######################
    # <div class="statsValue">2</div>
    # TODO: open bottom commented out parts 
    # for i in s.find_all('a'):
    #     href = i.attrs['href']
    #     if href.startwith('/'):
    #         url  = url+href
    #         if url not in urls:
    #             urls.append(url)
    #             print(url)
    #             crawlWebpage(url)
    
    # if __name__ == "__main__":
    #     site = 'http://redfin.com//'
    #     scrape(site)
    

def drawSitemap():
    # Sitemapmanager.print_sitemap
    # Call function that gokberk implemented 
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
    WHQuestion = input("Please enter a WH question: ")
    # TODO We need a map to store keywords and its answers, it should be filled when scraping the first url
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
userInput = isInputValid(userInput)

# TODO validate function

while(userInput != '6'): # 6 can be defined at top 
    userInput = int(userInput)
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
        exitItem.function()


