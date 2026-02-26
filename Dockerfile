# Use a slim Python image for efficiency
FROM python:3.13-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the requirements file and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy all project files into the container
COPY . .

# Expose the port the load balancer runs on
EXPOSE 8080

# Command to run the application
CMD ["python", "main.py"]