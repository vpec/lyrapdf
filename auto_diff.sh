#!/bin/bash
string1="_pre.md"
string2="_post.md"

file1=""
file2=""

for file in "$1"/*
do
    # Check if file is string1 or string2
    if [[ "$file" == *"$string1"* ]]
    then
        file1="$file"
    elif [[ "$file" == *"$string2"* ]]
    then
        file2="$file"
    fi
    # Check if both files have been detected and proceed to diff
    if [ -n "$file1" ] && [ -n "$file2" ]
    then
        echo "$file1"
        echo "$file2"
        diff "$file1" "$file2"
        echo ""
        # Reset values
        file1=""
        file2=""
    fi

done

