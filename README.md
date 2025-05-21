# Merton Jump Diffusion Model

---

## Overview

I will give a quick overview for the normal GBM variables and a detailed explaination of the new variables introduced in this model. If you want a detailed explanation of GBM as such, please check out my "Monte Carlo Share Price Prediction" repository [HERE](https://github.com/nitintonypaul/monte-carlo-spp).

---

## Limitations of the Classic GBM Model

The classic Geometric Brownian Motion (GBM) is of the form:

$$
S_t = S_0 e^{(\mu - 0.5 \sigma^2)t + \sigma W_t}
$$

Where:

- $$S_t$$ = Expected future price  
- $$S_0$$ = Current price  
- $$e$$ = Euler’s number  
- $$\mu$$ = Drift (average return)  
- $$\sigma$$ = Volatility (price fluctuation)  
- $$t$$ = Time in trading years (e.g., 1 day = 1/252, since there are 252 trading days in a year)  
- $$W_t$$ = Wiener process, where $$W_t = Z \sqrt{t}$$, and $$Z \sim \mathcal{N}(0, 1)$$<br><br>

**Limitations include:**

- **Constant Volatility and Drift:** Assumes market behavior is stable, which it isn’t.
- **No Jumps:** Fails to capture sudden shocks/news events.
- **No Mean Reversion:** Prices can drift infinitely with no tendency to return.
- **Underestimates Extreme Events:** Doesn’t account for fat tails in return distributions.
- **Ignores Real Market Microstructure:** No bid-ask spread, liquidity, or trading constraints.

---

## What is the Merton Jump Diffusion Model?

The **Merton Jump Diffusion Model (JDM)** is an enhancement of the GBM that incorporates **random jumps** in asset prices, aiming to simulate sudden events like earnings surprises, policy changes, or crashes.

Its formula:

$$
S_t = S_0 e^{(\mu - 0.5 \sigma^2 - k\lambda)t + \sigma W_t + \sum_{i=1}^{N(t)} J_i}
$$

Where all original GBM variables apply, and the jump-related terms are:

- $$k$$ = Mean jump size (logarithmic average of all jumps)
- $$\lambda$$ = Average number of jumps per time period (jump intensity/frequency)
- $$N(t)$$ = A Poisson process representing how many jumps occur up to time $$t$$
- $$J_i$$ = The size of the $$i$$-th jump (typically modeled as log-normally distributed)

---

# Mathematical Explanation

Let’s break down the new jump-related variables:

- **Jump Intensity ($$\lambda$$)**: Represents how frequently jumps are expected. A $$\lambda$$ of 2 means 2 jumps per day on average (If the time period is taken as 1 day).

- **Average Jump Size ($$k$$)**: This is calculated as:

$$
k = mean(ln(1 + J))
$$

  where $$J$$ is a random variable representing the proportional jump size (In fractions). This value adjusts the drift so the model remains unbiased over time.

  An example: Let's take the jump percentage of a stock $$X$$ to be 47%, -33%, -10% and 89% in a given time frame. We can compute the **Average Jump Size ($$k$$)** by

$$
k = \frac{ln(1+0.47) + ln(1-0.33) + ln(1-0.1) + ln(1+0.89)}{4}
$$

  Where $$4$$ is the number of jumps recorded. This gives us a value of 

$$
k = 0.129000286
$$

- **Jump Process ($$N(t)$$)**: A **Poisson-distributed** random variable that gives the total number of jumps in time $$t$$. It has a mean  and variance of $$\lambda t$$. It is represented as

$$
N(t) \sim \mathcal{P}(\lambda t)
$$

- **Jump Magnitude ($$J_i$$)**: Represents the size of the $$i^{th}$$ jump. Typically drawn from a log-normal distribution. The sum $$\sum_{i=1}^{N(t)} J_i$$ accounts for the total log-return from all jumps up to time $$t$$.

$$J_i$$ or $$J$$ is computed by

$$
J \sim \mathcal{N}(ln(1+k)- \frac{\sigma_j^{2}}{2}, \sigma_j^{2})
$$

Where $$\sigma_j$$ is the **jump volatility**, which represents the standard deviation of log jump sizes. For example, if we consider the set of jumps of a stock $$Y$$ as 15%, 30%, 10% and 25%, the average jump percentage becomes

$$
\frac{15+30+10+25}{4} = 20
$$

So, $$\sigma_j$$ can be computed by

$$
\sigma_j = \sqrt{\frac{(20-15)^2 + (20-30)^2 + (20-25)^2 + (20-10)^2}{4}}
$$

OR

$$
\sigma_j = 7.906
$$

Which is the **standard deviation** of the set of jumps of the stock $$Y$$.<br><br><br>

Together, these additions allow the model to simulate rare but impactful market movements while still preserving the standard GBM structure.

---

## PSEUDOCODE

```py
IMPORT dependencies (yfinance, numpy, math, mcs_simulator)

#Function
DECLARE function data_scrape(stock, time)

  CONVERT stock to ticker object using yf.Ticker()
  FETCH data from stock.history() for a period of 30 days
  FETCH jump_data from stock.history() for a period of 1 year

  #Obtaining prices when the market closes each day
  FETCH prices from data["Close"]
  FETCH jump_prices from jump_data["Close"]

  #Computing returns
  COMPUTE returns as np.log(prices / prices.shift(1)).dropna()
  COMPUTE jump_returns as jump_prices.pct_change().dropna()

  #Computing mean and volatility
  COMPUTE mean as returns.mean() and volatility as returns.std()
  COMPUTE annual_mean as mean * 252 and annual_volatility as volatility * np.sqrt(252)

  #Defining threshold
  COMPUTE threshold as 3 * jump_returns.std()
  COMPUTE jumps as jump_returns[abs(jump_returns) > threshold].tolist()

  #Computing k
  DECLARE ksum as 0
  FOR each i in jumps
    INCREMENT ksum by math.log(1+i)
  IF length(jumps) is 0
    DECLARE k as 0
  ELSE
    DECLARE k as ksum / length(jumps)

  #Computing jump volatility
  DECLARE jump_array as empty array
  FOR each i in jumps
    APPEND math.log(1+i) to jump_array
  IF length(jump_array) is 0
    DECLARE sig_j as 0
  ELSE
    COMPUTE sig_j as np.std(jump_array, ddof=1)

  COMPUTE lambda_ as length(jumps) / (1 / time)
  RETURN (annual_mean, annual_volatility, k, sig_j, lambda_)

#Obtaining data
OBTAIN stock from the user
OBTAIN simulations from the user

FETCH data_today from yf.Ticker(stock).history(period="1d")
FETCH price from data_today["Close"].iloc[-1]

DECLARE time as 1/252
OBTAIN mean, vol, k, sig_j, lam from data_scrape(stock, time)

#Declaring variables
DECLARE price_sum = 0
COMPUTE base_wt = (time)^0.5, first_term = mean - vol^2 - lam*k

#Simulation using C++ module
COMPUTE expected_price from mcs_simulator.run_simulation(price, mean, vol, lam, k, sig_j, time)

DISPLAY expected_price
```

---

## Disclaimer

This Merton model implementation has an estimated accuracy above 50%, but it is not intended for making critical financial decisions. All simulations and predictions are for educational or illustrative purposes only. Any financial decisions you make based on this model are solely your responsibility. We disclaim any liability for losses or damages resulting from its use.

---

## Build Instructions

Download the ZIP folder from the repo and extract it to your local machine before proceeding.

### Windows

No build required. The compiled module is already located in the `src` directory.

**To run:**
```bash
python src/main.py
```


### macOS and Linux

**Prerequisites:**

- Ensure `Python 3.x` is installed along with a C++ compiler (`GCC` for Linux or `Clang` for macOS), and the `setuptools` and `pybind11` Python packages.

Ubuntu/Debian:

```bash
sudo apt update
sudo apt install python3-dev python3-pip build-essential
pip3 install setuptools pybind11
```

macOS:

```shell
xcode-select --install
brew install python
pip3 install setuptools pybind11
```

<br>

**Building:**

Run the following from the root directory (where `setup.py` is):
```bash
python3 setup.py build_ext --inplace
```

This will generate a `.so` file in the root folder. Something like this:
```bash
mcs_simulator.cpython-311-darwin.so  # macOS
mcs_simulator.cpython-311-x86_64-linux-gnu.so  # Linux
```

<br>

**Running:**

Move the `.so` file into `src/` and run:
```bash
python3 src/main.py
```

---
## Demo

```shell
#Test 1: AAPL (Apple Inc.) for 200,000 simulations (Price in USD)

Enter stock name: AAPL
=========================================================
Stock chosen: AAPL
Price of AAPL right now = 206.86000061035156
Price of AAPL after 1 day is simulated to be = 208.04017825275457
=========================================================
```

```shell
#Test 2: GME (GameStop Corp) for 200,000 simulations (Price in USD)

Enter stock name: GME
=========================================================
Stock chosen: GME
Price of GME right now = 28.510000228881836
Price of GME after 1 day is simulated to be = 28.6943765265786
=========================================================
```

```shell
#Test 3: RELIANCE for 200,000 simulations (Price in INR)

Enter stock name: RELIANCE.NS
=========================================================
Stock chosen: RELIANCE.NS
Price of RELIANCE.NS right now = 1430.699951171875
Price of RELIANCE.NS after 1 day is simulated to be = 1438.926053886467
=========================================================
```

---
