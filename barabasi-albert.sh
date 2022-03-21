#!/bin/bash
#SBATCH --job-name=barabasi-albert
#SBATCH --output=barabasi_out_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=50:00:00
#SBATCH --partition=compute
#SBATCH --mem-per-cpu=3500M
#SBATCH -c 16

python ./barabasi-albert.py < input-barabasi.txt
