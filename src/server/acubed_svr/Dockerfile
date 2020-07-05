# Use official Python version 3.8 ans the runtime image
FROM python:3.8

# EXPOSE indicates the port number the container will listen for connections
# 5000 is the FLASK default
EXPOSE 5000

# Sets the working directory for the COPY and CMD instructions
WORKDIR /acubed_svr

ENV FLASK_APP acubed_server.py
ENV FLASK_RUN_HOST 0.0.0.0

# Install all the needed packages specified in the requirements.txt
COPY ./ /acubed_svr
RUN pip3 install -r requirementsSV.txt
RUN chmod +x boot.sh
ENTRYPOINT ["./boot.sh"]

