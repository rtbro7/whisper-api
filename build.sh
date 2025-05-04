#!/bin/bash

# Клонируем whisper.cpp, если его нет
if [ ! -d "whisper-cpp" ]; then
  git clone https://github.com/ggerganov/whisper.cpp.git whisper-cpp
fi

# Переходим в папку
cd whisper-cpp

# Сборка
cmake -B build -DCMAKE_BUILD_TYPE=Release
cmake --build build

# Возврат в корень и копирование бинарника
cd ..
if [ -f whisper-cpp/build/bin/main ]; then
  cp whisper-cpp/build/bin/main .
else
  echo "Бинарник main не найден!" >&2
  exit 1
fi
