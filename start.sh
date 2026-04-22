#!/bin/bash
set -e
echo "=== Установка Emergency Engine ==="
mkdir -p temp
cd temp
wget -q https://github.com/official-stockfish/Stockfish/releases/download/sf_18/stockfish-ubuntu-x86-64-bmi2.tar
tar -xf stockfish-ubuntu-x86-64-bmi2.tar
cp stockfish/stockfish-ubuntu-x86-64-bmi2 ../emergency_engine
cd ..
rm -rf temp
chmod +x ./emergency_engine
exec gunicorn -k uvicorn.workers.UvicornWorker -b 0.0.0.0:$PORT engine:app
