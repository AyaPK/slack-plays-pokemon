FROM python:3.12

RUN pip install "poetry"

WORKDIR /app

COPY . .

RUN poetry install

CMD ["poetry", "run", "python", "src/main.py"]
