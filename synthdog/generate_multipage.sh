#!/bin/bash

# One-line script to generate a SynthDog dataset with multiple types of docs
# in Autotransformers format.
cd ~/data/ocr/donut/synthdog
rm ~/data/autotransformers/.data/document/multipage_synthetic -r
synthtiger -o ~/data/autotransformers/.data/document/multipage_synthetic/text -c 20 -w 4 -v template.py SynthDoG config_en_clean.yml 
synthtiger -o ~/data/autotransformers/.data/document/multipage_synthetic/numbers -c 20 -w 4 -v template.py SynthDoG config_en_numbers.yml 
synthtiger -o ~/data/autotransformers/.data/document/multipage_synthetic/sparse -c 20 -w 4 -v template.py SynthDoG config_en_sparse.yml

python3 utils/metadata_to_dataset.py ~/data/autotransformers/.data/document/multipage_synthetic
