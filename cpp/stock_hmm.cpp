#include <vector>
#include <random>
#include <algorithm>
#include <cmath>
#include <limits>
#include <numeric>
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>

namespace py = pybind11;

// Helper function
double logsumexp(const std::vector<double>& vec) {
    double max_val = *std::max_element(vec.begin(), vec.end());
    double sum = 0.0;
    for (double x : vec) {
        sum += std::exp(x - max_val);
    }
    return max_val + std::log(sum);
}

class StockHMM {
private:
    int num_states;
    int num_symbols;
    std::vector<double> initial_probs;
    std::vector<std::vector<double>> transition_probs;
    std::vector<std::vector<double>> emission_probs;
    std::vector<double> mean_returns;
    std::vector<double> std_returns;

public:
    StockHMM(int states = 4) : num_states(states), num_symbols(100) {
        std::random_device rd;
        std::mt19937 gen(rd());
        std::uniform_real_distribution<> dis(0.0, 1.0);

        // Initialize probabilities
        initial_probs.resize(num_states);
        transition_probs.resize(num_states, std::vector<double>(num_states));
        emission_probs.resize(num_states, std::vector<double>(num_symbols));
        mean_returns.resize(num_states);
        std_returns.resize(num_states);

        // Random initialization
        for (int i = 0; i < num_states; ++i) {
            initial_probs[i] = dis(gen);
            mean_returns[i] = dis(gen) * 0.02 - 0.01;  // Random mean between -1% and 1%
            std_returns[i] = dis(gen) * 0.02;  // Random std between 0% and 2%
            for (int j = 0; j < num_states; ++j) {
                transition_probs[i][j] = dis(gen);
            }
            for (int k = 0; k < num_symbols; ++k) {
                emission_probs[i][k] = dis(gen);
            }
        }

        // Normalize probabilities
        double sum_initial = std::accumulate(initial_probs.begin(), initial_probs.end(), 0.0);
        for (int i = 0; i < num_states; ++i) {
            initial_probs[i] /= sum_initial;
            double sum_trans = std::accumulate(transition_probs[i].begin(), transition_probs[i].end(), 0.0);
            double sum_emis = std::accumulate(emission_probs[i].begin(), emission_probs[i].end(), 0.0);
            for (int j = 0; j < num_states; ++j) {
                transition_probs[i][j] /= sum_trans;
            }
            for (int k = 0; k < num_symbols; ++k) {
                emission_probs[i][k] /= sum_emis;
            }
        }
    }

    std::vector<double> forward(const std::vector<int>& observations) const {
        int T = observations.size();
        std::vector<std::vector<double>> alpha(T, std::vector<double>(num_states));

        // Initialize
        for (int i = 0; i < num_states; ++i) {
            alpha[0][i] = std::log(initial_probs[i]) + std::log(emission_probs[i][observations[0]]);
        }

        // Iterate
        for (int t = 1; t < T; ++t) {
            for (int j = 0; j < num_states; ++j) {
                std::vector<double> temp(num_states);
                for (int i = 0; i < num_states; ++i) {
                    temp[i] = alpha[t-1][i] + std::log(transition_probs[i][j]);
                }
                alpha[t][j] = logsumexp(temp) + std::log(emission_probs[j][observations[t]]);
            }
        }

        return alpha.back();
    }

    std::vector<int> viterbi(const std::vector<int>& observations) const {
        int T = observations.size();
        std::vector<std::vector<double>> delta(T, std::vector<double>(num_states));
        std::vector<std::vector<int>> psi(T, std::vector<int>(num_states));

        // Initialize
        for (int i = 0; i < num_states; ++i) {
            delta[0][i] = std::log(initial_probs[i]) + std::log(emission_probs[i][observations[0]]);
            psi[0][i] = 0;
        }

        // Iterate
        for (int t = 1; t < T; ++t) {
            for (int j = 0; j < num_states; ++j) {
                delta[t][j] = -std::numeric_limits<double>::infinity();
                for (int i = 0; i < num_states; ++i) {
                    double prob = delta[t-1][i] + std::log(transition_probs[i][j]) + std::log(emission_probs[j][observations[t]]);
                    if (prob > delta[t][j]) {
                        delta[t][j] = prob;
                        psi[t][j] = i;
                    }
                }
            }
        }

        // Backtrack
        std::vector<int> path(T);
        path[T-1] = std::max_element(delta[T-1].begin(), delta[T-1].end()) - delta[T-1].begin();
        for (int t = T - 2; t >= 0; --t) {
            path[t] = psi[t+1][path[t+1]];
        }

        return path;
    }

