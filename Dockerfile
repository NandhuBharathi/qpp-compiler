# Base image: Python + OS
FROM python:3.9-slim

# C++ Compiler (g++) matrum Make-ah install pandrom
RUN apt-get update && apt-get install -y g++ make

# Working directory setup
WORKDIR /app

# Namma repo files ellathaiyum Docker kulla copy pandrom
COPY . /app

# Python packages install pandrom (Flask, Gunicorn)
RUN pip install --no-cache-dir -r requirements.txt

# C++ Engine-ah compile pandrom
RUN cd compiler_engine && make

# Web server port
EXPOSE 5000

# Gunicorn vachi API-ah production mode-la run pandrom
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
