FROM amancevice/pandas:0.18.1
RUN apk add --no-cache g++
RUN pip install ipython[notebook] redpanda RandomWords
ENV PYTHONPATH=/redpanda
EXPOSE 2700
CMD ipython notebook --ip=* --no-browser --port 2700
