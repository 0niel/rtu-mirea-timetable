
# rtu-mirea-timetable

The rtu-mirea-timetable service is a Web App (including a documented API) that provides users with access to schedules and other related data. It allows users search for classes, teachers and lessons, and view detailed information about each lesson.

## Backend Requirements

* [Docker](https://www.docker.com/).
* [Docker Compose](https://docs.docker.com/compose/install/).


## Backend local development

### Without containers

1. Clone this repo:
```bash
git clone https://github.com/mirea-ninja/rtu-mirea-timetable.git
cd rtu-mirea-timetable
```
2. Edit `.env`
3. Install dependencies:
```bash
pip install -r requirements.txt
```
4. Run backend app:
```bash
python runserver.py
```
5. Run celery app:
```bash
celery -A worker.tasks worker -B -E --concurrency=2
```


### With containers

1. Clone this repo:
```bash
git clone https://github.com/mirea-ninja/rtu-mirea-timetable.git
cd rtu-mirea-timetable
```
2. Edit `.env`
3. Run stack using docker compose:
```bash
docker compose up -d
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
