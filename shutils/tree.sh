#!/bin/bash

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

target_dir="${1:-.}"

if [ ! -d "$target_dir" ]; then
    echo "Error: '$target_dir' is not a directory."
    exit 1
fi

echo "$target_dir"
print_tree "$target_dir" ""
