# COCO-Visualizer

![](video_example.mp4)

A simple visualization library for the COCO dataset format.

Only supports bounding boxes for now.

https://cocodataset.org/#home

Requires annotations in json format in the current directory, along with the reference images.

`poetry run python main.py --json-path annotations.json --dest-dir out`

ffmpeg -framerate 15 -pattern_type glob -i '*.jpg' -r 15 -vf scale=512:-1 out.gif
