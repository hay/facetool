# facetool.py
> Command line utility to manipulate, recognize and detect faces in videos and images, written in Python 3

![Facetool header logo](data/header.gif)

This utility allows you to do all kinds of operations on face images and videos, straight from the command line. Think of it as `ffmpeg` for faces.

Some things `facetool` can do:
* Face swapping
* Face recognition
* Create an average face
* Counting faces
* Cropping faces (even multiple ones from a single image)
* Extracting and combining frames from and to videos
* Classifying faces based on age and gender

## Installation
In theory, this tool should work on any system that can run the required libraries (`dlib`, `opencv` and a couple of other ones), but in practice i've only tested it on MacOS.

### macOS
I highly recommend using [`brew`](https://brew.sh/) to install all dependencies. You'll also need a working version of Python 3.6 or higher.

You can either use [`pipenv`](https://pipenv.readthedocs.io/en/latest/install/#installing-pipenv) (installable with `brew`) or install the required libraries globally using `pip`.

Given that you have Python 3.6 on your system this should be enough:

Clone this repository:
```bash
    git clone https://github.com/hay/facetool.git
```
Install dependencies using `brew`:
```bash
    brew install cmake ffmpeg pipenv
```

*When using `pipenv` (recommended)*

Run `pipenv install` in the root folder of tthe checked out folder. This might take a while! Then run `pipenv shell`.

*When using globally installed libraries*

`pip3 install dlib numpy opencv-python ffmpeg-python scikit-image tqdm imutils tensorflow pandas face-recognition`

After installing the libraries (either with or without `pipenv`) try running the script by typing `./facetool.py`.

If that all works you can try some of the commands below.

## Examples

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

### Face recognition

Calculate the distance between 'alice.jpg' and a folder full of faces

    facetool.py distance -i alice.jpg -t faces

The same, but then print percentages instead of distance

    facetool.py distance -i alice.jpg -t faces --as-percentage

Save the results to a CSV file instead of printing to the command line

    facetool.py distance -i alice.jpg -t faces --as-percentage -of csv -o results.csv

Encode a path of images and save the encodings to a file called `encodings.json`

    facetool.py encode -i faces -o encodings.json

Use the `encodings.json` file instead of recalculating all the encodings. Note the `-m` (model) switch.

    facetool.py distance -i alice.jpg -m encodings.json

### Face averaging

Create an 'average.jpg' face from a folder of faces

    facetool.py average -i faces -o average.jpg

Do the same thing from a single image that has multiple faces

    facetool.py average -i group.jpg -o average.jpg

Save 'original' and 'transformed' averaged faces as well

    facetool.py average -i faces -o average.jpg --save-originals --save-warped

### Classifying age and gender

Get the age and gender of a single image and print to console

    facetool.py classify -i face.jpg

Get the age and gender of all images in a folder and write to a csv file

    facetool.py classify -i faces/ -of csv -o classified.csv

### Face detection, position and cropping

Count the number of faces in `face.jpg`

    facetool.py count -i face.jpg

Count the number of faces in all images in directory `faces`

    facetool.py count -i faces

Show the bounding box of all faces in `face.jpg`

    facetool.py locate -i face.jpg

Create a new image called `face-box.jpg` that draws bounding boxes around all faces in `face.jpg`

    facetool.py locate -i face.jpg -o face.box.jpg

Draw bounding boxes on all faces for all images in directory `faces` and save to `locations`

    facetool.py locate -i faces -o locations

Show the poses of all faces in `face.jpg`

    facetool.py pose -i face.jpg

Create a new image called `face-pose.jpg` that shows the shapes and poses of `face.jpg`

    facetool.py pose -i face.jpg -o face-pose.jpg

Crop all faces from `face.jpg` and save to new files in the directory `cropped`. This will also work with a single image with multiple faces.

    facetool.py crop -i face.jpg -o cropped

### Media utilites
Convert a movie file called `movie.mp4` to a set of JPG files in a directory called `frames` (used for video swapping)

    facetool.py extractframes -i movie.mp4 -o frames

Convert a set of JPG files from the directory `frames` to a movie file called `movie.mp4` (used for video swapping)

    facetool.py combineframes -i frames -o movie.mp4

Return metadata about an image or video file in JSON format

    facetool.py probe -i movie.mp4

## Troubleshooting
* Before opening an issue, try running your command with the `-v` (verbose) switch, because this will give you more debug information. When using `-vv` (extra verbose) `facetool` will abort the program on exceptions.
* Note that, by default, facetool doesn't stop at errors.
* Documentation might be a bit lacking at times. I try to at least provide one image for every command line switch and option.

## All options
You'll get this output when running `facetool.py -h`.

```bash
usage: facetool.py [-h] -i INPUT [-o OUTPUT] [-t TARGET] [--as-percentage]
                   [-bl BLUR] [-dd DATA_DIRECTORY] [-fr FRAMERATE]
                   [-fa FEATHER] [-ih IMAGE_HEIGHT] [-iw IMAGE_WIDTH] [-kt]
                   [-m MODEL] [--no-eyesbrows] [--no-nosemouth]
                   [-of {default,csv,json}] [-pp PREDICTOR_PATH] [--profile]
                   [-s] [--save-originals] [--save-warped] [-v] [-vv]
                   [{average,classify,combineframes,count,distance,crop,encode,extractframes,landmarks,locate,pose,probe,swap}]

Manipulate faces in videos and images

positional arguments:
  {average,classify,combineframes,count,distance,crop,encode,extractframes,landmarks,locate,pose,probe,swap}

optional arguments:
  -h, --help            show this help message and exit
  -i INPUT, --input INPUT
                        Input file or folder, 'face' when swapping
  -o OUTPUT, --output OUTPUT
                        Output file or folder
  -t TARGET, --target TARGET
                        'Head' when swapping
  --as-percentage       Show face distances as percentages
  -bl BLUR, --blur BLUR
                        Amount of blur to use during colour correction
  -dd DATA_DIRECTORY, --data-directory DATA_DIRECTORY
                        Directory where the data files are located
  -fr FRAMERATE, --framerate FRAMERATE
  -fa FEATHER, --feather FEATHER
                        Softness of edges on a swapped face
  -ih IMAGE_HEIGHT, --image-height IMAGE_HEIGHT
                        Height of output image / height
  -iw IMAGE_WIDTH, --image-width IMAGE_WIDTH
                        Width of output image / video
  -kt, --keep-temp      Keep temporary files (used with video swapping
  -m MODEL, --model MODEL
                        Use a precalculated model (for calculating distances)
  --no-eyesbrows
  --no-nosemouth
  -of {default,csv,json}, --output-format {default,csv,json}
                        Specify output format
  -pp PREDICTOR_PATH, --predictor-path PREDICTOR_PATH
  --profile             Show profiler information
  -s, --swap            Swap input and target
  --save-originals      Save original images when averaging faces
  --save-warped         Save warped images when averaging faces
  -v, --verbose         Show debug information
  -vv, --extra-verbose  Show debug information AND raise / abort on exceptions
```

## Limitations
* Face swapping is limited to one face.
* More advanced swapping methods like 'deepfake' are not supported.
* Even though you could use the library in your own scripts (instead of using the command line utility), this isn't very well supported yet.
* No multithreading / processor support.
* Operations on videos will remove the audio.

## Testing
`facetool` doesn't have a proper test suite yet, but you could try running `test-all.sh` in the `test` directory to try a couple of common examples.

## License
Licensed under the [MIT license](https://opensource.org/licenses/MIT).

## Credits
Written by [Hay Kranen](https://www.haykranen.nl).

This utility is built around well-known libraries like `dlib`, `face_recognition` and `opencv`.

### Faceswapping
Faceswapping algorithm by [Matthew Earl](http://matthewearl.github.io/2015/07/28/switching-eds-with-python/), licensed under the MIT license.

Copyright (c) 2015 Matthew Earl

### Age and gender classifier
Age and gender classifier by [Boyuan Jiang](https://github.com/BoyuanJiang/Age-Gender-Estimate-TF), licensed under the MIT license.

Copyright (c) 2017 Boyuan
