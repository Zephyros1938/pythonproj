#!/bin/bash
#
# no i wont support mac, blame them for using dynlib :3
#
#       (also this script was a pain to make :sob:)

TO_COMPILE="stb_image test"

rm -rf libraries/compiled/*
echo "[ INFO    ] Removed all compiled libraries."
echo "[ INFO    ] To Compile:"
for item in $TO_COMPILE; do
    echo "[ INFO    ]  - $item"
done

for item in $TO_COMPILE; do
    echo "[ INFO    ] Compile $item"
    mkdir "libraries/compiled/$item"

    echo "[ INFO    ]  Start compile Linux libraries"
    echo "[ COMPILE ]   Compile $item.a"
    g++ -c libraries/$item.cpp -o libraries/compiled/$item/$item.o -fPIC
    g++ -shared -o libraries/compiled/$item/$item.so libraries/compiled/$item/$item.o
    if [ ! -f libraries/compiled/$item/$item.o ]; then
        echo "[ ERROR   ] Failed to compile object file ($item.o)."
        exit 1
    fi
    objcopy -O elf64-x86-64 libraries/compiled/$item/$item.o libraries/compiled/$item/$item.a
    echo "[ COMPILE ]   Compile $item.so"

    echo "[ INFO    ]  Start compile OSX libraries"
    echo "[ COMPILE ]   Compile $item.lib"
    x86_64-w64-mingw32-g++ -c libraries/$item.cpp -o libraries/compiled/$item/$item.o -fPIC
    if [ ! -f libraries/compiled/$item/$item.o ]; then
        echo "[ ERROR   ] Failed to compile object file for Windows."
        exit 1
    fi
    ar rcs libraries/compiled/$item/$item.lib libraries/compiled/$item/$item.o
    echo "[ COMPILE ]   Compile $item.dll"
    x86_64-w64-mingw32-g++ -shared -o libraries/compiled/$item/$item.dll libraries/compiled/$item/$item.o
done

echo "[ INFO    ] Done!"
