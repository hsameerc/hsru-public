CXX ?= g++
CXXFLAGS = -O3 -std=c++11 -Wall -Iinclude
LDFLAGS = 

ifeq ($(OS), Windows_NT)
    CXXFLAGS += -fopenmp -static
    LDFLAGS = libhsru_llm.dll
    RM = del /Q /F
else ifeq ($(shell uname -s), Darwin)
    ifneq ($(wildcard /opt/homebrew/opt/llvm/bin/clang++),)
        CXX = /opt/homebrew/opt/llvm/bin/clang++
        CXXFLAGS += -Xclang -fopenmp -I/opt/homebrew/opt/libomp/include -mmacosx-version-min=11.0
        LDFLAGS += /opt/homebrew/opt/libomp/lib/libomp.a
    endif
    LDFLAGS += -L. -lhsru_llm -Wl,-rpath,.
    RM = rm -f
else
    CXXFLAGS += -fopenmp -static-libgcc -static-libstdc++
    LDFLAGS = -L. -lhsru_llm -Wl,-rpath,.
    RM = rm -f
endif

all: hsru_edge

hsru_edge: main.cpp
	$(CXX) $(CXXFLAGS) -o hsru_edge main.cpp $(LDFLAGS)

clean:
	-$(RM) hsru_edge hsru_edge.exe
