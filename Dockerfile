# Use official Frappe docker image as base
FROM frappe/bench:latest

# Set working directory
WORKDIR /home/frappe/frappe-bench

# Copy the app
COPY --chown=frappe:frappe . apps/frappe_ai_form_builder

# Switch to frappe user
USER frappe

# Install dependencies
RUN cd apps/frappe_ai_form_builder && \
    pip3 install -r requirements.txt

# Expose port
EXPOSE 8000-8005 9000

# Start command
CMD ["bench", "start"]
