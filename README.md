# Merton Jump Diffusion Model

---

## Overview

I will give a quick overview for the normal GBM variables and a detailed explaination of the new variables introduced in this model. If you want a detailed explanation of GBM as such, please check out my "Monte Carlo Share Price Prediction" repository [HERE](https://github.com/nitintonypaul/monte-carlo-spp).

---

### Limitations of the Classic GBM Model

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
- $$t$$ = Time in years (e.g., 1 day = 1/252)  
- $$W_t$$ = Wiener process, where $$W_t = Z \sqrt{t}$$, and $$Z \sim \mathcal{N}(0, 1)$$<br><br>

**Limitations include:**

- **Constant Volatility and Drift:** Assumes market behavior is stable, which it isn’t.
- **No Jumps:** Fails to capture sudden shocks/news events.
- **No Mean Reversion:** Prices can drift infinitely with no tendency to return.
- **Underestimates Extreme Events:** Doesn’t account for fat tails in return distributions.
- **Ignores Real Market Microstructure:** No bid-ask spread, liquidity, or trading constraints.

---

### What is the Merton Jump Diffusion Model?

The **Merton Jump Diffusion Model (JDM)** is an enhancement of the GBM that incorporates **random jumps** in asset prices, aiming to simulate sudden events like earnings surprises, policy changes, or crashes.

Its formula:

$$
S_t = S_0 e^{(\mu - 0.5 \sigma^2 - k\lambda)t + \sigma W_t + \sum_{i=1}^{N(t)} J_i}
$$

Where all original GBM variables apply, and the jump-related terms are:

- $$k$$ = Mean jump size (logarithmic average of all jumps)
- $$\lambda$$ = Average number of jumps per year (jump intensity)
- $$N(t)$$ = A Poisson process representing how many jumps occur up to time $$t$$
- $$J_i$$ = The size of the $$i$$-th jump (typically modeled as log-normally distributed)

---

### Mathematical Explanation

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



