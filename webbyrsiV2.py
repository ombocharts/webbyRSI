import datetime as dt
import pandas as pd
from pandas_datareader import data as pdr
import yfinance as yf
from matplotlib import style
import matplotlib.dates as mdates
import numpy as np
import mplfinance as mpf

##############################################################

#I marked up this document to explain some of the code. If you have any questions on how it works...
#let me know, thanks! 

#Tyler/@ombocharts

##############################################################


yf.pdr_override()

emasUsed = [8,21]
smasUsed = [50,200]
usedVolumeMA = [50]

ogStart = dt.datetime(2020,1,1) #ogstart means original start
start =  ogStart - dt.timedelta(days=2 * max(smasUsed)) #check resetDate for explaination on the 2 *
now = dt.datetime.now()
stock = input("Enter your stock: ")


def setMovingAverages():
	global emasUsed, smasUsed, df
	for x in emasUsed:
		ema = x
		df["EMA_"+str(ema)] = df['Adj Close'].ewm(span = ema).mean()
	for x in smasUsed:
		sma = x
		df["SMA_"+str(sma)] = df['Adj Close'].rolling(window = sma).mean()
	for x in usedVolumeMA:
		volMA = x
		df["VOL_"+str(volMA)] = df['Volume'].rolling(window = volMA).mean()



def webbyRSI():
	#calculates the distance from the 21 ema, and calculates the percent from it
	global df, percentFrom21
	percentFrom21 =[]
	for row in df.index:
	 	appendMe = ((df['Adj Close'][row] - df['EMA_21'][row])/df["Adj Close"][row] * 100)
	 	if appendMe < 0:
	 		appendMe = 0
	 	percentFrom21.append(appendMe)			
	df["PERCENT_FROM_21"] = percentFrom21
	#df["WRSI_SMA_10"] = df["PERCENT_FROM_21"].rolling(window = 10).mean()#line is no longer needed --> mav = 10 does this for me



def resetDate():
	#I created this because I had issues with the moving averages - not very important

	#Explaination:
	#the dates are in trading days, so when resetting the date, adding 200 days actuallys puts the date forward...
	#further than intended b/c its setting it forward 200 trading days, not 200 calendar days

	#Fix:
	#I doulbed the distance back it goes to ensure that theres enough data for the longest moving average...
	#and had a list to count how many trading days to remove (I used the length as the index: in iloc) until it hit the starting day...
	#the reason its within a range of around 6 days is because the date entered isn't necessarily on a trading day
	global df, ogStart
	removeList = []	
	for i in df.index:
		removeList.append(df["Date"][i])
		og = mdates.date2num(ogStart)
		passedDate = df["Date"][i]
		if int(passedDate >= int(og) - 3 and int(passedDate) <= int(og + 3)):
			df = df.iloc[int(len(removeList)):]
			break


def figures():
	global df
	line6 = []
	line4 = []
	line2 = []
	for i in df.index:
		#this creates a horizontal line as long as the data frame 
		line6.append(6) 
		line4.append(4)
		line2.append(2)

	additions = [ 
			#Webby RSI
	         mpf.make_addplot((df['PERCENT_FROM_21']),panel=2,color='b',type='bar', width=0.75, mav=(10))
             ,mpf.make_addplot(line6 ,panel=2,color='r'),
             mpf.make_addplot(line4,panel=2,color='y'),
             mpf.make_addplot(line2,panel=2,color='g'),

             #Moving Averages
             #have to hard code this in here - not sure how to do a for loop through this new system

             #panel 0 - price
             #panel 1 - volume
             #panel 2 - webbyRSI     
             mpf.make_addplot((df['EMA_21']),panel=0,color='m'),   
             mpf.make_addplot((df['EMA_8']),panel=0,color='b'), 
             mpf.make_addplot((df['SMA_50']),panel=0,color='r'), 
             mpf.make_addplot((df['SMA_200']),panel=0,color='k'),
             mpf.make_addplot((df['VOL_50']),panel=1,color='r') 

	       ] 

	#volume = True creates another panel (panel 1) of volume with correctly colored bars
	mpf.plot(df, type = "candle", addplot=additions,panel_ratios=(1,.25),figratio=(1,.25),figscale=1.5, style = 'yahoo', volume = True, title = str(stock) + " Daily")



while stock != "quit":
	df = pdr.get_data_yahoo(stock, start, now)
	df["Date"] = mdates.date2num(df.index)
	setMovingAverages()
	webbyRSI()
	resetDate()
	figures()


	stock = input("Enter your stock: ")

	##############

	#Thanks for reading!

	##############



