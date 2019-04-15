#!/bin/zsh

for file in `ls ../track` ;
do
    input=${file%.*}
    python track_util.py $input
done