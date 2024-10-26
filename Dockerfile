# Start with a base Python image
FROM python:3.12

# Install Poetry
RUN pip install "poetry"

# Set the working directory
WORKDIR /app

# Copy the rest of the application code
COPY . .

# Install dependencies
RUN poetry install

# Define the default command to run your app
CMD ["poetry", "run", "python", "src/main.py"]
