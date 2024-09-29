import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'Release')))
print("Python path:", sys.path)

try:
    import cpp_hmm

    print("cpp_hmm imported successfully")
    print("cpp_hmm module:", cpp_hmm)
    print("cpp_hmm directory:", dir(cpp_hmm))

    # Create an HMM instance
    hmm = cpp_hmm.HMM(2, 3)  # Assuming 2 states and 3 possible observations
    print("HMM instance created:", hmm)

    # Set some probabilities (adjust these based on your HMM implementation)
    hmm.transition_probs = [[0.7, 0.3], [0.4, 0.6]]
    hmm.emission_probs = [[0.5, 0.4, 0.1], [0.1, 0.3, 0.6]]
    hmm.initial_probs = [0.6, 0.4]

    # Test the Viterbi algorithm
    observations = [0, 1, 2, 1]
    path = cpp_hmm.viterbi(hmm, observations)
    print("Viterbi path:", path)

except ImportError as e:
    print(f"Failed to import cpp_hmm: {e}")
except AttributeError as e:
    print(f"Failed to use cpp_hmm: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")
