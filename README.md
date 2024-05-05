Esto fue un simple challenge en Django que realicé para el proceso de selección de una empresa, utilizando
la API de Mercadolibre.

![screenshot](https://github.com/dsocolobsky/meli-smartwatches-dashboard/blob/main/screenshot.png?raw=true)

## Instrucciones
Clonar el repositorio:

`git clone git@github.com:dsocolobsky/meli-smartwatches-dashboard.git`

Crear un entorno virtual y activarlo:

`python3 -m venv .venv`

`source .venv/bin/activate`

Instalar las dependencias:

`python3 -m pip install -r requirements.txt`

Crear una aplicación en el devcenter de Mercadolibre, completar
los campos correspondientes en `.env`

Correr las migraciones:

`python3 manage.py migrate`

Generar certificados con [mkcert](https://github.com/FiloSottile/mkcert):
* `mkcert -install`
* `mkcert -cert-file cert.pem -key-file key.pem localhost 127.0.0.1`

Correr el servidor:

`python3 manage.py runserver_plus --cert-file cert.pem --key-file key.pem
`

Es necesario generar los certificados y correrlo de esta manera ya que necesitamos el soporte de HTTPS
para poder utilizar OAuth con Mercadolibre.

Entrar a [https://localhost:8000](https://localhost:8000) (presentar atencion que debe ser https)

## Coverage
Para correr los tests y ver el coverage:
- `coverage run --source='.' manage.py test core`
- `coverage report`

## Cache
Ya que los llamados a la API de Mercadolibre son muy lentos, los datos no varian muy seguido, y se muestran los mismos a todos
los usuarios, la pagina usa una cache de 5 minutos para evitar realizar los llamados en cada request.

Si se quiere probar el sistema sin la cache, se puede cambiar en `settings.py` en la definicion de `CACHES`.

Actualmente uso el backend en memoria de Django para la cache, en produccion seria mejor usar memcached o redis.

## Otras Notas
- Utilice BulmaCSS para darle un minimo de estilo a la aplicacion.
- Utilice un minimo de HTMX para para mostrar indicadores de carga al cargar los datos.
- Muestro los thumbnails de los productos con el link que devuelve la API, probablemente seria mejor cachear
  nosotros la imagen pero no lo hice para no complicar el codigo, es para que quede un poco mas visual nada mas.
- El manejo de excepciones es basico y no hay logging de ningun tipo pero no queria perder demasiado tiempo con eso.
- Los tests probablemente podrian ser un poco mas exhaustivos.
- Deje Django en Debug Mode por simplicidad

