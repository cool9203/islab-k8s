#!/bin/bash
curl --location \
--request POST 'http://203.64.95.118:30001/gpu/GET' \
--header 'Content-Type: application/json' \
--data "{\"name\":\"${HOSTNAME}\", \"token\":\"\"}"
