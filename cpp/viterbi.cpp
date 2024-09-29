//
// Created by aiisa on 9/27/2024.
//

#include "viterbi.h"
#include <limits>
#include <vector>
#include <hmm.h>
std::vector<int> viterbi(const HMM& model, const std::vector<int>& observations) {
    int T = observations.size();
    std::vector<std::vector<double>> viterbi(T, std::vector<double>(model.num_states, 0.0));
    std::vector<std::vector<int>> backpointer(T, std::vector<int>(model.num_states, 0));

    // Initialization
    for (int s = 0; s < model.num_states; ++s) {
        viterbi[0][s] = model.initial_probs[s] * model.emission_probs[s][observations[0]];
        backpointer[0][s] = 0;
    }

    // Recursion
    for (int t = 1; t < T; ++t) {
        for (int s = 0; s < model.num_states; ++s) {
            double max_prob = -std::numeric_limits<double>::infinity();
            int best_state = 0;
            for (int prev_s = 0; prev_s < model.num_states; ++prev_s) {
                double prob = viterbi[t - 1][prev_s] * model.transition_probs[prev_s][s];
                if (prob > max_prob) {
                    max_prob = prob;
                    best_state = prev_s;
                }
            }
            viterbi[t][s] = max_prob * model.emission_probs[s][observations[t]];
            backpointer[t][s] = best_state;
        }
    }

    // Termination
    double max_prob = -std::numeric_limits<double>::infinity();
    int best_last_state = 0;
    for (int s = 0; s < model.num_states; ++s) {
        if (viterbi[T - 1][s] > max_prob) {
            max_prob = viterbi[T - 1][s];
            best_last_state = s;
        }
    }

    // Backtracking
    std::vector<int> best_path(T);
    best_path[T - 1] = best_last_state;
    for (int t = T - 2; t >= 0; --t) {
        best_path[t] = backpointer[t + 1][best_path[t + 1]];
    }

    return best_path;
}