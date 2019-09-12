#!/bin/bash

python3 ./find_orphan_pages.py > /tmp/wiki.txt
python3 ./get_pages_wo_cat.py >> /tmp/wiki.txt
python3 ./get_pages_wo_int.py >> /tmp/wiki.txt
python3 ./get_pages_wo_links.py >> /tmp/wiki.txt
