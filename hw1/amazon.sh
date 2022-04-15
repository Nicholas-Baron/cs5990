#!/bin/bash
#SBATCH --job-name=amazon
#SBATCH --output=amazon_out_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH --partition=compute
#SBATCH --mem-per-cpu=3500M
#SBATCH -c 16

python ./amazon-analytics.py
