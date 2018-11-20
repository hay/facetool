# facetool
> Command line utility to manipulate faces in videos and images, written in Python 3

This library and command line tool is mostly a wrapper around well-known libraries and algorithms like `ffmpeg`, `dlib`, `opencv` and `face_recognition`.

## Installation

You'll need `git` and `pipenv` to run this tool.

1. Clone this repository
2. `pipenv install`
3. `pipenv shell`
4. Run your command

## Examples

Put the features of face.jpg on head.jpg and save the result as swap.jpg

    facetool swap -i face.jpg -t head.jpg -o swap.jpg

Put the features of face.jpg on a video file called head.mp4 and save as swap.mp4

    facetool swap -i face.jpg -t head.mp4 -o swap.mp4

Put the features of a video file called face.mp4 on another video file called head.mp4 and save as swap.mp4

    facetool swap -i face.mp4 -t head.mp4 -o swap.mp4

### Utility commands
Convert a movie file called `movie.mp4` to a set of JPG files in a directory called `frames` (used for video swapping)

    facetool extractframes -i movie.mp4 -o frames

Convert a set of JPG files from the directory `frames` to a movie file called `movie.mp4` (used for video swapping)

    facetool combineframes -i frames -o movie.mp4

Return metadata about an image or video file in JSON format

    facetool probe -i movie.mp4