cmake_minimum_required(VERSION 3.10)
project(QuantiSPY)

set(CMAKE_CXX_STANDARD 11)

find_package(Python COMPONENTS Interpreter Development REQUIRED)
find_package(pybind11 CONFIG REQUIRED)

# Set the include directory
include_directories(${CMAKE_CURRENT_SOURCE_DIR}/cpp)

# List all your source files
set(SOURCES
        cpp/hmm.cpp
        cpp/viterbi.cpp
        cpp/hmm_wrapper.cpp
        )

# List all your header files
set(HEADERS
        cpp/hmm.h
        cpp/viterbi.h
        )

pybind11_add_module(cpp_hmm ${SOURCES} ${HEADERS})

# Set the target include directories
target_include_directories(cpp_hmm PRIVATE ${CMAKE_CURRENT_SOURCE_DIR}/cpp)