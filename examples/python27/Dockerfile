FROM amancevice/pandas:0.18.1
RUN apk add --no-cache g++
RUN pip install jupyter redpanda RandomWords
ENV PYTHONPATH=/redpanda
EXPOSE 2700
CMD jupyter notebook --ip=* --no-browser --port 2700
