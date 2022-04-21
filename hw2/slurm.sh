#!/bin/bash

if [ $# -ne 1 ]; then
    echo "Usage: $0 <serial script to run>"
    exit
fi

input_filename=$1

if [ ! -x "$input_filename" ]; then
    echo "$input_filename is not executable"
    exit
fi

env input_filename="$input_filename" sbatch \
    --job-name="${input_filename%.*}" \
    --output="${input_filename%.*}_out_%j.txt" \
	sbatch.sh
