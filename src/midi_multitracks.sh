#!/bin/zsh

for file in `ls ../midi` ;
do
    input=${file%.*}
    python midi_util.py $input
done