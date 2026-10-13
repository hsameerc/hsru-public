#!/bin/bash
CXX=${CXX:-g++}
echo "Linking native libhsru_llm.so on this device..."
if [ -f "libhsru_llm.a" ]; then
    $CXX -shared -fPIC -o libhsru_llm.so -Wl,--whole-archive libhsru_llm.a -Wl,--no-whole-archive -fopenmp -lpthread -lm
fi
echo "Done! Native libhsru_llm.so generated."
