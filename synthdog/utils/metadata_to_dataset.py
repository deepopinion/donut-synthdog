"""Convert one or multiple metadata.jsonl files from SynthDoG to a AutoTransformers dataset file"""
import argparse
import os
import json
import jsonlines
import logging

from ocr_wrapper import BBox

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

parser = argparse.ArgumentParser()
parser.add_argument("input_folder", type=str, help="Path to the folder containing the synthetic images and metadata.jsonl files")

args = parser.parse_args()
logger.info("Converting folder %s", args.input_folder)
samples = {"train": [], "eval": [], "test": []}
for dirpath, _, filenames in os.walk(args.input_folder):
    logger.info("Processing subfolder %s", dirpath)
    if not "metadata.jsonl" in filenames:
        continue
    split = os.path.split(dirpath)[1]  # can be "train", "eval" or "test"
    if split == "validation":
        split = "eval"  # rename "validation" to "eval"
    # each folder with a metadata.jsonl file is added to the dataset
    with jsonlines.open(os.path.join(dirpath, "metadata.jsonl"), mode="r") as reader:
        for line in reader:
            doc = {}
            doc["image"] = os.path.relpath(os.path.join(dirpath, line["file_name"]), args.input_folder)
            logger.debug("Found %s", doc['image'])
            gt = json.loads(line["ground_truth"])["gt_parse"]
            words = bboxes = gt["words"]
            boxes = bboxes = gt["quads"]
            doc["bboxes"] = [BBox.from_easy_ocr_output(box_as_quads).to_dict() for box_as_quads in boxes]

            samples[split].append(doc)

with open(os.path.join(args.input_folder, "dataset.json"), mode="w") as f:
    json.dump(samples, f, indent=4)
