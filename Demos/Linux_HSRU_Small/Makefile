CXX ?= g++
CXXFLAGS = -O3 -std=c++11 -Wall -Iinclude -fopenmp

all: hsru_edge

hsru_edge: main.cpp
	$(CXX) $(CXXFLAGS) -o hsru_edge main.cpp -L. -lhsru_llm -Wl,-rpath,.

clean:
	rm -f hsru_edge
