#!/bin/bash

# Move to data script directory
cd /modules

# Check if each file has data
for file in ../data/*
do
    if [[ -f $file ]]; then

        # Get data file size
        fileSize=$(stat -c%s "$file")

        # Get model from data file
        fileName=$(echo $file| cut -d'/' -f 6)
        model=$(echo $fileName| cut -d'_' -f 1)

        # Get site from data file
        fileName=$(echo $file| cut -d'_' -f 2)
        site=$(echo $fileName| cut -d'.' -f 1)

        # Check file size and get data if < 500 bytes
        if [[ $fileSize -gt 500 ]]; then
            echo $fileSize
        else
            python3.7 -c "import GetModelData; GetModelData.getData('$site', '$model', 5, 16)"
        fi

    fi
done