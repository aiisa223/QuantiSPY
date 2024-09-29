//
// Created by aiisa on 9/27/2024.
//

#ifndef HMM_H
#define HMM_H

#include <vector>

class HMM {
public:
    int num_states;
    int num_observations;
    std::vector<std::vector<double>> transition_probs;
    std::vector<std::vector<double>> emission_probs;
    std::vector<double> initial_probs;

    HMM(int states, int obs);
};

#endif