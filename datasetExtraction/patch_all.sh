#!/bin/bash

SECONDS=0

unzip dataset_junit.zip

WORKING_DIR=$(pwd)

DRIVERS_LIST=()
#DRIVERS_LIST=("DocChecker" "Baseline")
#DRIVERS_LIST=("CASCADE")


(
cd java
for repo in */*
do
(
	echo "At repository: $repo ---------------------"
	cd "$repo"
	# clone this repo 
	git clone https://github.com/$repo ./repository
	
	for commit in *
	do
	
		if [ $commit == "repository" ]
		then continue
		fi

	(
		echo "    At commit: $commit -------"
		
		# checkout specific commit
		(cd repository; git checkout $commit)
		cd "$commit"
		cp -r "../repository" "./backup"
		cp -r "../repository" "./repository"
		(
			cd backup
			mvn test
			pwd
			read
			mvn clean
		)


		#create patch		
		diff -urN --exclude=.git repository backup > file.patch

		rm -rf ./backup ./repository
	)				
	done
	rm -rf ./repository
)
done
(cd; cd "CASCADE"; git rev-parse HEAD >> $WORKING_DIR/runs; date >> $WORKING_DIR/runs;  echo >> $WORKING_DIR/runs)
)

printf 'Finished in %d h %02d m %02d s\n' $((SECONDS/3600)) $(((SECONDS/60)%60)) $((SECONDS%60))
