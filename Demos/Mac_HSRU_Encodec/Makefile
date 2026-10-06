CXX      = g++
CXXFLAGS = -O3 -Wall -std=c++17 -Iinclude -mmacosx-version-min=11.0
LDFLAGS  = -Llib -lhsru_codec -Wl,-rpath,@executable_path/lib

all: demo inference inference_stream

demo: demo.cpp
	$(CXX) $(CXXFLAGS) demo.cpp -o demo $(LDFLAGS)

inference: inference.cpp
	$(CXX) $(CXXFLAGS) inference.cpp -o inference $(LDFLAGS)

inference_stream: inference_stream.cpp
	$(CXX) $(CXXFLAGS) inference_stream.cpp -o inference_stream $(LDFLAGS)

clean:
	rm -f demo inference inference_stream
