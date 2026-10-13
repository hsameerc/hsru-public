#!/bin/bash
CXX=${CXX:-g++}
echo "Linking native libhsru_drone.so on this device..."
if [ -f "lib/libhsru_drone.a" ]; then
    $CXX -shared -fPIC -o lib/libhsru_drone.so -Wl,--whole-archive lib/libhsru_drone.a -Wl,--no-whole-archive -lm -lpthread
    [ -d demo ] && cp lib/libhsru_drone.so demo/ || true
elif [ -f "libhsru_drone.a" ]; then
    $CXX -shared -fPIC -o libhsru_drone.so -Wl,--whole-archive libhsru_drone.a -Wl,--no-whole-archive -lm -lpthread
    [ -d ../lib ] && cp libhsru_drone.so ../lib/ || true
    [ -d ../demo ] && cp libhsru_drone.so ../demo/ || true
elif [ -f "../lib/libhsru_drone.a" ]; then
    $CXX -shared -fPIC -o ../lib/libhsru_drone.so -Wl,--whole-archive ../lib/libhsru_drone.a -Wl,--no-whole-archive -lm -lpthread
    cp ../lib/libhsru_drone.so . || true
fi
echo "Done! Native libhsru_drone.so generated."
