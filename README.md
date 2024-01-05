Testeado en MacOS con Python 3.11.7

## Instrucciones
Clonar el repositorio:

`git clone git@github.com:dsocolobsky/realtrends.git`

Crear un entorno virtual y activarlo:

`python3 -m venv .venv`

`source .venv/bin/activate`

Instalar las dependencias:

`python3 -m pip install -r requirements.txt`

Correr las migraciones:

`python3 manage.py migrate`

Correr el servidor:

`python3 manage.py runserver_plus --cert-file cert.pem --key-file key.pem
`
