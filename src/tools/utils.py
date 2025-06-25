#Importing dependencies
import yfinance as yf
import numpy as np
import math

# data_scrape function to obtain values from yfinance
# Necessary values are precomputed
# backtest variable is given for scalability, incase a backtest is added in the future
def data_scrape(stock, time, backtest=False):

    # Conversion into ticker symbol object
    stock = yf.Ticker(stock)

    # Obtaining data for volatility/mean and for jump
    # Period for mean and volatility is taken as 30 days while jumps are taken for 1y
    # data array is extracted from jumpdata minimizing API calls
    jumpdata = stock.history(period="1y")
    data = jumpdata[-30:]
    
    # Obtaining prices for volatility/mean and for jump
    prices = data["Close"]
    jump_prices = jumpdata["Close"]

    # Compute daily returns both for vol/mean and jump
    returns = np.log(prices / prices.shift(1)).dropna()
    jump_returns = np.log(jump_prices / jump_prices.shift(1)).dropna()

    # Calculate the mean and volatility
    mean = returns.mean()
    volatility = returns.std()

    # Scaling to daily mean if it's not daily
    mean /= (time * 252)
    volatility /= (time * 252) ** 0.5

    # Computing Threshold for obtaining jumps
    threshold = 3 * jump_returns.std()

    # Obtaining jumps in fractions
    jumps = jump_returns[abs(jump_returns) > threshold]
    jumps = jumps.tolist()

    # Obtaining average jump (Logarithmic)
    ksum = 0
    for i in jumps:
        ksum+=math.log(1+i)
    
    # Considering case if jumps array is empty
    if len(jumps) == 0:
        k = 0
    else:
        k = ksum/len(jumps)

    # Computing jump volatility
    jump_vol_array = []
    for i in jumps:
        jump_vol_array.append(math.log(1+i))
    
    # Considering case if jump_vol_array is empty
    if len(jump_vol_array) == 0:
        sig_j = 0
    else:
        sig_j = np.std(jump_vol_array, ddof=1)

    # Computing Average jump frequency over given time
    lambda_ = len(jumps)/(1/time)

    # Obtaining current price of stock using data
    # Done to minimize API calls
    price = data["Close"].iloc[-1]

    # Returning obtained values
    return (price, mean, volatility, k, sig_j, lambda_)