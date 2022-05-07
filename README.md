# oiio_techcheck

A tool to check the image stats of an image or sequence of images.

It's intended as a python wrapper to the shell examples listed below.

## Usage
```shell
usage: oiio_techcheck_cli.py [-h] -d DIRPATH -o OUTPATH

Check for files of type: '.exr', '.tif', '.hdr', '.jpg', '.png'in input directory.
Detect stats with oiiotool and return original stats along with a summary of overall min/max and frame numbers of any nans or infs.
Save each detected sequence's stats as as a JSON file

optional arguments:
  -h, --help            show this help message and exit
  -d DIRPATH, --dirpath DIRPATH
                        Path to the directory to check for valid files
  -o OUTPATH, --outpath OUTPATH
                        Path to the output directory to save analysis
```

## Examples using oiiotool cli
Stats
```shell
oiiotool --stats ./PROJECTS/test_project/render/test_output_v001.exr
```
Stats Output
```shell
./PROJECTS/test_project/render/test_output_v001.exr : 2048 x 1556, 3 channel, half openexr
    Stats Min: -0.714355 -0.020981 -0.029449 (float)
    Stats Max: 8.734375 13.718750 9.304688 (float)
    Stats Avg: 0.199642 0.200939 0.145871 (float)
    Stats StdDev: 0.389372 0.458225 0.356934 (float)
    Stats NanCount: 0 0 0 
    Stats InfCount: 0 0 0 
    Stats FiniteCount: 3186688 3186688 3186688 
    Constant: No
    Monochrome: No
```

Hash
```shell
oiiotool --hash ./PROJECTS/test_project/render/test_output_v001.exr
```

Hash Output
```shell
./PROJECTS/test_project/render/test_output_v001.exr : 2048 x 1556, 3 channel, half openexr
    SHA-1: 4777E8AFB18508B932ADE95DA5C6BD6BAA021C21
```
