from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from bs4 import BeautifulSoup
from matplotlib import pyplot as plt
import datetime as dt
import numpy as np
import configparser
import sqlite3
import requests
import io
import os
import re

#  Load Config
config = configparser.ConfigParser()
config.read('config.ini')

### HTML Conversion Stage ###

def convert2html(fname, pages=None):
    pagenums = set()     
    manager = PDFResourceManager()
    output = io.BytesIO()
    converter = HTMLConverter(manager, output, codec='utf-8', laparams=LAParams())
    interpreter = PDFPageInterpreter(manager, converter)  
    infile = open(fname, 'rb')
    ### As invoices could be multiple pages and its number is not static determining a for loop for each page
    for page in PDFPage.get_pages(infile, pagenums,caching=True, check_extractable=True):
        interpreter.process_page(page)
 
    HtmlConverted = output.getvalue()  
    infile.close(); converter.close(); output.close()
    return HtmlConverted

path = "C:\\Users\\Emin\\Desktop\\InvoiceParse"
#fileIn= "BE02019000688551"
fileIn= "53727368"
fileOut =path+"/"+fileIn+".html"
filePDF=path+"/"+fileIn+".pdf"

covertedHTML = convert2html(filePDF, pages=None)
fileConverted = open(fileOut, "wb")
fileConverted.write(covertedHTML)
fileConverted.close()

### Parsing Stage after HTML conversion ###

HTMLFile = open(fileOut, "r", encoding="utf-8")
source = HTMLFile.read()
soup = BeautifulSoup(source, "html.parser")
HTMLFile.close()

### Template Matching Before Patterns ###
flags = config.items( "Templates" )
for key, flag in flags:
    if(soup.find(text=re.compile(flag))):
        template = flag
        break

#  Load Section CSS Selectors
sum_selector = config[template]['sum_selector']
date_selector = config[template]['date_selector']
prices_selector_s1 = config[template]['prices_selector_s1']
prices_selector_s2 = config[template]['prices_selector_s2']
packages_selector_s1 = config[template]['packages_selector_s1']
packages_selector_s2 = config[template]['packages_selector_s2']

#  Load Indexes of CSS Selectors
prices_index = int(config[template]['prices_index'])
packages_index = int(config[template]['packages_index'])
loop_range_start = int(config[template]['loop_range_start'])
loop_range_end = int(config[template]['loop_range_end'])

#  Load Optional Parameters
mul_sum = config.getboolean(template,'mul_sum')
if mul_sum:
    sum_selector2 = config[template]['sum_selector2']

dateSelector = date_selector   # Selector for invoice date, static for now will be dynamic with after config implementation
if "br" in dateSelector:
    date = soup.select(dateSelector)[0].next_sibling # "next_sibling" is used for reading the value after <br> tag in case there is a br tag in our selector
else:
    date = soup.select(dateSelector)
    date = [r.text.strip() for r in date]
    #parse date as datetime object
    #date = dt.datetime.strptime(date[0], '%d.%m.%Y')
print("Fatura Tarihi", date)

i = packages_index   # CSS index loop counter for Packages
z = prices_index  # CSS index loop counter for Prices

# Create package and price lists
packages = []
prices = []

loop = range(loop_range_start, loop_range_end)   # Temp loop stop rule until determining empty rows     
for i in loop:
    packageSelector = packages_selector_s1
    packageSelector += str(i)
    packageSelector += packages_selector_s2
    package = soup.select(packageSelector)
    package = [r.text.strip() for r in package]

    i = i + 1   # Increment index of Packages CSS Selector to adress next row/package
    
    priceSelector = prices_selector_s1
    priceSelector += str(z)
    priceSelector += prices_selector_s2
    price = soup.select(priceSelector)
    price = [r.text.strip() for r in price]
    
    z = z + 1   # Increment index of Prices CSS Selector to adress next row/price
    
    print("Paket :", str(package), "Fiyatı :", price)

    #save package and price to a list
    packages.append(package)
    prices.append(price)
        
sumSelector = sum_selector  # Selector for price summary, static for now will be dynamic with after config implementation
if "br" in sumSelector:
    sumPrice = soup.select(sumSelector)[0].next_sibling # "next_sibling" is used for reading the value after <br> tag
    sumPrice = str(sumPrice)
    flags = config.items( "Currencies" )
    for key, flag in flags:
        matches = str(config[flag]["match"])
        matches = matches.split(',')
        for i in matches:
            if(re.search(re.compile(i), sumPrice)):
                currency = flag
                break
    sumPrice = sumPrice.replace(",", ".")
    sumPrice = float(re.search(r"[-+]?\d*\.\d+|\d+", sumPrice).group(0))
