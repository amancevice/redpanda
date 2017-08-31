FROM amancevice/pandas:0.20.3-python2-alpine
RUN apk add --no-cache g++ && \
    pip install jupyter randomwords redpanda
ENV PYTHONPATH=/redpanda
VOLUME /notebooks \
       /redpanda
WORKDIR /notebooks
EXPOSE 2700
CMD ["sh" , "-c", "jupyter notebook --ip=* --no-browser --allow-root --port 2700"]
