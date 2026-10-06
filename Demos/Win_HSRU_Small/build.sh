#!/bin/bash
echo "========================================"
echo " Building HSRU Zero-Dependency Engine "
echo "========================================"
make clean
make
echo "========================================"
echo "Build complete! You can now run the standalone executable:"
echo "Linux/Mac: ./hsru_edge"
echo "Windows:   hsru_edge.exe"
