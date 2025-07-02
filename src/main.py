#Importing dependencies
import numpy as np
import sys
import matplotlib.pyplot as plt

# Importing custom libraries
from tools.merton import price_path
from tools.utils import data_scrape

# Obtaining stock (Ticker Symbol) and number of price paths from the user
stock = input("Enter stock name: ")
paths = int(input("Enter number of price paths: "))

# Safety check for paths
# Obtains user confirmation for price paths more than 100
if paths > 100:
    print("==============================================")
    print(f"Simulating {paths} price paths may be demanding on your PC")
    print("Do you want to continue (Y/N): ")
    if (input().lower() != 'y'):
        sys.exit(0)

# Time per trading year (252 trading days in a year)
time = 252/252

# Obtaining necessary values using data_scrape from utils.py
# backtest is defaulted to false (It doesn't change anything if set to true... yet)
price, mean, vol, k, sig_j, lam = data_scrape(stock, time)

# Array to store terminal prices
terminals = []

# TIMES list for plotting prices
# The '24/99' looks weird but it's done so that the TIMES array includes 0 and has a 100 data points
# This is to match the length of priceArray which also has 100 data points making it easy to plot
TIMES = [j*24/99 for j in range(100)]

# Monte Carlo Simulation
# Each iteration, it obtains a price path from merton and appends terminal prices and plots it against TIMES
for i in range(paths):
    priceArray = price_path(price, mean, vol, lam, k, sig_j, time, 100)
    terminals.append(priceArray[-1])
    plt.plot(TIMES, priceArray, alpha=0.9, linewidth=1)

# Plotting current price
plt.plot(price, 'bo', markersize=4, label=f"Current {stock} Price", alpha=0.9)

# Displaying results
print("==============================================")
print("STOCHASTIC SIMULATION - RESULTS MAY VARY")
print(f"Stock chosen for analysis: {stock}")
print(f"Current Price = {price:.2f}")
print(f"Median Expected Price (1 day) = {np.median(terminals):.2f}")
print(f"Average Expected Price (1 day) = {np.mean(terminals):.2f}")
print(f"Lowest Simulated Price = {min(terminals):.2f}")
print(f"Highest Simulated Price = {max(terminals):.2f}")
print(f"Probability of Price Increase = {(len([x for x in terminals if x > price])/len(terminals))*100:.2f}%")
print("==============================================")

# Plotting axis line to indicate 1 day
plt.axvline(x = 24, color='black', linestyle=':', label='1 day', alpha=0.7)

# Adding some informations
plt.legend()
plt.title(f"{paths} Merton price path(s) for {stock}")
plt.xlabel("Hours From Now")
plt.ylabel("Price")
plt.grid(True)
plt.show()