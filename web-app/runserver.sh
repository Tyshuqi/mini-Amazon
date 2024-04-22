#!/bin/bash
python3 manage.py makemigrations
python3 manage.py migrate
python3 startDB.py
echo "Running as user: $(whoami)"
if [ -d "./product_image" ]; then
    chmod -R 775 ./product_image
else
    echo "Directory not found: ./product_image"
fi
while [ "1"=="1" ]
do
    python3 manage.py runserver 0.0.0.0:8000
    sleep 1
done
