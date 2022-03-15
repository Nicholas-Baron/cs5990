#!/bin/bash
#SBATCH --job-name=watts-strogatz
#SBATCH --output=watts_out.txt
#SBATCH --ntasks=1
#SBATCH --time=1:00:00
#SBATCH --mem-per-cpu=500M

srun python ./watts-strogatz.py < input.txt
