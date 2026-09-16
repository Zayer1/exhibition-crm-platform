FROM python:3.12-slim

WORKDIR /workspace

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the app code
COPY app /workspace/app
COPY data /workspace/data

# Expose port 3000
EXPOSE 3000

# Start the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "3000"]
