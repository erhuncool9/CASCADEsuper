#!/bin/bash

WORKDIR="~/cacsade_dataset_extraction/extraction"

CSV_FILE="$WORKDIR/index.csv"
FAILED="$WORKDIR/failed.csv"

#rm $FAILED

while IFS=, read -r user_project commit nr name file inco
do	
    output_dir="$WORKDIR/dataset/java/$user_project/$commit/$nr"

	file=$(echo $file | sed 's/\r//')
	inco=$(echo "$inco" | sed 's/\r//')
	
	printf "%s" "$inco" > "$output_dir/inconsistency.txt"

done < $CSV_FILE
