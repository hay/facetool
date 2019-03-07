#!/bin/bash

cd ../

rm -rf test/output/*

exec() {
    printf "\n"
    echo "***"
    echo $1
    echo "***"
    printf "\n"
    cmd="./facetool.py $2 -vv"
    echo $cmd
    eval $cmd

    if [ $? != 0 ];then
        exit
    fi
}

exec "Show help" "-h"

exec "Count faces (single image)" "count -i test/img-group/1.jpg -o test/output/count-single"

exec "Crop faces (image)" "crop -i test/img-single/1.jpg -o test/output/crop-image.jpg"

exec "Crop faces (directory)" "crop -i test/img-single -o test/output/crop-folder"

exec "Locate faces (image)" "locate -i test/img-single/1.jpg"

exec "Face distance (image to dir)" "distance -i test/img-recognize/obama -t test/img-recognize/trump/trump.jpg"

exec "Pose face (image)" "pose -i test/img-single/1.jpg -o test/output/pose-image.jpg"

exec "Probe image" "probe -i test/img-single/1.jpg"

exec "Probe video" "probe -i test/video/1.mp4"

exec "Swap: image to image" "swap -i test/img-single/1.jpg -t test/img-single/3.jpg -o test/output/swap-image-to-image.jpg"

exec "Swap: image to dir" "swap -i test/img-single/1.jpg -t test/img-single -o test/output/swap-image-to-dir"

exec "Swap dir to image" "swap -i test/img-single -t test/img-single/1.jpg -o test/output/swap-dir-to-image"

exec "Swap dir to dir" "swap -i test/img-single -t test/img-single -o test/output/swap-dir-to-dir"

exec "Swap image to video" "swap -i test/img-single/1.jpg -t test/video/1.mp4 -o test/output/swap-image-to-video.mp4"

exec "Swap video to video" "swap -i test/video/1.mp4 -t test/video/2.mp4 -o test/output/swap-video-to-video.mp4"

exec "Classify faces" "classify -i test/img-single -of csv -o test/output/classify.csv"

exec "Averaging faces" "average -i test/img-single -o test/output/avgface.jpg"