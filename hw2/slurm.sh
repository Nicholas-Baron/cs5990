#!/bin/bash

if [ $# -lt 1 ] || [ $# -gt 2 ]; then
    echo "Usage: $0 <serial script to run> [num jobs]"
    exit
fi

input_filename=$1

if [ ! -x "$input_filename" ]; then
    echo "$input_filename is not executable"
    exit
fi

num_jobs=1

if [ $# -eq 2 ]; then
    num_jobs=$2
    if [ $num_jobs -lt 2 ]; then
        echo "Number of jobs should be above 2. Found $num_jobs"
        exit
    fi
fi

echo "Running $input_filename on $num_jobs jobs"

sbatch << EOF
#!/bin/bash
#SBATCH --job-name=${input_filename%.*}
#SBATCH --ntasks=$num_jobs
#SBATCH --output=${input_filename%.*}_out_%j.txt
#SBATCH --partition=compute

echo "Running $input_filename on $num_jobs jobs"

python ${input_filename}
EOF

squeue