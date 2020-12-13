# Specifying python 3.
FROM python:3

# Setting up work directory.
WORKDIR /usr/src/app

# Copying all the files to the container.
COPY . .

# Running dependencies
RUN pip3 install --no-cache-dir -r requirements.txt
RUN pip3 install --no-cache-dir discord.py

# Running the app.
CMD ["python3", "main.py"]
