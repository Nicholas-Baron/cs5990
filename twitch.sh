#!/bin/bash
#SBATCH --job-name=twitch
#SBATCH --output=twitch_out_%j.txt
#SBATCH --ntasks=1
#SBATCH --time=10:00:00
#SBATCH --partition=compute
#SBATCH --mem-per-cpu=7000M
#SBATCH -c 16

python ./twitch-analytics.py
