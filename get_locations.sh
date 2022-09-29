#!/bin/bash

start_date="2022-09-01 00"
end_date="2022-10-01 00"
frequency="6hour"

mkdir location_files
while [[ $(date -d "$start_date" "+%Y%m%d%H") -le $(date -d "$end_date" "+%Y%m%d%H") ]]; do
    echo $(date -d "$start_date" "+%Y%m%d%H")

    day=$(date -d "$start_date" "+%Y%m%d")
    hour=$(date -d "$start_date" "+%H")
    echo "reading" prepbufr_files/${day}${hour}/gdas.t${hour}z.prepbufr.nr
    ./prepbufr_decode_locations.exe prepbufr_files/${day}${hour}/gdas.t${hour}z.prepbufr.nr > location_files/locations.${day}${hour}.txt

    start_date=$(date -d "$start_date+$frequency" "+%Y-%m-%d %H")
done
