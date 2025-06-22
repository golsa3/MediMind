# Use a slim Python base
FROM python:3.10-slim

# Install required system packages (including wkhtmltopdf)
RUN apt-get update && apt-get install -y \
    build-essential \
    libssl-dev \
    libffi-dev \
    libxml2-dev \
    libxslt1-dev \
    zlib1g-dev \
    libjpeg-dev \
    libglib2.0-0 \
    libgdk-pixbuf2.0-0 \
    libpango-1.0-0 \
    libpangocairo-1.0-0 \
    libfontconfig1 \
    libxrender1 \
    xfonts-base \
    xfonts-75dpi \
    wkhtmltopdf \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Set work directory
WORKDIR /app

# Copy everything
COPY . /app

# Install Python dependencies
RUN pip install --upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Allow external access
EXPOSE 8080

# Set environment variables for Streamlit
ENV PORT 8080
ENV PLACES_API_KEY=AIzaSyBu9SE9h_9p2DupRvJBuKV3p3KveOcn6QQ

# Run Streamlit app
CMD ["streamlit", "run", "streamlit_app.py", "--server.port=8080", "--server.address=0.0.0.0"]
