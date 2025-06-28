//Including header files
#include <iostream>
#include <random>
#include <cmath>
#include <vector>

//pybind11 to build into python module
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> 

namespace py = pybind11;

// Defining functions
std::vector<double> price_path (double price, double mean, double vol, double lam, double k, double sig_j, double time, int plots=100);
double estimate(double price, double mean, double vol, double lam, double k, double sig_j, double time, std::mt19937 &gen);

// Price path function
// Obtains price path with 100 data points (Including the initial price)
std::vector<double> price_path (double price, double mean, double vol, double lam, double k, double sig_j, double time, int plots) {

    // Declaring price path array and initializing first value to current price
    std::vector<double> prices(plots);
    prices[0] = price;

    // Random number engine
    // Defined in this function to increase computational efficiency
    std::random_device rd;
    std::mt19937 gen(rd());

    // Precomputing dt and initializing previousPRICE variable
    double dt = time/plots;
    double previousPRICE = price;

    // Finding the price path of the stock
    // Compounds from previousPRICE essentially making it recursive
    for (int i = 1; i <= (plots-1); i++) {
        previousPRICE = estimate (previousPRICE, mean, vol, lam, k, sig_j, dt, gen);
        prices[i] = previousPRICE;
    }

    // Debugging code
    // std::cout << prices.size() << std::endl;

    // Returning the list to python to plot on graph and further analysis
    return prices;
}

//Merton Jump Diffusion expected price estimation function
double estimate (double price, double mean, double vol, double lam, double k, double sig_j, double time, std::mt19937 &gen) {

    // J distribution variables
    double J_mean = std::log(1+k)-(std::pow(sig_j, 2)/ (double)2);

    // Initializing distributions for Brownian noise and Jump component
    // Assigning functions for the respective distributions to be used in MJD
    std::normal_distribution<double> wiener_dist(0.0, 1.0);
    std::normal_distribution<double> J_dist(J_mean, sig_j);
    std::poisson_distribution<int> poisson(lam*time);
    
    // PREPARING VARIABLES FOR MJD
    // Wiener Process
    double Z = wiener_dist(gen);
    double Wt = Z * std::pow(time, 0.5);

    // Obtaining N_t
    int N_t = poisson(gen);

    // Computing J_i sum
    double Ji_sum = 0.000;
    for (int j = 1; j <= N_t; j++) {
        double J = J_dist(gen);
        Ji_sum += J;
    }

    // MJD EQUATION
    // Computing and returning expected price using MJD equation
    // MJD EQUATION roughly is price * exp ( mean.time + BROWNIAN NOISE + JUMP COMPONENT)
    double expected_price = price * std::exp( (mean * time) + (vol * Wt) + Ji_sum);

    // Why do I even use expected_price variable when I can return it directly?
    // I guess we'll never know
    return expected_price;
}

//pybind11 declaration
PYBIND11_MODULE(merton, m) {
    m.def("price_path", &price_path,
          "Monte Carlo Simulation to simulate price paths.");
}
