#!/bin/sh
mkdir $1
mysqldump --all-databases -u root -p > $1/$1.sql

echo "sql dump finished, copying pictures"

cp -r /home/sol315/pictures ./$1/
echo "Archive finished. Files are stored in" $1
