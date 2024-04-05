# start by pulling the python image
FROM python:3.8

RUN apt update


# copy the requirements file into the image
COPY requirement.txt /app/requirement.txt

# switch working directory
WORKDIR /app

# install the dependencies and packages in the requirements file
RUN pip install -r requirement.txt

# copy every content from the local file to the image
COPY . /app

# configure the container to run in an executed manner
ENTRYPOINT [ "python" ]

CMD ["run.py"]