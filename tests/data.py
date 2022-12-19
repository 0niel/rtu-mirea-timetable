from app.models import Campus, Room

CAMPUSES = [Campus(id=1, name="Кампус 1", short_name="К1"), Campus(id=2, name="Кампус 2", short_name="К2")]
ROOMS = [
    Room(id=1, name="Аудитория 1", campus_id=1, campus=CAMPUSES[0]),
    Room(id=2, name="Аудитория 2", campus_id=1, campus=CAMPUSES[0]),
    Room(id=3, name="Аудитория 3", campus_id=1, campus=CAMPUSES[0]),
]
