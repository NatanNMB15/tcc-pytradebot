# Back-End Django e Banco de Dados

## Implantar o Back-End


Com o Docker e Docker-Compose já instalados, execute os comandos abaixo a partir desta
pasta raiz. Execute os comandos no terminal do Linux ou Windows.



1. Construir imagem Django:


```
docker build --compress -t django-pytradebot .
```


2. Construir imagem Docker Local Create (Cloud Function):


```
docker build --compress -t docker-local-create docker-local-create/.
```


3. Criar rede virtual pytradebot:


```
docker network create \
  --driver=bridge \
  --subnet=172.28.0.0/16 \
  --ip-range=172.28.1.0/24 \
  --gateway=172.28.1.254 \
  pytradebot
```


4. Inicializar todo o sistema com o Docker Compose:


```
docker-compose up -d
```

