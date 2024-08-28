# Use the official Python image
FROM python:3.9-slim

# Set the working directory
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Expose ports for both applications
EXPOSE 8501 8502

# Start both applications using a shell command
CMD ["sh", "-c", "streamlit run chat.py --server.port 8501 & streamlit run embeddings.py --server.port 8502"]