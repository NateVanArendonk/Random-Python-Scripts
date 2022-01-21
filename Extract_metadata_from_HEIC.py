import exifread
from pathlib import Path

# Fxns to extract metadata from HEIC files
def get_exif_data(ifile, kill_list):
    f = open(ifile, 'rb')
    tags = exifread.process_file(f, details=False)
    date = str(tags.get("EXIF DateTimeOriginal"))
    lon = convert_to_string(str(tags.get("GPS GPSLongitude")))
    lat = convert_to_string(str(tags.get("GPS GPSLatitude")))
    tzone = str(tags.get("EXIF OffsetTime"))

    # Remove characters from the coordinates
    for k in kill_list:
        lon = [s.replace(k, '') for s in lon]
        lat = [s.replace(k, '') for s in lat]

    # Get lat lon in decimal degrees
    lon = convert_to_decimal_degrees(lon)
    lat = convert_to_decimal_degrees(lat)
    return date, lat, lon, tags, tzone


def convert_to_string(string):
    li = list(string.split(","))
    return li


def split_at_division(string):
    split = string.split("/")
    return split


def convert_to_decimal_degrees(lst):
    if '/' in lst[2]:
        sec = split_at_division(lst[2])
        sec = (int(sec[0]) / int(sec[1])) / 3600
    else:
        sec = int(lst[2]) / 3600
    minute = int(lst[1]) / 60
    ms = minute + sec
    dec_deg = int(lst[0]) + ms
    return dec_deg


# Code to metadata from folder of HEIC photos
kill_list = ['[', ']', ' ', ':', '.']
photoFolder = 'BellinghamBay_Sampling_Jan2022/'
header = ['Image', ' DateTime', ' GMT Offset', ' Latitude', ' Longitude']
with open('metadata.csv', 'w') as csvfile:
    csvfile.write(','.join(header) + '\n')
    # Loop and extract metadata from all HEIC files in the directory
    for file in Path(photoFolder).rglob('*.HEIC'):
        if file.is_file():
            date, lat, lon, tags, tzone = get_exif_data(str(file), kill_list)
            print(tzone)
            # Write to CSV file
            csvfile.write(str(file.name) + ', ' + str(date) + ', ' + str(tzone) + ', ' + str(lat) + ', ' + str(lon) + '\n')


