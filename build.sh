#!/bin/bash

# Клонируем whisper.cpp, если его нет
if [ ! -d "whisper.cpp" ]; then
  git clone https://github.com/ggerganov/whisper.cpp.git
fi

cd whisper.cpp

# Собираем бинарник
cmake -B build
cmake --build build --config Release

# Копируем бинарник main в корень проекта
cp build/bin/main ../
