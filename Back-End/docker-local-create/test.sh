#!/bin/bash
docker run -it \
  -e "PORT=8000" \
  -v $PWD:/app:z \
  -v /var/run/docker.sock:/var/run/docker.sock:z \
  --network pytradebot \
  docker-local-create bash
