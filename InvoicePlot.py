from matplotlib import pyplot as plt
import datetime as dt
import numpy as np
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
    except:
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
        plt.show()
        plt.close()

try:
    html_file = open('invoice_plot.html', 'w')
except:
    print("File could not be opened, please check if file is writeable or appropriate permissions are set")
    sys.exit()

html_file.write('<html><head><title>Invoice Plot</title></head><body>')
for file in os.listdir("plots/"):
    if file.endswith(".png"):
        html_file.write('<img src="' + "plots/" + file + '" alt="' + file + '" width="75%">')
html_file.write('</body></html>')
html_file.close()