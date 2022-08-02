from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import HTMLConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from OCRHandler import OCR
from bs4 import BeautifulSoup
import datetime as dt
import configparser
import sqlite3
import requests
import io
import sys
import re


#  Load Config
config = configparser.ConfigParser()
config.read('config.ini')

### HTML Conversion Stage ###

def convert2html(fname, pages=None):
    pagenums = set()     
    manager = PDFResourceManager()
    output = io.BytesIO()
    if (altLAParams):
        LAP = LAParams(line_margin=0.2,word_margin=0.1, char_margin=0.5, line_overlap=0.4, boxes_flow=0.5, all_texts=True)
    else : 
        LAP = LAParams()
    converter = HTMLConverter(manager, output, codec='utf-8', laparams=LAP)
    interpreter = PDFPageInterpreter(manager, converter)  
    infile = open(fname, 'rb')
    ### As invoices could be multiple pages and its number is not static determining a for loop for each page
    for page in PDFPage.get_pages(infile, pagenums, password=pdfPassword, caching=True, check_extractable=True):
        interpreter.process_page(page)

    HtmlConverted = output.getvalue()  
    infile.close(); converter.close(); output.close()
    return HtmlConverted

def parse_date(date):
    if (re.search(r"(\d\d)(.)(\d\d)(.)(\d\d\d\d)", str(date))):
        regex = re.search(r"(\d\d)(.)(\d\d)(.)(\d\d\d\d)", str(date))
        dateFormatted = regex.group(1) + " " + regex.group(3) + " " + regex.group(5)
        dateFormatted = dt.datetime.strptime(dateFormatted, '%d %m %Y')
    elif (re.search(r"(\d\d.)(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)(.\d\d\d\d)", str(date))):
        regex = re.search(r"(\d\d.)(Ocak|Şubat|Mart|Nisan|Mayıs|Haziran|Temmuz|Ağustos|Eylül|Ekim|Kasım|Aralık)(.\d\d\d\d)", str(date))
        dateFormatted = regex.group(0)
        dateFormatted = dt.datetime.strptime(dateFormatted, '%d %B %Y')
    elif (re.search(r"(\d\d.)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(.\d\d\d\d)", str(date))):
        regex = re.search(r"(\d\d.)(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)(.\d\d\d\d)", str(date))
        dateFormatted = regex.group(0)
        dateFormatted = dt.datetime.strptime(dateFormatted, '%d %b %Y')
    elif (re.search(r"(\d\d\d\d)(.)(\d\d)(.)(\d\d)", str(date))):
        regex = re.search(r"(\d\d\d\d)(.)(\d\d)(.)(\d\d)", str(date))
        dateFormatted = regex.group(5) + " " + regex.group(3) + " " + regex.group(1)
        dateFormatted = dt.datetime.strptime(dateFormatted, '%d %m %Y')
    elif (re.search(r"(\d\d.)(January|February|March|April|May|June|July|August|September|October|November|December)(.\d\d\d\d)", str(date))):
        regex = re.search(r"(\d\d)(January|February|March|April|May|June|July|August|September|October|November|December)(.\d\d\d\d)", str(date))
        dateFormatted = regex.group(0)
        dateFormatted = dt.datetime.strptime(dateFormatted, '%d %B %Y')
    else:
        print ("Error : Date format is not recognized")
        exit()
    return dateFormatted

def parse_price(price):
    if (re.search(r"(\.)(.*,)", price)):
        price = price.replace(".", "")
    price = price.replace(",", ".")
    price = float(re.search(r"[-+]?\d*\.\d+|\d+", price).group(0))
    return price

def find_currency(price):
    flags = config.items( "Currencies" )
    for key, flag in flags:
        matches = str(config[flag]["match"])
        matches = matches.split(',')
        for i in matches:
            if(re.search(re.compile(i), price)):
                currency = flag
                break
    return currency

def clean_list(element):
    element = element.replace("['", "")
    element = element.replace("']", "")
    element = element.replace("[\"", "")
    element = element.replace("\"]", "")
    element = element.replace("\\n", " ")
    return element

path = "C:\\Users\\Emin\\Desktop\\InvoiceParse"
#fileIn= "e-Fatura"
fileIn = "image_01"
#fileIn= "ShowXML"
#fileIn= "e-FaturaGFW"
#fileIn= "ShowXMLtt"
#fileIn= "e-Fatura622"
#fileIn= "BE02019000688551"
#fileIn= "53727368"
fileOut =path+"/"+fileIn+".html"
filePDF=path+"/"+fileIn+".pdf"

#  Load General Settings
keepConvertedHtml = config.getboolean('GeneralSettings','keepConvertedHtml')
autoCurrencyConversion = config.getboolean('GeneralSettings','autoCurrencyConversion')
pdfPasswordSupport = config.getboolean('GeneralSettings','pdfPasswordSupport')
globalOCRSupport = config.getboolean('GeneralSettings','globalOCRSupport')
altLAParams = config.getboolean('GeneralSettings','alternativeLAParams')

if (globalOCRSupport):
    tesseractPath = config['GeneralSettings']['tesseractPath']
    tesseractPath = tesseractPath.replace("\"", "")
else:
    tesseractPath = ""

