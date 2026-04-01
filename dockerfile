# Use an official Python runtime as a parent image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file from the app directory to the container
# This is located at app/requirements.txt in your repository 
COPY app/requirements.txt .

# Install any needed packages specified in requirements.txt
# This includes Flask and pytest 
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code from the local app directory
# This includes app.py and aceest_fitness.db 
COPY app/ .

# Make port 5000 available to the world outside this container
EXPOSE 5000

# Define environment variable for Flask
ENV FLASK_APP=app.py

# Run the application when the container launches
CMD ["python", "app.py"]