
# Build and Launch

## Backend Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).
* [Poetry](https://python-poetry.org/) for Python package and environment management.


## Backend local development

### Without containers

1. Clone this repo:

```bash
git clone https://github.com/mirea-ninja/rtu-map-backend.git
cd mobile-app-web
```

2. Edit `.env.example`

3. Rename `.env.example` to `.env`.

4. Install dependencies using poetry:

```bash
cd .\backend\src\
poetry install
```

5. Activate Poetry virtual environment:

```bash
poetry shell
```

6. [Install](https://www.postgresql.org/download/) and run PostgreSQL locally.

8. Configure the connection to the PostgreSQL database in the `.env` file

8. Run backend app using uvicorn:

```bash
uvicorn app.main:app --host localhost --reload --port 8080
```

### With Docker Compose Override

**Start the dev stack with Docker Compose:**

```bash
docker-compose up -d
```

During development, you can change Docker Compose settings that will only affect the local development environment, in the file `docker-compose.override.yml`.

Have in mind that if you have a syntax error and save the Python file, it will break and exit, and the container will stop. After that, you can restart the container by fixing the error and running again:

To check the logs, run:

```bash
docker-compose logs
```

To check the logs of a specific service, add the name of the service, e.g.:

```bash
docker-compose logs backend
```

By default, when starting the docker-compose backend container, the script will be executed `/start-reload.sh `

There is also a commented out [command override](https://github.com/mirea-ninja/mobile-app-web/blob/561997b04c5d0ed2a5c8359c17b49042fe59ac15/docker-compose.override.yml#L67), you can uncomment it and comment the default one. It makes the backend container run a process that does "nothing", but keeps the container alive. That allows you to get inside your running container and execute commands inside, for example a Python interpreter to test installed dependencies

To get inside the container with a `bash` session you can start the stack with:

```bash
docker-compose up -d
```

and then `exec` inside the running container:

```bash
docker-compose exec backend bash
```

You should see an output like:

```console
root@7f2607af31c3:/app#
```

that means that you are in a `bash` session inside your container, as a `root` user, under the `/app` directory.

There you can use the script `/start-reload.sh` to run the debug live reloading server. You can run that script from inside the container with:

```bash
bash /start-reload.sh
```

...it will look like:

```console
root@7f2607af31c3:/app# bash /start-reload.sh
```

and then hit enter. That runs the live reloading server that auto reloads when it detects code changes.

## Migrations

Make sure you create a "revision" of your models and that you "upgrade" your database with that revision every time you change them. As this is what will update the tables in your database. Otherwise, your application will have errors.

### Running migrations locally without Docker

In the directory `.\backend\src\`:
* Make sure that all the Poetry dependencies are installed and you are in the Poetry Shell environment.

### Running migrations with Docker Compose 
Migrations are applied automatically when starting docker-compose in development mode.

* Start an interactive session in the backend container:

```bash
docker-compose exec backend bash
```

### Migration rules and commands
* If you created a new model in `./backend/src/app/pkg/sqlalchemy/schemes/`, make sure to import it in `./backend/src/app/pkg/sqlalchemy/schemes/__init__.py`, that all the models will be used by Alembic.

* After changing a model (for example, adding a column), create a revision, e.g.:

```bash
alembic revision --autogenerate -m "Commit description"
```

* Commit to the git repository the files generated in the alembic directory.

* After creating the revision, run the migration in the database (this is what will actually change the database):

```bash
alembic upgrade head
```

<a name="deployment"></a>

## Deployment

Todo...

<a name="docs"></a>

## Documentation

Todo...

<a name="license"></a>

## License

- [MIT](LICENSE)