if(pdfPasswordSupport):
    pdfPassword = config.get('GeneralSettings','pdfPassword')
else:
    pdfPassword = ""

covertedHTML = convert2html(filePDF, pages=None)

# Decide to use temp file or keep file in path
if(keepConvertedHtml == True):
    fileConverted = open(fileOut, "wb")
    fileConverted.write(covertedHTML)
    fileConverted.close()

### Parsing Stage after HTML conversion ###

soup = BeautifulSoup(covertedHTML, "html.parser")

### Template Matching Before Patterns ###
flags = config.items( "Templates" )
for key, flag in flags:
    if(soup.find(text=re.compile(flag))):
        template = flag
        break
    else:
        template = None

if template == None:
    instance = OCR()
    instance.set_path(tesseractPath)
    img = instance.pdf2img(filePDF)
    ocResult = instance.get_text(img, "eng")
    print(ocResult)
    for key, flag in flags:
        if(re.search(re.compile(flag), ocResult)):
            template = flag
            break
        else:
            print("Error : Template is not recognized on both HTML and OCR")
            exit(1)

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
    dateFormatted = parse_date(date)
else:
    date = soup.select(dateSelector)
    date = [r.text.strip() for r in date]
    dateFormatted = parse_date(date)

print("Fatura Tarihi", dateFormatted)

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

    price = parse_price(str(price))
    packages.append(package)
    prices.append(price)
        
sumSelector = sum_selector  # Selector for price summary, static for now will be dynamic with after config implementation
if "br" in sumSelector:
    sumPrice = soup.select(sumSelector)[0].next_sibling # "next_sibling" is used for reading the value after <br> tag
    currency = find_currency(str(sumPrice))
    sumPrice = parse_price(str(sumPrice))
else:
    sumPrice = soup.select(sumSelector)
    sumPrice = [r.text.strip() for r in sumPrice]
    currency = find_currency(str(sumPrice))
    sumPrice = parse_price(str(sumPrice))

print("Toplam Ödenecek Tutar", sumPrice)
print("Para Birimi", currency)

if mul_sum:
    sumSelector2 = sum_selector2  # Selector for price summary, static for now will be dynamic with after config implementation
    if "br" in sumSelector2:
        sumPrice2 = soup.select(sumSelector2)[0].next_sibling # "next_sibling" is used for reading the value after <br> tag
        currency2 = find_currency(str(sumPrice2))
        sumPrice2 = parse_price(str(sumPrice2))
    else:
        sumPrice2 = soup.select(sumSelector2)
        sumPrice2 = [r.text.strip() for r in sumPrice2]
        currency2 = find_currency(str(sumPrice2))
        sumPrice2 = parse_price(str(sumPrice2))

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
    price FLOAT,
    price_currency TEXT
    )""")
conn.commit()
# Insert date company and sum lists to summaries table
if mul_sum:
    c.execute("INSERT INTO summaries VALUES(NULL,?,?,?,?,?,?)", (str(dateFormatted), template, sumPrice, currency, sumPrice2, currency2))
else:
    if(autoCurrencyConversion):
        ### Currency Conversion Stage ###
        # Load Currency Conversion Rates from api.exchangerate.host
        date = re.search(r"(\d\d\d\d)(.)(\d\d)(.)(\d\d)", str(dateFormatted)).group(0)
        if (currency == "TRY"):
            fromc = "TRY"
            toc = "USD"
        elif (currency == "USD"):
            fromc = "USD"
            toc = "TRY"
        amount = sumPrice
        url = "https://api.exchangerate.host/" + str(date) + "?base=" + fromc + "&symbols="+ toc + "&amount=" + str(amount) + "&places=3"
        try:
            response = requests.get(url)
            data = response.json()
        except:
            print("Currency Conversion Failed (API Error)")
            sys.exit()
    
        rate = str(data['rates'])

        if (currency == "TRY"):
            rate = float(rate.replace("{'USD': ", "").replace("}", ""))
            currency2 = "USD"
            sumPrice2 = rate
        elif (currency == "USD"):
            rate = float(rate.replace("{'TRY': ", "").replace("}", ""))
            currency2 = "TRY"
            sumPrice2 = rate
        else:
            print("Currency Conversion Failed (Currency Error)")
            sys.exit()

        c.execute("INSERT INTO summaries VALUES(NULL,?,?,?,?,?,?)", (str(dateFormatted), template, sumPrice, currency, sumPrice2, currency2))
    else: 
        c.execute("INSERT INTO summaries VALUES(NULL,?,?,?,?,NULL,?)", (str(dateFormatted), template, sumPrice, currency, "None"))
conn.commit()

# Insert package and price lists to products table
if mul_sum:
    for i in range(len(packages)):
        cleanPackages = clean_list(str(packages[i]))
        c.execute("INSERT INTO products VALUES(NULL,?,?,?,?,?)", (str(dateFormatted), template, cleanPackages, float(prices[i]), currency))
else:
    for i in range(len(packages)):
        print(prices)
        cleanPackages = clean_list(str(packages[i]))    
        c.execute("INSERT INTO products VALUES(NULL,?,?,?,?,?)", (str(dateFormatted), template, cleanPackages, float(prices[i]), currency))
conn.commit()
conn.close()