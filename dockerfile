FROM python:3.11-buster

# Update the image
RUN apt-get update && apt-get upgrade -y 

# Update the image
RUN apt-get update 

# Select the application working directory
WORKDIR /usr/src/app

# Update python tools OLD WAY
RUN pip install --upgrade pip
# RUN pip install -U wheel setuptools cpython
# Add the project to the WORKDIR
COPY . .

# --without dev

RUN pip install -r requirements.txt -U 

# Clean up APT when done.
RUN apt-get autoremove -y && apt-get clean && rm -rf /var/lib/apt/lists/* /tmp/* /var/tmp/*

# Finally run the container
CMD ["uvicorn", "src.main_backend:app", "--host", "0.0.0.0", "--port", "8000","--workers" ,"4"]
