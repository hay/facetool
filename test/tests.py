TESTS = [
    {
        "label" : "Show help",
        "command" : "-h"
    },
    {
        "label" : "Count faces (single image)",
        "command" : "count -i test/img-group/1.jpg -o test/output/count-single"
    },
    {
        "label" : "Crop faces (image)",
        "command" : "crop -i test/img-single/1.jpg -o test/output/crop-image"
    },
    {
        "label" : "Crop faces (directory)",
        "command" : "crop -i test/img-single -o test/output/crop-folder"
    },
    {
        "label" : "Locate faces (image)",
        "command" : "locate -i test/img-single/1.jpg"
    },
    {
        "label" : "Face distance (image to dir)",
        "command" : "distance -t test/img-recognize/obama -i test/img-recognize/trump/trump.jpg"
    },
    {
        "label" : "Pose face (image)",
        "command" : "pose -i test/img-single/1.jpg -o test/output/pose-image.jpg"
    },
    {
        "label" : "Probe image",
        "command" : "probe -i test/img-single/1.jpg"
    },
    {
        "label" : "Probe video",
        "command" : "probe -i test/video/1.mp4"
    },
    {
        "label" : "Swap image to image",
        "command" : "swap -i test/img-single/1.jpg -t test/img-single/3.jpg -o test/output/swap-image-to-image.jpg"
    },
    {
        "label" : "Swap image to dir",
        "command" : "swap -i test/img-single/1.jpg -t test/img-single -o test/output/swap-image-to-dir"
    },
    {
        "label" : "Swap dir to image",
        "command" : "swap -i test/img-single -t test/img-single/1.jpg -o test/output/swap-dir-to-image"
    },
    {
        "label" : "Swap dir to dir",
        "command" : "swap -i test/img-single -t test/img-single -o test/output/swap-dir-to-dir"
    },
    {
        "label" : "Swap group to group (faceswap)",
        "command" : "swap -i test/img-group/1.jpg -t test/img-group/1.jpg -o test/output/group-faceswap.jpg -so 1,0"
    },
    {
        "label" : "Swap single face to whole group",
        "command" : "swap -i test/img-single/1.jpg -t test/img-group/2.jpg -o test/output/single-to-goup.jpg -so 0 -sr"
    },
    {
        "label" : "Swap image to video",
        "command" : "swap -i test/img-single/1.jpg -t test/video/1.mp4 -o test/output/swap-image-to-video.mp4"
    },
    {
        "label" : "Swap video to video",
        "command" : "swap -i test/video/1.mp4 -t test/video/2.mp4 -o test/output/swap-video-to-video.mp4"
    },
    {
        "label" : "Classify faces",
        "command" : "classify -i test/img-single -of csv -o test/output/classify.csv"
    },
    {
        "label" : "Averaging faces",
        "command" : "average -i test/img-single -o test/output/avgface.jpg"
    }
];