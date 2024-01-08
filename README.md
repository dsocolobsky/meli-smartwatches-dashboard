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

## Notas
- Ya que los llamados a la API de Mercadolibre son muy lentos y no se espera que varien mucho los datos, implemente un cacheo de 5 minutos para los resultados de las busquedas.
  Lo realice a mano con modelos y la DB por defecto (sqlite3) que para este caso es mas que suficiente, en un escenario real
  probablemente se utilizaria memcached o redis.
- El tiempo de cacheo se puede modificar en `settings.py` alternativamente tambien hay un boton de Forzar Refresh
  en cada pagina de resultados. Tener en cuenta que si se fuerza el refresh y se hace F5 manualmente, va a seguir forzando
  porque persiste el parametro `?force_refresh=True` en la URL.
- Utilice BulmaCSS para darle un minimo de estilo a la aplicacion.
- Utilice un minimo de HTMX para para mostrar indicadores de carga al cargar los datos.
- Muestro los thumbnails de los productos con el link que devuelve la API, probablemente seria mejor cachear
  nosotros la imagen pero no lo hice para no complicar el codigo, es para que quede un poco mas visual nada mas.
- El manejo de excepciones es basico y no hay logging de ningun tipo pero no queria perder demasiado tiempo con eso.
- Los tests probablemente podrian ser un poco mas exhaustivos.
- La secret key esta en .env, por simplicidad la pushee al repo pero en un escenario real deberia estar en un lugar seguro.