    void baum_welch(const std::vector<double>& returns, int max_iterations = 100, double tolerance = 1e-6) {
        int T = returns.size();
        std::vector<int> discretized_returns = discretize_returns(returns);
        double prev_log_likelihood = -std::numeric_limits<double>::infinity();

        for (int iteration = 0; iteration < max_iterations; ++iteration) {
            // Forward-Backward algorithm
            auto [alpha, beta, log_likelihood] = forward_backward(discretized_returns);

            // Compute gamma and xi
            std::vector<std::vector<double>> gamma(T, std::vector<double>(num_states));
            std::vector<std::vector<std::vector<double>>> xi(T-1, std::vector<std::vector<double>>(num_states, std::vector<double>(num_states)));

            for (int t = 0; t < T; ++t) {
                for (int i = 0; i < num_states; ++i) {
                    gamma[t][i] = std::exp(alpha[t][i] + beta[t][i] - log_likelihood);
                    if (t < T - 1) {
                        for (int j = 0; j < num_states; ++j) {
                            xi[t][i][j] = std::exp(alpha[t][i] + std::log(transition_probs[i][j]) +
                                                   std::log(emission_probs[j][discretized_returns[t+1]]) +
                                                   beta[t+1][j] - log_likelihood);
                        }
                    }
                }
            }

            // Update parameters
            for (int i = 0; i < num_states; ++i) {
                initial_probs[i] = gamma[0][i];

                double sum_gamma = 0;
                double sum_returns = 0;
                double sum_squared_returns = 0;
                for (int t = 0; t < T - 1; ++t) {
                    sum_gamma += gamma[t][i];
                    sum_returns += gamma[t][i] * returns[t];
                    sum_squared_returns += gamma[t][i] * returns[t] * returns[t];
                }

                for (int j = 0; j < num_states; ++j) {
                    double sum_xi = 0;
                    for (int t = 0; t < T - 1; ++t) {
                        sum_xi += xi[t][i][j];
                    }
                    transition_probs[i][j] = sum_xi / sum_gamma;
                }

                mean_returns[i] = sum_returns / sum_gamma;
                std_returns[i] = std::sqrt(sum_squared_returns / sum_gamma - mean_returns[i] * mean_returns[i]);

                for (int k = 0; k < num_symbols; ++k) {
                    double lower = (k - num_symbols/2) * (4.0 / num_symbols);
                    double upper = (k - num_symbols/2 + 1) * (4.0 / num_symbols);
                    emission_probs[i][k] = (std::erf((upper - mean_returns[i]) / (std_returns[i] * std::sqrt(2))) -
                                            std::erf((lower - mean_returns[i]) / (std_returns[i] * std::sqrt(2)))) / 2;
                }
            }

            // Check for convergence
            if (std::abs(log_likelihood - prev_log_likelihood) < tolerance) {
                break;
            }
            prev_log_likelihood = log_likelihood;
        }
    }

    std::tuple<std::vector<std::vector<double>>, std::vector<std::vector<double>>, double>
    forward_backward(const std::vector<int>& observations) const {
        int T = observations.size();
        std::vector<std::vector<double>> alpha(T, std::vector<double>(num_states));
        std::vector<std::vector<double>> beta(T, std::vector<double>(num_states, 0.0));

        // Forward pass
        for (int i = 0; i < num_states; ++i) {
            alpha[0][i] = std::log(initial_probs[i]) + std::log(emission_probs[i][observations[0]]);
        }
        for (int t = 1; t < T; ++t) {
            for (int j = 0; j < num_states; ++j) {
                std::vector<double> temp(num_states);
                for (int i = 0; i < num_states; ++i) {
                    temp[i] = alpha[t-1][i] + std::log(transition_probs[i][j]);
                }
                alpha[t][j] = logsumexp(temp) + std::log(emission_probs[j][observations[t]]);
            }
        }

        // Backward pass
        for (int t = T - 2; t >= 0; --t) {
            for (int i = 0; i < num_states; ++i) {
                std::vector<double> temp(num_states);
                for (int j = 0; j < num_states; ++j) {
                    temp[j] = std::log(transition_probs[i][j]) + std::log(emission_probs[j][observations[t+1]]) + beta[t+1][j];
                }
                beta[t][i] = logsumexp(temp);
            }
        }

        double log_likelihood = logsumexp(alpha.back());
        return {alpha, beta, log_likelihood};
    }

