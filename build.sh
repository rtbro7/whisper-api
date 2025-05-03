#!/bin/bash

# Клонируем whisper.cpp, если его нет
if [ ! -d "whisper.cpp" ]; then
  git clone https://github.com/ggerganov/whisper.cpp.git
fi

# Переходим в папку
cd whisper.cpp

# Собираем бинарник
cmake -B build
cmake --build build --config Release

# Возвращаемся в корень и копируем бинарник
cd ..

if [ -f whisper.cpp/build/bin/main ]; then
  cp whisper.cpp/build/bin/main ./main
else
  echo "❌ Бинарник main не найден!" >&2
  exit 1
fi
