import click
import json
import os
import random

from dataclasses import dataclass, field
from dataclasses_json import config, dataclass_json
from PIL import Image, ImageColor, ImageDraw
from typing import Dict, List

# Primary colors for default color map
BASE_COLORS = [
    "#0000FF",
    "#FF0000",
    "#FFFF00",
    "#FF6600",
    "#00FF00",
    "#6600FF",
    "#000000",
    "#FFFFFF",
]


@dataclass_json
@dataclass
class Category:
    id: int
    name: str


@dataclass_json
@dataclass
class Annotation:
    id: int
    image_id: int
    category_id: int
    segmentation: List[str]
    bbox: List[int]  # Like: [x y width height]
    ignore: int  # FIXME Boolean value as int
    iscrowd: int  # FIXME Boolean value as int
    area: int


@dataclass_json
@dataclass
class COCOImage:
    id: int
    width: int
    height: int
    file_name: str


@dataclass_json
@dataclass
class Info:
    year: int
    version: str
    contributor: str


@dataclass_json
@dataclass
class Dataset:
    annotations: List[Annotation]
    categories: List[Category]
    images: List[COCOImage]
    info: Info


def get_default_color_map(ds: Dataset) -> Dict[int, str]:
    """
    Get a default color map. If it's only a few categories, use primary colors,
    otherwise, generate a random color for each category.
    """
    if len(ds.categories) <= len(BASE_COLORS):
        ids = [c.id for c in ds.categories]
        return dict(zip(ids, BASE_COLORS))
    else:
        color_map = {}
        for category in ds.categories:
            # Get a random color value as a hex
            color_map[category.id] = "%06x" % random.randint(0, 0xFFFFFF)
        return color_map


def annotate_and_write(
    ds: Dataset, color_map: Dict[int, str], dest_dir: str, labels=False
):
    """
    Draw an annotation for each image on the dataset. TODO Optionally draw a label.

    Save the image under dest_dir
    """
    for i in ds.images:
        img = Image.open(i.file_name)
        img.putalpha(255)
        overlay = Image.new("RGBA", img.size, (255, 255, 255, 0))
        draw = ImageDraw.Draw(overlay)
        stripped_file_name = i.file_name.split("/")[1]
        for annotation in ds.annotations:
            if annotation.image_id == i.id:
                formatted_bbox = [
                    annotation.bbox[0],
                    annotation.bbox[1],
                    annotation.bbox[0] + annotation.bbox[2],
                    annotation.bbox[1] + annotation.bbox[3],
                ]
                color = ImageColor.getcolor(
                    color_map[annotation.category_id], mode="RGB"
                )
                draw.rectangle(
                    formatted_bbox,
                    fill=color + (50,),
                    outline=color,
                    width=3,
                )
        save_img = Image.alpha_composite(img, overlay).convert("RGB")
        save_img.save(f"{os.getcwd()}/{dest_dir}/{stripped_file_name}")


@click.command()
@click.option("--json-path", required=True)
@click.option("--dest-dir", required=True)
@click.option("--show-labels", is_flag=True)
@click.option(
    "--color-map",
    default=None,
    help='A user defined color map for categories as a json string like {"category_a": "#00BEEF"}',
)
def run(json_path, dest_dir, show_labels, color_map):
    with open(json_path, "r") as f:
        ds: Dataset = Dataset.from_dict(json.load(f))

    # Make the dest_dir
    os.makedirs(f"{os.getcwd()}/{dest_dir}", exist_ok=True)

    if color_map is None:
        color_map = get_default_color_map(ds)
    elif len(color_map) != len(ds.categories):
        raise RuntimeError(
            "User defined color map has the incorrect number of fields based on available categories"
        )

    annotate_and_write(ds, color_map, dest_dir=dest_dir, labels=show_labels)


if __name__ == "__main__":
    run()
