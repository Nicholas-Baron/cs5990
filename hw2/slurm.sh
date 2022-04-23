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

sbatch << EOF
#!/bin/bash
#SBATCH --job-name=${input_filename%.*}
#SBATCH --ntasks=1
#SBATCH --output=${input_filename%.*}_out_%j.txt
#SBATCH --partition=compute

echo "Running $input_filename"

python ${input_filename}
EOF
