FROM python:3.7.5-slim-buster

# Configura as variáveis de ambiente
ENV APP_HOME /app
ARG DEBIAN_FRONTEND=noninteractive

RUN mkdir -p $APP_HOME

WORKDIR $APP_HOME
# Adiciona os arquivos necessários
COPY . ./

# Executa as operações de Build
RUN apt-get update -y && apt-get install -yq --no-install-recommends curl gnupg gnupg1 gnupg2 lsb-release apt-transport-https ca-certificates software-properties-common && \
    curl -fsSL https://download.docker.com/linux/debian/gpg | apt-key add - && \
    add-apt-repository "deb [arch=amd64] https://download.docker.com/linux/debian $(lsb_release -cs) stable" && \
    apt-get update && apt-get install -yq --no-install-recommends docker-ce docker-ce-cli containerd.io && \
    pip install --upgrade pip && pip install --default-timeout=100 -r $APP_HOME/requirements.txt

# Timezone
ENV TZ=America/Sao_Paulo
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# Define o comando para iniciar o container
CMD exec gunicorn --bind :$PORT --workers 1 --threads 8 app:app