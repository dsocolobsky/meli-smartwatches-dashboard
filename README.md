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

Es importante correrlo de esta manera ya que necesitamos el soporte de HTTPS
para poder utilizar OAuth con Mercadolibre.

Entrar a [https://localhost:8000](https://localhost:8000) (presentar atencion que debe ser https)

## Coverage
Para correr los tests y ver el coverage:
- `coverage run --source='.' manage.py test core`
- `coverage report`

## Cache
Ya que los llamados a la API de Mercadolibre son muy lentos, los datos no varian muy seguido, y se muestran los mismos a todos
los usuarios, la pagina usa una cache de 5 minutos para evitar realizar los llamados en cada request.

Originalmente implemente una cache manual utilizando Models y la DB por defecto (sqlite3), pero me di cuenta que no era
necesario ya que Django ya provee un sistema para cachear en memoria Views enteras, es por esto que cacheo por 5 minutos
las views que arrojan resultados de las busquedas. Esto reduce mucho el codigo.

Si se quiere probar el sistema sin la cache, se puede cambiar en `settings.py` en la definicion de `CACHES`.

En caso de querer ver esta cache (es un approach alternativo que puede ser mas flexible si se quiere trabajar con los datos),
estan en la branch `cache-manual`.

Actualmente uso el backend en memoria de Django para la cache, en produccion seria mejor usar memcached o redis.

## Sobre los certificados
Para poder utilizar OAuth con Mercadolibre es necesario que el servidor corra en HTTPS, para eso genere unos certificados (cert.pem y key.pem)
que son los que se utilizan al correr el servidor.

No pude testear esto en otra PC, creeria que al adjuntarlos deberia andar, pero en el evento de que solo funcionasen en la PC en las que se emitieron,
los certificados fueron generados con [mkcert](https://github.com/FiloSottile/mkcert). Se pueden borrar y regenerar de vuelta:

`mkcert -install`
`mkcert -cert-file cert.pem -key-file key.pem localhost 127.0.0.1`

## Otras Notas
- Utilice BulmaCSS para darle un minimo de estilo a la aplicacion.
- Utilice un minimo de HTMX para para mostrar indicadores de carga al cargar los datos.
- Muestro los thumbnails de los productos con el link que devuelve la API, probablemente seria mejor cachear
  nosotros la imagen pero no lo hice para no complicar el codigo, es para que quede un poco mas visual nada mas.
- El manejo de excepciones es basico y no hay logging de ningun tipo pero no queria perder demasiado tiempo con eso.
- Los tests probablemente podrian ser un poco mas exhaustivos.
- La secret key esta en .env, por simplicidad la pushee al repo pero en un escenario real deberia estar en un lugar seguro.
- Deje Django en Debug Mode por simplicidad

