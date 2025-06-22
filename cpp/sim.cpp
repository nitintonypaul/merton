//Including header files
#include <iostream>
#include <random>
#include <cmath>

//pybind11 to build into python module
#include <pybind11/pybind11.h>
#include <pybind11/stl.h> 

namespace py = pybind11;

// Defining functions
std::vector<double> price_path (double price, double mean, double vol, double lam, double k, double sig_j, double time);
double estimate(double price, double mean, double vol, double lam, double k, double sig_j, double time, std::mt19937 &gen);

// Price path function
// Obtains price path with 100 data points
std::vector<double> price_path (double price, double mean, double vol, double lam, double k, double sig_j, double time) {

    // Declaring price path array
    std::vector<double> prices(100);
    prices[0] = price;

    // Random number engine
    // Defined in this function to increase computational efficiency
    std::random_device rd;
    std::mt19937 gen(rd());

    // Precomputing dt to increase computational efficiency
    double dt = time/101;

    // Monte Carlo Simulation to find the price path of the given stock
    for (int i = 1; i <= 100; i++) {
        prices[i] = estimate (price, mean, vol, lam, k, sig_j, dt*i, gen);
    }

    // Returning the list to python to plot on graph and further analysis
    return prices;
}

//Merton Jump Diffusion expected price estimation function
double estimate (double price, double mean, double vol, double lam, double k, double sig_j, double time, std::mt19937 &gen) {

    // This was the critical mistake. "first_term" was used instead of "mean" in MJD EQUATION
    // double first_term = mean - (std::pow(vol, 2)) - (lam*k);

    // J distribution variables
    double J_mean = std::log(1+k)-(std::pow(sig_j, 2)/ (double)2);

    // Distributions
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
    for (int j = 1; j<= N_t; j++) {
        double J = J_dist(gen);
        Ji_sum += J;
    }

    // MJD EQUATION
    // Computing and returning expected price using MJD equation
    double expected_price = price * std::exp( (mean * time) + (vol * Wt) + Ji_sum);
    return expected_price;
}

//pybind11 declaration
PYBIND11_MODULE(merton, m) {
    m.def("price_path", &price_path,
          "Monte Carlo Simulation to simulate price paths.");
}