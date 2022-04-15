#!/bin/bash
#SBATCH --job-name=watts-strogatz
#SBATCH --output=watts_out_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=50:00:00
#SBATCH --partition=compute
#SBATCH --mem-per-cpu=3500M
#SBATCH -c 16

python ./watts-strogatz.py < input-watts.txt
