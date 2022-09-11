#!/usr/bin/make

REPO_DIR = ..

build: # build all containers
	@docker build -t bancho-service:latest $(REPO_DIR)/bancho-service

clone: # clone all containers
	@if [ ! -d $(REPO_DIR)/bancho-service ]; then git clone git@github.com:akatsuki-v2/bancho-service.git $(REPO_DIR)/bancho-service; fi

pull: # pull all containers
	cd $(REPO_DIR)/bancho-service && git pull

run-bg: # run all containers in the background
	@docker-compose up -d \
		bancho-service

run: # run all containers in the foreground
	@docker-compose up \
		bancho-service

logs: # attach to the containers live to view their logs
	@docker-compose logs -f
