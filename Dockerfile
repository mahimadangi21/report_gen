FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file into the container
COPY requirements.txt .

# Install dependencies and textblob corpora
RUN pip install --no-cache-dir -r requirements.txt && \
    python -m textblob.download_corpora

# Copy the rest of the application code
COPY . .

# Hugging Face Spaces expose port 7860 by default
EXPOSE 7860
ENV PORT=7860

# Run the FastAPI server using Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
