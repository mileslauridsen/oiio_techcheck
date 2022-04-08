# oiio_techcheck

A tool to check the image stats of an image or sequence of images

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

Metadata
```shell
oiiotool --info -v ./PROJECTS/test_project/render/test_output_v001.exr
```

Metadata Output
```shell
Reading ./PROJECTS/test_project/render/test_output_v001.exr
./PROJECTS/test_project/render/test_output_v001.exr : 2048 x 1556, 3 channel, half openexr
    channel list: R, G, B
    acesImageContainerFlag: 1
    chromaticities: 0.7347, 0.2653, 0, 1, 0.0001, -0.077, 0.32168, 0.33767
    compression: "none"
    nuke/full_layer_names: 0
    nuke/node_hash: "1a"
    nuke/version: "11.1v2"
    PixelAspectRatio: 1
    screenWindowCenter: 0, 0
    screenWindowWidth: 1
    version: 1
    oiio:ColorSpace: "Linear"
    oiio:subimages: 1
    smpte:TimeCode: 00:00:00:00
```
