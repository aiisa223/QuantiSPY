#ifndef VITERBI_H
#define VITERBI_H

#include <vector>
#include "hmm.h"

std::vector<int> viterbi(const HMM& model, const std::vector<int>& observations);

#endif