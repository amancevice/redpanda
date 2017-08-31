FROM amancevice/pandas:0.20.3-python3-alpine
RUN apk add --no-cache g++ && \
    pip3 install jupyter randomwords redpanda
ENV PYTHONPATH=/redpanda
VOLUME /notebooks \
       /redpanda
WORKDIR /notebooks
EXPOSE 3600
CMD ["sh" , "-c", "jupyter notebook --ip=* --no-browser --allow-root --port 3600"]
