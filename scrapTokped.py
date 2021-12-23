import time
import re
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from bs4 import BeautifulSoup
import pandas as pd

driver = webdriver.Chrome(executable_path="chromedriver.exe")

pageLoadWait = 1
numberOfProduct = 100

def getListProductPage(pageNum):
    driver.get("https://www.tokopedia.com/p/handphone-tablet/handphone?page=" + str(pageNum))
    driver.find_element_by_tag_name('html').send_keys(Keys.END)

    time.sleep(pageLoadWait)
    content = driver.page_source
    return BeautifulSoup(content, "lxml")

def getLink(card):
    link = card["href"]
    if (link.startswith("https://ta.tokopedia.com")):
        link = link[link.index("www.tokopedia.com"):link.index("%3Fsrc")]
        link = "https://" + link.replace('%2F', '/')
    return link

def getShopName(card):
    wrapper = list(list(card.find("div", {"data-testid": "divProductWrapper"}))[1])[2]
    if len(list(list(wrapper)[0])) > 1:
        return list(list(wrapper)[0])[1].getText()
    else:
        return list(list(wrapper)[1])[1].getText()

def getName(body):
    return body.find("h1", {"data-testid": "lblPDPDetailProductName"}).getText()

def getDesc(body):
    result = ""
    for string in body.find("div", {"data-testid": "lblPDPDescriptionProduk"}).strings:
        result += string + "\n"
    return result

def getImg(body):
    imgContainer = body.find("div", {"data-testid": "PDPImageMain"})
    return list(list(list(imgContainer)[0])[1])[0]["src"]

def getRating(body):
    return float(body.find("span", {"data-testid": "lblPDPDetailProductRatingNumber"}).getText())

def getPrice(body):
    textPrice = body.find("div", {"data-testid": "lblPDPDetailProductPrice"}).getText()
    return int(re.sub('[^0-9]','', textPrice))

data = {}
i = 1
while (len(data.keys())<numberOfProduct):
    for card in getListProductPage(i).findAll("a", {"data-testid": "lnkProductContainer"}):
        data[getLink(card)] = getShopName(card)
        if len(data.keys())==numberOfProduct:
            break
    i+=1

columns = ["name","desc","imgUrl","price","rating","storeName"]
products = []
for link in data:
    driver.get(link)
    time.sleep(pageLoadWait)
    content = driver.page_source
    soup = BeautifulSoup(content, "lxml")
    products.append([getName(soup), getDesc(soup), getImg(soup), getPrice(soup), getRating(soup), data[link]])

df = pd.DataFrame(products, columns=columns)
df.to_csv(r'scrapResult.csv', sep = ';')