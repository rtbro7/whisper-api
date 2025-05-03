#!/bin/bash

# Устанавливаем cmake и компилируем whisper.cpp
apt-get update && apt-get install -y build-essential cmake git

# Клонируем whisper.cpp, если не клонирован
if [ ! -d "whisper.cpp" ]; then
  git clone https://github.com/ggerganov/whisper.cpp.git
fi

cd whisper.cpp
cmake -B build
cmake --build build --config Release

# Копируем бинарник
cp build/bin/main ../main
chmod +x ../main
