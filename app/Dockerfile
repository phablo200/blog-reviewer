FROM python:3.12.3

WORKDIR /code

RUN apt-get update && apt-get install -y \
    build-essential \
    libffi-dev \
    python3-venv \
    && rm -rf /var/lib/apt/lists/*

COPY ./requirements.txt /code/requirements.txt
RUN pip install -r requirements.txt

COPY . /code

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "80"]