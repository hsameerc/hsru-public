CXX ?= g++
CXXFLAGS = -O3 -std=c++11 -Wall -I../include

all: demo_run

demo_run: demo.cpp
	$(CXX) $(CXXFLAGS) -o demo_run demo.cpp -L../lib -lhsru_drone -Wl,-rpath,../lib

clean:
	rm -f demo_run
