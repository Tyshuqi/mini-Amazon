FROM python:3
ENV PYTHONUNBUFFERED 1
RUN mkdir /code
WORKDIR /code
ADD requirements.txt /code/
RUN pip install --upgrade pip
RUN pip install -r requirements.txt
ADD . /code/

# Adjust permissions for the product_image directory
RUN chmod -R 775 /code/product_image && \
    chown -R nobody:nogroup /code/product_image
    