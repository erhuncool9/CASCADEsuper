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
	
	mkdir -p $output_dir

	git clone https://github.com/${user_project}.git $output_dir/repo
	
	printf "%s" "$inco" > "$output_dir/inconsistency.txt"

	cd $output_dir/repo
	git checkout $commit
	
	~/venvs/cascade.venv/bin/CASCADE run -i $output_dir/repo -o $output_dir -s "$WORKDIR/con-datasetcollection.json" -filter "(0,content:$name)" -filter "(1,content:$file)"

	if [ ! -f "$output_dir/analyzed.json" ]
	then
		echo "-----------no analyzed file-------------------"
		echo "$user_project,$commit,$nr,err" >> $FAILED
	else
		chars=$(wc -m < $output_dir/analyzed.json)
		echo "$chars -----------------------"

		if [ -z "$chars" ]
		then
			echo "$user_project,$commit,$nr,err" >> $FAILED
		else	
			if [ "$chars" -lt 10 ]
			then
				echo "$user_project,$commit,$nr,filter" >> $FAILED
			fi
		fi
	fi

	cd $WORKDIR
	rm $output_dir/extracted.json
	rm -rf $output_dir/repo

done < $CSV_FILE
