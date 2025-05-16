#Importing dependencies
import yfinance as yf
import numpy as np
import math

#data_scrape function to obtain precomputed values
def data_scrape(stock, time):

    #Conversion into ticker symbol object
    stock = yf.Ticker(stock)

    #Obtaining data for volatility/mean and for jump
    data = stock.history(period="30d")  #Period for mean and volatility is taken as 30 days
    jumpdata = stock.history(period="1y")  #Period for jumps array is taken to be 1 year
    
    #Obtaining prices for volatility/mean and for jump
    prices = data["Close"]
    jump_prices = jumpdata["Close"]

    #Compute daily returns both for vol/mean and jump
    returns = np.log(prices / prices.shift(1)).dropna()
    jump_returns = jump_prices.pct_change().dropna()

    #Calculate the mean and volatility
    mean = returns.mean()
    volatility = returns.std()

    #Convert into annual values
    annual_mean = mean * 252
    annual_volatility = volatility * np.sqrt(252)

    # Computing Threshold for obtaining jumps
    threshold = 3 * jump_returns.std()

    #Obtaining jumps in fractions
    jumps = jump_returns[abs(jump_returns) > threshold]
    jumps = jumps.tolist()

    #Obtaining average jump (Logarithmic)
    ksum = 0
    for i in jumps:
        ksum+=math.log(1+i)
    
    #Considering case if jumps array is empty
    if len(jumps) == 0:
        k = 0
    else:
        k = ksum/len(jumps)

    #Computing jump volatility
    jump_vol_array = []
    for i in jumps:
        jump_vol_array.append(math.log(1+i))
    
    #Considering case if jump_vol_array is empty
    if len(jump_vol_array) == 0:
        sig_j = 0
    else:
        sig_j = np.std(jump_vol_array, ddof=1)

    #Computing Average jump frequency over given time
    lambda_ = len(jumps)/(252/time)

    #Returning obtained values
    return (annual_mean, annual_volatility, k, sig_j, lambda_)

#Obtaining stock (Ticker Symbol) and number of simulations from user
stock = input("Enter stock name: ")
simulations = int(input("Enter the number of simulations: "))

#Obtaining today's stock priice
data_today = yf.Ticker(stock).history(period="1d")
price = data_today["Close"].iloc[-1]

#Time in days (252 trading days in a year)
time = 1

#Obtaining values of mean, vol, average logarithmic jump, jump volatility and jump frequency
mean, vol, k, sig_j, lam = data_scrape(stock,time)

#Assigning price sum, reassigning time to fractions (per year), computing base_wt for efficiency and computing first_term for efficiency
price_sum = 0
time = time/252
base_wt = (time)**0.5
first_term = mean - (vol**2) - (lam*k)

#Monte Carlo Simulation
for i in range(simulations):
    
    #Wiener Process
    Z = np.random.normal(0,1)
    Wt = Z * base_wt

    #Obtaining N(t)
    N_t = np.random.poisson(lam*time)

    #Computing Ji
    Ji_sum = 0

    #Inner loop to compute summation of Ji till N(t)
    for j in range(1,N_t+1):

        #Finding J as a random number from the normal distribution of log(1+k) - sig_j^2 with a std of sig_j [sig_j is the jump volatility]
        J = np.random.normal(math.log(1+k)-((sig_j)**2)/2, sig_j)
        Ji_sum += J
    
    #Computing simulated price per iteration
    simulated_price = price * math.e ** ((first_term * time) + (vol * Wt) + Ji_sum)

    #price_sum by simulated price
    price_sum += simulated_price

#Taking the average of price_sum to obtain expected price
expected_price = price_sum/simulations

# Print results
print("=========================================================")
print(f"Stock chosen: {stock}")
print(f"Price of {stock} right now = {price}")
print(f"Price of {stock} after 1 day is simulated to be = {expected_price}")
print("=========================================================")