    std::vector<int> discretize_returns(const std::vector<double>& returns) const {
        std::vector<int> discretized(returns.size());
        for (size_t i = 0; i < returns.size(); ++i) {
            int symbol = static_cast<int>((returns[i] + 0.02) * num_symbols / 0.04);
            discretized[i] = std::max(0, std::min(num_symbols - 1, symbol));
        }
        return discretized;
    }

    double predict_next_return() const {
        double predicted_return = 0.0;
        for (int i = 0; i < num_states; ++i) {
            predicted_return += initial_probs[i] * mean_returns[i];
        }
        return predicted_return;
    }

    double calculate_aic(double log_likelihood) const {
        int num_params = num_states * (num_states - 1) + num_states * (num_symbols - 1) + num_states * 2;
        return 2 * num_params - 2 * log_likelihood;
    }

    double calculate_bic(double log_likelihood, int num_observations) const {
        int num_params = num_states * (num_states - 1) + num_states * (num_symbols - 1) + num_states * 2;
        return num_params * std::log(num_observations) - 2 * log_likelihood;
    }

    double calculate_hqc(double log_likelihood, int num_observations) const {
        int num_params = num_states * (num_states - 1) + num_states * (num_symbols - 1) + num_states * 2;
        return -2 * log_likelihood + 2 * num_params * std::log(std::log(num_observations));
    }

    double calculate_caic(double log_likelihood, int num_observations) const {
        int num_params = num_states * (num_states - 1) + num_states * (num_symbols - 1) + num_states * 2;
        return -2 * log_likelihood + num_params * (std::log(num_observations) + 1);
    }

    double calculate_out_of_sample_r_squared(const std::vector<double>& true_returns, const std::vector<double>& predicted_returns) const {
        double mean_return = std::accumulate(true_returns.begin(), true_returns.end(), 0.0) / true_returns.size();
        double tss = 0.0, rss = 0.0;
        for (size_t i = 0; i < true_returns.size(); ++i) {
            tss += std::pow(true_returns[i] - mean_return, 2);
            rss += std::pow(true_returns[i] - predicted_returns[i], 2);
        }
        return 1.0 - (rss / tss);
    }

    std::string get_trading_signal() const {
        double predicted_return = predict_next_return();
        if (predicted_return > 0.005) {  // 0.5% threshold for buying
            return "BUY";
        } else if (predicted_return < -0.005) {  // -0.5% threshold for selling
            return "SELL";
        } else {
            return "HOLD";
        }
    }

    // Getter methods
    std::vector<double> get_initial_probs() const { return initial_probs; }
    std::vector<std::vector<double>> get_transition_probs() const { return transition_probs; }
    std::vector<std::vector<double>> get_emission_probs() const { return emission_probs; }
    std::vector<double> get_mean_returns() const { return mean_returns; }
    std::vector<double> get_std_returns() const { return std_returns; }
};

PYBIND11_MODULE(cpp_stock_hmm, m) {
py::class_<StockHMM>(m, "StockHMM")
.def(py::init<int>())
.def("forward", &StockHMM::forward)
.def("viterbi", &StockHMM::viterbi)
.def("baum_welch", &StockHMM::baum_welch)
.def("predict_next_return", &StockHMM::predict_next_return)
.def("calculate_aic", &StockHMM::calculate_aic)
.def("calculate_bic", &StockHMM::calculate_bic)
.def("calculate_hqc", &StockHMM::calculate_hqc)
.def("calculate_caic", &StockHMM::calculate_caic)
.def("calculate_out_of_sample_r_squared", &StockHMM::calculate_out_of_sample_r_squared)
.def("get_trading_signal", &StockHMM::get_trading_signal)
.def("get_initial_probs", &StockHMM::get_initial_probs)
.def("get_transition_probs", &StockHMM::get_transition_probs)
.def("get_emission_probs", &StockHMM::get_emission_probs)
.def("get_mean_returns", &StockHMM::get_mean_returns)
.def("get_std_returns", &StockHMM::get_std_returns);
}