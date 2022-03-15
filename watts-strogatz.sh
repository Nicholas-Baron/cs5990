#!/bin/bash
#SBATCH --job-name=watts-strogatz
#SBATCH --output=watts_out.txt
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --partition=compute
#SBATCH --mem-per-cpu=1500M
#SBATCH -c 16

srun python ./watts-strogatz.py < input.txt
