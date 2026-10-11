# In-degree analysis of a 7.6M-edge web graph on a Spark cluster.
# `make help` lists the targets.

COMPOSE := docker compose
EXEC := $(COMPOSE) exec -T
RUNNER := $(COMPOSE) run --rm --no-deps runner
BENCHMARK_REPEATS ?= 3

# Git Bash on Windows rewrites container paths such as /opt/spark/... into
# Windows paths before Docker sees them. This switches that off; it has no
# effect on Linux or macOS.
export MSYS_NO_PATHCONV := 1

# Jobs are submitted from the master container, so executors can reach the
# driver. 2 cores / 1g per executor = one executor per 2-core worker.
SPARK_SUBMIT := /opt/spark/bin/spark-submit \
	--master spark://spark-master:7077 \
	--conf spark.eventLog.enabled=true \
	--conf spark.eventLog.dir=file:/opt/spark-events \
	--conf spark.sql.adaptive.enabled=true \
	--conf spark.sql.shuffle.partitions=16 \
	--executor-cores 2 \
	--executor-memory 1g \
	--total-executor-cores 4 \
	--driver-memory 1g \
	/app/jobs/run_indegree.py

.PHONY: help build up down data run metrics benchmark test lint clean

help:
	@echo "make up         build the image and start the cluster"
	@echo "make data       download the SNAP web-BerkStan edge list into data/"
	@echo "make run        run the analysis on the cluster, then capture its metrics"
	@echo "make metrics    capture the latest run's metrics from the history server"
	@echo "make benchmark  measure the effect of caching and the broadcast join"
	@echo "make test       run the tests in the Spark image"
	@echo "make lint       ruff lint + format check (needs ruff installed)"
	@echo "make down       stop the cluster"

build:
	$(COMPOSE) build spark-master

up: build
	$(COMPOSE) up -d --wait spark-master spark-worker-1 spark-worker-2 spark-history
	@echo "master :8080  history :18080"

down:
	$(COMPOSE) --profile tools down

data:
	@sh scripts/fetch_data.sh

run:
	$(EXEC) -e RUN_TAG=default spark-master $(SPARK_SUBMIT)
	$(MAKE) metrics

metrics:
	$(RUNNER) python3 scripts/capture_metrics.py

# Each setting is run BENCHMARK_REPEATS times; the summary uses the median.
benchmark:
	for cfg in "1 1 baseline" "0 1 no-cache" "1 0 no-broadcast"; do \
		set -- $$cfg; \
		for i in $$(seq 1 $(BENCHMARK_REPEATS)); do \
			$(EXEC) -e CACHE=$$1 -e BROADCAST=$$2 -e RUN_TAG=bench-$$3-$$i \
				spark-master $(SPARK_SUBMIT) || exit 1; \
		done; \
	done
	$(RUNNER) python3 scripts/summarise_benchmark.py

test:
	$(RUNNER) python3 -m pytest -p no:cacheprovider

lint:
	ruff check .
	ruff format --check .

clean:
	$(COMPOSE) --profile tools down -v
