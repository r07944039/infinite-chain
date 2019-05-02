all: help

## Run blockchain setup and start mining
run:
	python3 main.py

## Ping 1234
p1: 
	python3 client.py 127.0.0.1 1234 '{"method":"sendHeader","data":"bbb"}'

## Ping 2345
p2:
	python3 client.py 127.0.0.1 2345 '{"method":"sendHeader","data":"bbb"}'

## Ping 1234 then 2345
pp:
	python3 client.py 127.0.0.1 1234 '{"method":"sendHeader","data":"bbb"}'
	python3 client.py 127.0.0.1 2345 '{"method":"sendHeader","data":"bbb"}'

## Open neighbor node 1
n1:
	python3 open_neighbor1.py

## Open neighbor node 2
n2:
	python3 open_neighbor2.py

#########
# Help ##
#########
# COLORS
GREEN  := $(shell tput -Txterm setaf 2)
YELLOW := $(shell tput -Txterm setaf 3)
WHITE  := $(shell tput -Txterm setaf 7)
RESET  := $(shell tput -Txterm sgr0)

TARGET_MAX_CHAR_NUM=6
## Show help
help:
	@echo ''
	@echo 'Usage:'
	@echo '  ${YELLOW}make${RESET} ${GREEN}<target>${RESET}'
	@echo ''
	@echo 'Targets:'
	@awk '/^[a-zA-Z\-\_0-9]+:/ { \
		helpMessage = match(lastLine, /^## (.*)/); \
		if (helpMessage) { \
			helpCommand = substr($$1, 0, index($$1, ":")); \
			helpMessage = substr(lastLine, RSTART + 3, RLENGTH); \
			printf "  ${YELLOW}%-$(TARGET_MAX_CHAR_NUM)s${RESET} ${GREEN}%s${RESET}\n", helpCommand, helpMessage; \
		} \
	} \
{ lastLine = $$0 }' $(MAKEFILE_LIST)
	@echo ''