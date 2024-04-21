#!/bin/bash
python3 manage.py makemigrations
python3 manage.py migrate
if [ -d "./product_image" ]; then
    chmod -R 775 ./product_image
else
    echo "Directory not found: ./product_image"
fi

res="$?"
while [ "$res" != "0" ]
do
    sleep 1;
    python3 manage.py migrate
    res="$?"
done

