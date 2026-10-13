#!/bin/bash
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CXX=${CXX:-g++}
echo "Linking native libhsru_drone.so on this device..."
if [ -f "$DIR/libhsru_drone.a" ]; then
    $CXX -shared -fPIC -o "$DIR/libhsru_drone.so" -Wl,--whole-archive "$DIR/libhsru_drone.a" -Wl,--no-whole-archive -lm -lpthread
    echo "Done! Native libhsru_drone.so generated at $DIR/libhsru_drone.so."
else
    echo "Error: $DIR/libhsru_drone.a not found."
    exit 1
fi
