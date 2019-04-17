#!/bin/zsh

for file in `ls ../track` ;
do
    python standarlize_track.py $file 
done