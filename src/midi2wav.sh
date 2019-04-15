#!/bin/zsh

for file in `ls ../track` ;
do
    input=${file%.*}
    # 这里有一些输入参数得调整下
    # 不然采样率过高,数据太大
    timidity ../track/$file -Ow -o ../wav/${input}.wav 
done