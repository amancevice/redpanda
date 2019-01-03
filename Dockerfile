FROM amancevice/pandas:0.23.4
RUN apk add --no-cache g++ && \
    pip3 install jupyter randomwords redpanda
ENV PYTHONPATH=/redpanda
VOLUME /redpanda
WORKDIR /redpanda/notebooks
EXPOSE 8888
CMD ["sh" , "-c", "jupyter notebook --ip=* --no-browser --allow-root --port 8888"]
