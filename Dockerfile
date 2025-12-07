# Use the existing working bench as base
FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    git \
    redis-server \
    mariadb-client \
    build-essential \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Create frappe user
RUN useradd -ms /bin/bash frappe

# Set working directory
WORKDIR /home/frappe/frappe-bench

# Copy the entire bench
COPY --chown=frappe:frappe ../../frappe-bench /home/frappe/frappe-bench

# Switch to frappe user
USER frappe

# Install Python dependencies
RUN pip install --upgrade pip && \
    pip install -r apps/frappe/requirements.txt && \
    pip install -r apps/frappe_ai_form_builder/requirements.txt

# Expose ports
EXPOSE 8000-8005 9000

# Start command
CMD ["bench", "start"]
