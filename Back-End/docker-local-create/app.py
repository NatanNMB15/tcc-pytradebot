import os
import subprocess

import os
from flask import Flask
from flask import request

app = Flask(__name__)

@app.route('/create')
def docker_create():
    """
    Metódo chamado ao receber uma solicitação HTTP para criar um container Docker
    """
    usuario = request.args.get('id') # Pegar o ID do usuário com o parâmetro da URL (?id=valor)
    os.environ["id_usuario"] = usuario # Seta a variável de ambiente com o ID do usuário
    # Executa o Shell Script entrypoint.sh
    subprocess.call(['./entrypoint-create.sh'], shell=True)
    subprocess.call(['./entrypoint-start.sh'], shell=True)
    return 'OK\n'

@app.route('/reset')
def docker_reset():
    """
    Metódo chamado ao receber uma solicitação HTTP para reiniciar um container Docker
    """
    usuario = request.args.get('id') # Pegar o ID do usuário com o parâmetro da URL (?id=valor)
    os.environ["id_usuario"] = usuario # Seta a variável de ambiente com o ID do usuário
    # Executa o Shell Script entrypoint.sh
    subprocess.call(['./entrypoint-reset.sh'], shell=True)
    return 'OK\n'

@app.route('/remove')
def docker_remove():
    """
    Metódo chamado ao receber uma solicitação HTTP para remover um container Docker
    """
    usuario = request.args.get('id') # Pegar o ID do usuário com o parâmetro da URL (?id=valor)
    os.environ["id_usuario"] = usuario # Seta a variável de ambiente com o ID do usuário
    # Executa o Shell Script entrypoint.sh
    subprocess.call(['./entrypoint-remove.sh'], shell=True)
    return 'OK\n'

if __name__ == "__main__":
    app.run(debug=True,host='0.0.0.0',port=int(os.environ.get('PORT', 8081)))
