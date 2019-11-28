import gunicorn
from psycogreen.gevent import patch_psycopg     # use this if you use gevent workers

# Ocultar o Header "Server" do Gunicorn
gunicorn.SERVER_SOFTWARE = 'PyTradeBot'

def post_fork(server, worker):
    """
    Método para realizar o Patch do Psycopg2 com o gevent
    """
    patch_psycopg()
    worker.log.info("Made Psycopg2 Green")