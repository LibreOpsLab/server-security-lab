FROM python:3.14-alpine
RUN adduser -D -u 10001 app
USER app
WORKDIR /app
COPY app.py .
EXPOSE 8080
CMD ["python", "-u", "app.py"]
