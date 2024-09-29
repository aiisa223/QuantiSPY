//
// Created by aiisa on 9/27/2024.
//


#include "hmm.h"

HMM::HMM(int states, int obs) : num_states(states), num_observations(obs) {
    transition_probs.resize(states, std::vector<double>(states, 0.0));
    emission_probs.resize(states, std::vector<double>(obs, 0.0));
    initial_probs.resize(states, 0.0);
}