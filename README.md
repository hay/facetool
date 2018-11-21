# facetool
> Command line utility to manipulate faces in videos and images, written in Python 3

This library and command line tool is mostly a wrapper around well-known libraries and algorithms like `ffmpeg`, `dlib`, `opencv` and `face_recognition`.

## Installation

You'll need `git` and `pipenv` to run this tool.

1. Clone this repository
2. `pipenv install`
3. `pipenv shell`
4. Run your command

## Features

### Face swapping on images and video files

Put the features of face.jpg on head.jpg and save the result as swap.jpg

    facetool.py swap -i face.jpg -t head.jpg -o swap.jpg

Put the features of face.jpg on a video file called head.mp4 and save as swap.mp4

    facetool.py swap -i face.jpg -t head.mp4 -o swap.mp4

Put the features of a video file called face.mp4 on another video file called head.mp4 and save as swap.mp4

    facetool.py swap -i face.mp4 -t head.mp4 -o swap.mp4

Take one 'head' image called `head.jpg` and generate a new faceswap for every file in a directory called `dir-to-face`.

    facetool.py swap -i faces -t head.jpg -o dir-to-face

The other way around: apply the face of `face.jpg` to a directory of `heads` and output to a directory called `face-to-dir`

    facetool.py swap -i face.jpg -t heads -o face-to-dir

### Media utilites
Convert a movie file called `movie.mp4` to a set of JPG files in a directory called `frames` (used for video swapping)

    facetool.py extractframes -i movie.mp4 -o frames

Convert a set of JPG files from the directory `frames` to a movie file called `movie.mp4` (used for video swapping)

    facetool.py combineframes -i frames -o movie.mp4

Return metadata about an image or video file in JSON format

    facetool.py probe -i movie.mp4

## All options

    usage: facetool.py [-h] -i INPUT [-o OUTPUT] [-t TARGET] [-f FRAMERATE]
                       [-pp PREDICTOR_PATH] [-s] [-v] [-vv]
                       [{swap,extractframes,combineframes,probe}]

    positional arguments:
      {swap,extractframes,combineframes,probe}

    optional arguments:
      -h, --help            show this help message and exit
      -i INPUT, --input INPUT
      -o OUTPUT, --output OUTPUT
      -t TARGET, --target TARGET
      -f FRAMERATE, --framerate FRAMERATE
      -pp PREDICTOR_PATH, --predictor-path PREDICTOR_PATH
      -s, --swap            Swap input and target
      -v, --verbose
      -vv, --extra-verbose

## Credits
Written by [Hay Kranen](https://www.haykranen.nl).

### Faceswapping
Faceswapping algorithm by [Matthew Earl](http://matthewearl.github.io/2015/07/28/switching-eds-with-python/), licensed under the MIT license.

Copyright (c) 2015 Matthew Earl

## License
Licensed under the [MIT license](https://opensource.org/licenses/MIT).