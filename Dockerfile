# Stage 1: build
# Start with a python image that includes python:3
FROM python:3

# Stage 2: intall python-telegram-bot and requests
RUN pip install python-telegram-bot --upgrade
RUN pip install requests
COPY . .

# Command to run the application
CMD [ "python", "./configbot.py" ]
