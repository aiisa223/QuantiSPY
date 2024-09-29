//
// Created by aiisa on 9/27/2024.
//
#include <pybind11/pybind11.h>
#include <pybind11/stl.h>
#include "hmm.h"
#include "viterbi.h"

namespace py = pybind11;

PYBIND11_MODULE(cpp_hmm, m) {
py::class_<HMM>(m, "HMM")
.def(py::init<int, int>())
.def_readwrite("num_states", &HMM::num_states)
.def_readwrite("num_observations", &HMM::num_observations)
.def_readwrite("transition_probs", &HMM::transition_probs)
.def_readwrite("emission_probs", &HMM::emission_probs)
.def_readwrite("initial_probs", &HMM::initial_probs);

m.def("viterbi", &viterbi, "Run Viterbi algorithm on HMM",
py::arg("model"), py::arg("observations"));
}