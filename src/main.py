#Importing dependencies
import yfinance as yf
import numpy as np
import math
import matplotlib.pyplot as plt
from merton import price_path

# data_scrape function to obtain values from yfinance
# Necessary values are precomputed
def data_scrape(stock, time):

    # Conversion into ticker symbol object
    stock = yf.Ticker(stock)

    # Obtaining data for volatility/mean and for jump
    data = stock.history(period="30d")  #Period for mean and volatility is taken as 30 days
    jumpdata = stock.history(period="1y")  #Period for jumps array is taken to be 1 year
    
    # Obtaining prices for volatility/mean and for jump
    prices = data["Close"]
    jump_prices = jumpdata["Close"]

    # Compute daily returns both for vol/mean and jump
    returns = np.log(prices / prices.shift(1)).dropna()
    jump_returns = jump_prices.pct_change().dropna()

    # Calculate the mean and volatility
    mean = returns.mean()
    volatility = returns.std()

    # Convert into annual values
    annual_mean = mean * 252
    annual_volatility = volatility * np.sqrt(252)

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

    # Returning obtained values
    return (annual_mean, annual_volatility, k, sig_j, lambda_)

# Obtaining stock (Ticker Symbol) and number of price paths from the user
stock = input("Enter stock name: ")
paths = int(input("Enter number of paths: "))

# Obtaining today's stock price
data_today = yf.Ticker(stock).history(period="1d")
price = data_today["Close"].iloc[-1]

# Time per trading year (252 trading days in a year)
time = 1/252

# Obtaining values of mean, vol, average logarithmic jump, jump volatility and jump frequency
mean, vol, k, sig_j, lam = data_scrape(stock,time)

# Array to store terminal prices
terminals = []

# TIMES list for plotting prices
TIMES = [j*24/99 for j in range(100)]

# Monte Carlo Simulation
# Each iteration, it obtains a price path from merton and appends terminal prices and plots it against TIMES
for i in range(paths):
    priceArray = price_path(price, mean, vol, lam, k, sig_j, time)
    terminals.append(priceArray[-1])
    plt.plot(TIMES, priceArray, alpha=0.9, linewidth=1)

# Displaying results
print("==============================================")
print("RESULTS (MAY VARY EACH RUN)")
print(f"Stock chosen for analysis: {stock}")
print(f"Current Price = {price:.2f}")
print(f"Median Expected Price (1 day) = {np.median(terminals):.2f}")
print(f"Average Expected Price (1 day) = {np.mean(terminals):.2f}")
print(f"Chances of Price Increase = {(len([x for x in terminals if x > price])/len(terminals))*100:.2f}%")
print("==============================================")

# Plotting price paths
plt.axvline(x = 24, color='red', linestyle='--', label='1 day', alpha=0.5)
plt.legend()
plt.title(f"{paths} Merton price path(s) for {stock}")
plt.xlabel("Time (Hours)")
plt.ylabel("Price")
plt.grid(True)
plt.show()