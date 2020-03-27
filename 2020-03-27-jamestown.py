#! /usr/bin/env python3
#
# 2020-03-27 
# Colton Grainger 
# CC-0 Public Domain

"""
Python script to download USS Jamestown Logs
"""

# Where to download the images and metadata?
# Default: present working directory.
data = "."

# Where is the slice of Kevin Wood's NARA roster with Jamestown images?
# Default: present working directory, see email.
csv = "2020-03-27-NARA_Jamestown_records.csv"

##

import pandas as pd
df = pd.read_csv(csv)

##

import logging
import http.client
http.client.HTTPConnection.debuglevel = 1
logging.basicConfig()
logging.getLogger().setLevel(logging.DEBUG)
requests_log = logging.getLogger("requests.packages.urllib3")
requests_log.setLevel(logging.DEBUG)
requests_log.propagate = True

##

import requests
api_base = 'https://catalog.archives.gov/api/v1/'

for nara_id in map(lambda s : s.split('/')[-1], df['NARA URL']):

    api_url = f'{api_base}?naIds={nara_id}'
    res = requests.get(api_url)

    # parse NARA API output for metadata
    entry_img_array = res.json().get('opaResponse').get('results').get('result')[0].get('objects').get('object')
    digital_directory = entry_img_array[0].get('file').get('@path').split("/")[-2]

    # write NARA API output to file for reference
    api_output = f"{data}/nara_id_{nara_id}.json"
    if res.status_code == 200:
        with open(api_output, 'wb') as f:
            f.write(res.content)

    # download images
    for img_info in entry_img_array: 

        # test for mimetype "image/jpeg"
        # we don't want "application/pdf"
        if img_info.get('file').get('@mime') == "image/jpeg":

            img_name = img_info.get('file').get('@name')
            img_url = img_info.get('file').get('@url')
            img_res = requests.get(img_url)

            # write a single image to file
            local_img_name = "{0}/{1}".format(data, img_name)
            if img_res.status_code == 200:
                with open(local_img_name, 'wb') as img_f:
                    img_f.write(img_res.content)
