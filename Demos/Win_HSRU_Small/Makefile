CXX ?= g++
CXXFLAGS = -O3 -std=c++11 -Wall -fPIC -Iinclude

# Add OpenMP if available (optional for Mac, required for fast CPU)
# CXXFLAGS += -fopenmp

all: hsru_edge libhsru_llm.so

hsru_edge: main.cpp src/hsru_math.cpp src/hsru_llm.cpp
	$(CXX) $(CXXFLAGS) -o hsru_edge main.cpp src/hsru_math.cpp src/hsru_llm.cpp

libhsru_llm.so: src/hsru_math.cpp src/hsru_llm.cpp
	$(CXX) $(CXXFLAGS) -shared -o libhsru_llm.so src/hsru_math.cpp src/hsru_llm.cpp

clean:
	rm -f hsru_edge hsru_edge.exe libhsru_llm.so
