# Python Version
python-3.12

# Install dependencies
pip install -r requirements.txt

# Expose the port
EXPOSE 8501

# Start the application
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]