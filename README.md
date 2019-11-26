# Sistema PyTradeBot


Repositório do sistema Pytradebot do Trabalho de Conclusão de Curso


## Instalação do Docker e Docker Compose:


Necessário ter o Docker Community e o Docker Compose instalado no Linux ou Windows.


### Windows


Acesse o link https://docs.docker.com/v17.09/docker-for-windows/install/ 


Utilize a versão "Stable". A versão do Windows já vem com o Docker Compose.


### Linux


Acesse o Link https://docs.docker.com/v17.09/engine/installation/linux/docker-ce/ubuntu/#install-using-the-repository 

Siga os passos do tópico "Install using the repository" e subtópico "INSTALL DOCKER CE".


Instalar o Docker Compose no Linux execute os comandos abaixo:

```
sudo curl -L "https://github.com/docker/compose/releases/download/1.25.0/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
```

```
sudo chmod +x /usr/local/bin/docker-compose
```


## Implantação do sistema PyTradeBot


1. Criar imagem Software de Trading


Dentro da pasta "Software de Trading" tem o procedimento para criar a imagem do Software de Trading.


2. Back-End


Dentro da pasta "Back-End" tem o passo-a-passo para construir a imagem do Django e executar.