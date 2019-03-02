#!/bin/bash
END=8
for i in $(seq 1 $END); do

    declare -A pids

    echo "attempt ${i}"
    outdir="out/${i}"
    mkdir -p $outdir

    for j in $(seq 0 4); do
        echo "launching './main.py ${j} ${outdir}'"
        ./main.py $j $outdir &
         pids[${i}]=$!
    done

    for pid in ${pids[*]}; do
        echo "waiting for ${pid}"
        wait $pid
    done
    echo -e "\n---\n"
done