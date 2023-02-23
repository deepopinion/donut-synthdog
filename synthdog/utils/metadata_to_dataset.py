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

# Add meta and config to dataset - it's static since the task is always the same
samples["meta"] =  {
        "name": "unknown",
        "version": "1.0.0",
        "created_with": "synthdog"
    }

samples["config"] = [
        {
            "ocr": "easyocr",
            "domain": "document",
            "type": "IDocument"
        },
        {
            "task_id": "dc_single",
            "classes": [
                "sparse",
                "text",
                "numbers",
            ],
            "type": "TSingleClassification"
        }
    ]

for dirpath, _, filenames in os.walk(args.input_folder):
    logger.info("Processing subfolder %s", dirpath)
    if not "metadata.jsonl" in filenames:
        continue
    rest, split = os.path.split(dirpath) # split can be "train", "eval" or "test"
    _, label = os.path.split(rest)  # label can be "sparse", "text", "numbers"
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
            quads = bboxes = gt["quads"]
            doc["bboxes"] = []
            for word, quad in zip(words, quads):
                box = BBox.from_easy_ocr_output(quad).to_normalized(1024, 1024*1.414) # convert to the normalized format so we can use it with LayoutLM
                box.text = word
                doc["bboxes"].append(box.to_dict())

            samples[split].append([doc, {"value": label}])

with open(os.path.join(args.input_folder, "dataset.json"), mode="w") as f:
    json.dump(samples, f, indent=4)
