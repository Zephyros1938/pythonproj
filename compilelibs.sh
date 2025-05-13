#!/bin/bash

LIBRARIES_DIR="libraries"                   # the directory where the libraries are located
COMPILED_DIR="$LIBRARIES_DIR/compiled"      # where the compiled libraries go
TO_COMPILE="stb_image test logger assimp"                 # what needs to be compiled - seperate with spaces
PURGE_LIBRARIES=1                           # removes all the compiled libraries before compilation
SHOW_TO_COMPILE=1                           # shows what needs to be compiled
SHOW_COMPILED=1                             # shows what was compiled
COMPILE_OSX=1                               # tells to compile windows dlls (reccommended)

if [ $PURGE_LIBRARIES == 1 ]; then
    rm -rf $COMPILED_DIR/*
    echo "[ INFO    ] Removed all compiled libraries."
fi

if [ $SHOW_TO_COMPILE == 1 ]; then
    echo "[ INFO    ] To Compile:"
    for item in $TO_COMPILE; do
        echo "[ INFO    ]  - $item"
    done
fi

for item in $TO_COMPILE; do
    echo "[ INFO    ] Compile $item"
    if [ ! -d "$COMPILED_DIR/$item" ]; then
        mkdir "$COMPILED_DIR/$item"
    fi

    echo "[ INFO    ]  Start compile Linux libraries"
    echo "[ COMPILE ]   Compile $item.a"
    g++ -c $LIBRARIES_DIR/$item.cpp -o $COMPILED_DIR/$item/$item.o -fPIC
    g++ -shared -o $COMPILED_DIR/$item/$item.so $COMPILED_DIR/$item/$item.o -lassimp
    if [ ! -f $COMPILED_DIR/$item/$item.o ]; then
        echo "[ ERROR   ] Failed to compile object file ($item.o)."
        exit 1
    fi
    objcopy -O elf64-x86-64 $COMPILED_DIR/$item/$item.o $COMPILED_DIR/$item/$item.a
    echo "[ COMPILE ]   Compile $item.so"

    if [ $COMPILE_OSX == 1 ]; then
        echo "[ INFO    ]  Start compile OSX libraries"
        echo "[ COMPILE ]   Compile $item.lib"
        x86_64-w64-mingw32-g++ -c $LIBRARIES_DIR/$item.cpp -o $COMPILED_DIR/$item/$item.o -fPIC
        if [ ! -f $COMPILED_DIR/$item/$item.o ]; then
            echo "[ ERROR   ] Failed to compile object file for Windows."
            exit 1
        fi
        ar rcs $COMPILED_DIR/$item/$item.lib $COMPILED_DIR/$item/$item.o
        echo "[ COMPILE ]   Compile $item.dll"
        x86_64-w64-mingw32-g++ -shared -o $COMPILED_DIR/$item/$item.dll $COMPILED_DIR/$item/$item.o -lassimp
    fi
done

print_tree() {
    local dir="$1"
    local prefix="$2"

    local entries=("$dir"/*)
    local count=${#entries[@]}
    local i=0

    for entry in "${entries[@]}"; do
        ((i++))
        local name="$(basename "$entry")"
        local connector="├──"
        if [ "$i" -eq "$count" ]; then
            connector="└──"
        fi
        echo "${prefix}${connector} ${name}"
        if [ -d "$entry" ]; then
            local new_prefix="${prefix}│   "
            if [ "$i" -eq "$count" ]; then
                new_prefix="${prefix}    "
            fi
            print_tree "$entry" "$new_prefix"
        fi
    done
}

if [ $SHOW_COMPILED == 1 ]; then
    TREE=$(echo "$COMPILED_DIR" && print_tree "$COMPILED_DIR" "")
    echo "$TREE"
fi

echo "[ INFO    ] Done!"