else:
    sumPrice = soup.select(sumSelector)
    sumPrice = [r.text.strip() for r in sumPrice]
    sumPrice = str(sumPrice)
    flags = config.items( "Currencies" )
    for key, flag in flags:
        matches = str(config[flag]["match"])
        matches = matches.split(',')
        for i in matches:
            if(re.search(re.compile(i), sumPrice)):
                currency = flag
                break
    sumPrice = sumPrice.replace(",", ".")
    sumPrice = float(re.search(r"[-+]?\d*\.\d+|\d+", sumPrice).group(0))
print("Toplam Ödenecek Tutar", sumPrice)
print("Para Birimi", currency)

if mul_sum:
    sumSelector2 = sum_selector2  # Selector for price summary, static for now will be dynamic with after config implementation
    if "br" in sumSelector2:
        sumPrice2 = soup.select(sumSelector2)[0].next_sibling # "next_sibling" is used for reading the value after <br> tag
        sumPrice2 = str(sumPrice2)
        flags = config.items( "Currencies" )
        for key, flag in flags:
            matches = str(config[flag]["match"])
            matches = matches.split(',')
            for i in matches:
                if(re.search(re.compile(i), sumPrice2)):
                    currency2 = flag
                    break
        sumPrice2 = sumPrice2.replace(",", ".")
        sumPrice2 = float(re.search(r"[-+]?\d*\.\d+|\d+", sumPrice2).group(0))
    else:
        sumPrice2 = soup.select(sumSelector2)
        sumPrice2 = [r.text.strip() for r in sumPrice2]
        sumPrice2 = str(sumPrice2)
        flags = config.items( "Currencies" )
        for key, flag in flags:
            matches = str(config[flag]["match"])
            matches = matches.split(',')
            for i in matches:
                if(re.search(re.compile(i), sumPrice2)):
                    currency2 = flag
                    break
        sumPrice2 = sumPrice2.replace(",", ".")
        sumPrice2 = float(re.search(r"[-+]?\d*\.\d+|\d+", sumPrice2).group(0))
    print("Toplam Ödenecek Tutar (Optional)", sumPrice2)
    print("Para Birimi (Optional)", currency2)
    
### Database Insertion Stage ###
conn = sqlite3.connect('invoices.db')
c = conn.cursor()
# Create summaries table within desired format if it doesnt exist
c.execute("""CREATE TABLE IF NOT EXISTS summaries(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    company TEXT,
    sum FLOAT,
    sum_currency TEXT,
    sum_mul FLOAT,
    sum_mul_currency TEXT
    )""")
conn.commit()
# Create products table within desired format if it doesnt exist
c.execute("""CREATE TABLE IF NOT EXISTS products(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    date TEXT,
    company TEXT,
    package TEXT,
    price TEXT,
    price_currency TEXT
    )""")
conn.commit()
# Insert date company and sum lists to summaries table
if mul_sum:
    c.execute("INSERT INTO summaries VALUES(NULL,?,?,?,?,?,?)", (str(date), template, sumPrice, currency, sumPrice2, currency2))
else:
    c.execute("INSERT INTO summaries VALUES(NULL,?,?,?,?,?,?)", (str(date), template, sumPrice, currency, 0, "None"))
conn.commit()

# Insert package and price lists to products table
if mul_sum:
    for i in range(len(packages)):
        c.execute("INSERT INTO products VALUES(NULL,?,?,?,?,?)", (str(date), template, str(packages[i]), str(prices[i]), "$"))
else:
    for i in range(len(packages)):
        c.execute("INSERT INTO products VALUES(NULL,?,?,?,?,?)", (str(date), template, str(packages[i]), str(prices[i]), "$"))
conn.commit()
conn.close()

### Currency Conversion Stage ###
# Load Currency Conversion Rates from api.exchangerate.host
date = "2020-04-04"
fromc = "USD"
toc = "TRY"
amount = 1
url = "https://api.exchangerate.host/" + str(date) + "?base=" + fromc + "&symbols="+ toc
response = requests.get(url)
data = response.json()
rate = str(data['rates'])
rate = float(rate.replace("{'TRY': ", "").replace("}", ""))
print("USD to TL price", rate*amount)