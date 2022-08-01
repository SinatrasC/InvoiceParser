from matplotlib import pyplot as plt
import datetime as dt
import numpy as np
import configparser
import sqlite3
import re

#  Load Config
config = configparser.ConfigParser()
config.read('config.ini')

flags = config.items( "Templates" )
for key, flag in flags:
    #for each flag read sum price and date from db and plot it
    conn = sqlite3.connect('invoices.db')
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
        plt.savefig('invoice_plot_' + flag + '.png', format = "png", dpi = 300, bbox_inches = "tight", pad_inches=0.5)
        plt.show()
        plt.close()