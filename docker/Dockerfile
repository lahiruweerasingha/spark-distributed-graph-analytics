# Spark 3.5.9 for the cluster roles, the jobs and the tests: one image, so the
# tests run against the same Spark and Python the cluster uses.
FROM apache/spark:3.5.9-java17-python3

USER root
RUN pip3 install --no-cache-dir pytest==9.1.1

ENV SPARK_HOME=/opt/spark \
    PYTHONPATH=/opt/spark/python:/opt/spark/python/lib/py4j-0.10.9.7-src.zip:/app/src \
    PYSPARK_PYTHON=python3

RUN mkdir -p /app /opt/spark-events && chown -R spark:spark /app /opt/spark-events
WORKDIR /app
USER spark
