CXX ?= g++
CXXFLAGS = -O3 -std=c++11 -Wall -Iinclude -fopenmp -static -static-libgcc -static-libstdc++

all: hsru_edge.exe

hsru_edge.exe: main.cpp
	$(CXX) $(CXXFLAGS) -o hsru_edge.exe main.cpp -L. -lhsru_llm

clean:
	rm -f hsru_edge.exe
