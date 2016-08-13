FROM amancevice/pandas:0.18.1-python3
RUN apk add --no-cache g++
RUN pip3 install ipython[notebook] redpanda RandomWords
ENV PYTHONPATH=/redpanda
EXPOSE 3500
CMD ipython notebook --ip=* --no-browser --port 3500
