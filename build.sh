#!/bin/bash

# Клонируем whisper.cpp, если его нет
if [ ! -d "whisper-cpp" ]; then
    git clone https://github.com/ggerganov/whisper.cpp.git whisper-cpp
fi

# Переходим в папку
cd whisper-cpp

# Собираем бинарник
cmake -B build
cmake --build build --config Release

# Копируем бинарник main в корень проекта
if [ -f build/bin/main ]; then
  cp build/bin/main ../main
else
  echo "❌ Бинарник main не найден!" >&2
  exit 1
fi
