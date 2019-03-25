from python:3.7-alpine3.8
RUN apk add --no-cache gcc musl-dev
COPY . /app
RUN cd /app && \
        pip install -e .[tests]
