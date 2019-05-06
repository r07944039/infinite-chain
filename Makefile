all: help

new_server:
	python3 new_server.py

ping1:
	python3 new_ping1.py

ping2:
	python3 new_ping2.py

## Run blockchain setup and start mining
run:
	python3 main.py

## Test all API
t1: 
	python3 client.py 127.0.0.1 1234 '{"method":"getBlocks","data": { \
        "hash_count" : 1, \
        "hash_begin" : "0000000008e647742775a230787d66fdf92c46a48c896bfbc85cdc8acc67e87d", \
        "hash_stop" : "0000be5b53f2dc1a836d75e7a868bf9ee576d57891855b521eaabfa876f8a606" \
    }}'
	python3 client.py 127.0.0.1 2345 '{ \
		"method": "getBlockCount" \
	}'
	python3 client.py 127.0.0.1 2345 '{ \
		"method": "getBlockHash", \
		"data": { \
			"block_height": 10 \
		} \
	}'
	python3 client.py 127.0.0.1 2345 '{ \
		"method": "getBlockHeader", \
		"data": { \
			"block_hash": "0000be5b53f2dc1a836d75e7a868bf9ee576d57891855b521eaabfa876f8a606" \
		} \
	}' 
	python3 client.py 127.0.0.1 2345 '{"method":"sendHeader","data": { \
		"block_hash": "00000f55c821fdd5d88b5a1071ec70064681ebef1ca7829500de95ba4dc33077", \
		"block_header" : "00000001000005f3aaef1c4ef5f896ce123d6124f88b863635872ab489985c69e62a53a40000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000348510", \
		"block_height" : 2 \
	}}'

## Ping 2345
p2:
	python3 client.py 127.0.0.1 2345 '{"method":"sendHeader","data": { \
		"block_hash": "00000f55c821fdd5d88b5a1071ec70064681ebef1ca7829500de95ba4dc33077", \
		"block_header" : "00000001000005f3aaef1c4ef5f896ce123d6124f88b863635872ab489985c69e62a53a40000000000000000000000000000000000000000000000000000000000000000000010000000000000000000000000000000000000000000000000000000000000348510", \
		"block_height" : "2" \
	}}'

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