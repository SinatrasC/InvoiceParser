from matplotlib import pyplot as plt
import configparser
import sqlite3
import re
import os
import sys

#  Load Config
config = configparser.ConfigParser()
config.read('config.ini')

flags = config.items( "Templates" )
for key, flag in flags:
    #for each flag read sum price and date from db and plot it
    #try to connect db catch error if db not exist
    try:
        conn = sqlite3.connect('invoices.db')
    except Exception:
        print("DB could not be opened or created, please check if file is writeable or appropriate permissions are set")
        sys.exit(1)

    c = conn.cursor()
    c.execute("SELECT sum, date FROM summaries WHERE company = ?", (flag,))
    rows = c.fetchall()
    #if rows are not empty plot them
    if rows:
        #create list of dates and prices
        dates = []
        prices = []
        for row in rows:
            dates.append(re.search(r"(\d\d\d\d)(.)(\d\d)(.)(\d\d)", row[1]).group(0))
            prices.append(row[0])
        conn.close()
        #plot the data
        plt.rcParams['figure.figsize'] = (16,6)
        plt.plot(dates, prices)
        plt.title(flag + ' Price Summary History')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.tight_layout(pad=5)
        plt.savefig('plots/invoice_plot_' + flag + '.png', format = "png", dpi = 300, bbox_inches = "tight", pad_inches=0.5)
        plt.close()

try:
    html_file = open('invoice_plot.html', 'w')
except Exception:
    print("HTML file could not be opened, please check if file is writeable or appropriate permissions are set")
    sys.exit()

html_file.write('<html><head><title>Invoice Plot</title></head><body>')
#add a heading to html file
html_file.write('<h1>Invoice Plot</h1>')
html_file.write('<h3>This is a plot of the invoice price history</h3>')
#make h3 fontsize 80 and h1 fontsize 170
html_file.write('<style>h3 {font-size: 65px;} h1 {font-size: 170px;}</style>')

#add a paragraph to html file

#add a image to html file
for file in os.listdir("plots/"):
    if file.endswith(".png"):
        html_file.write('<img src="' + "plots/" + file + '" alt="' + file + '" width="75%">')
html_file.write('</body></html>')
html_file.close()