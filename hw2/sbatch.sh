#!/bin/bash
#SBATCH --ntasks=1
#SBATCH --partition=compute
#SBATCH -c 1

echo "Running $input_filename"

python ${input_filename}
