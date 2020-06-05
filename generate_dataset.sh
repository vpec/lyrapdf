#!/bin/bash

for dir in "$1"/*
do
    # Generate dataset for each directory
    snips-nlu generate-dataset es $dir/*.yml > $dir/dataset.json
done

