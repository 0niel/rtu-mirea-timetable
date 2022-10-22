import datetime

import pytz


def get_week(date: datetime.datetime = None) -> int:
    """Возвращает номер учебной недели по дате

    Args:
        date (datetime.datetime, optional): Дата, для которой необходимо получить учебную неделю.
    """
    now = now_date() if date is None else date
    start_date = get_semester_start(date)

    if now.timestamp() < start_date.timestamp():
        return 1

    week = now.isocalendar()[1] - start_date.isocalendar()[1]

    if now.isocalendar()[2] != 0:
        week += 1

    return week


def get_semester_start(date: datetime.datetime = None) -> datetime.datetime:
    """Возвращает дату начала семестра по дате

    Args:
        date (datetime.datetime, optional): Дата для расчёта начала семестра.
    """
    date = now_date() if date is None else date
    return get_first_semester() if date.month >= 9 else get_second_semester()


def now_date() -> datetime.datetime:
    return datetime.datetime.now(pytz.timezone('Europe/Moscow'))


def get_first_semester() -> datetime.datetime:
    return datetime.datetime(now_date().year, 9, 1)


def get_second_semester() -> datetime.datetime:
    return datetime.datetime(now_date().year, 2, 9)
