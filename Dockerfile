FROM python:3.9-slim

# Install g++, make, and LLVM development libraries
RUN apt-get update && apt-get install -y g++ make llvm llvm-dev

WORKDIR /app
COPY . /app
RUN pip install --no-cache-dir -r requirements.txt

# Engine compile aagum
RUN cd compiler_engine && make

EXPOSE 5000
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "app:app"]
