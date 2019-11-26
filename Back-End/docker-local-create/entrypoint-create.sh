#!/bin/bash
docker run -d \
  --env id_usuario=$id_usuario \
  --env DB_NAME=$DB_NAME \
  --env DB_USER=$DB_USER \
  --env DB_PASSWORD=$DB_PASSWORD \
  --env DB_HOST=$DB_HOST \
  --env DB_PORT=$DB_PORT \
  --network pytradebot \
  --name pytradebot-$id_usuario \
  pytradebot