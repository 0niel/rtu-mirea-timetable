Эта папка содержит документы с расписанием, которые будут переопределять расписание официального сайта. 

Чтобы добавить новый документ для переопределения расписания, отредактируйте файл ./docs/files.json, добавив новый объект с информацией о файле. Например:


**Пример:**
```
[
    {
        "file": "./расписание колледж.xlsx",
        "institute": "КПК",
        "type": 1,
        "degree": 4
    }
]
```

---

`file` - имя файла с расписанием

`institute` - короткое название института, для которого применяется расписание (см. https://github.com/mirea-ninja/rtu-schedule-parser/blob/c1d2dac7ce885a178556ba3bdf33cb6f43308035/rtu_schedule_parser/constants.py#L78)

`type` - тип расписания (см. https://github.com/mirea-ninja/rtu-schedule-parser/blob/c1d2dac7ce885a178556ba3bdf33cb6f43308035/rtu_schedule_parser/constants.py#L49)

`degree` - уровень образования (см. https://github.com/mirea-ninja/rtu-schedule-parser/blob/c1d2dac7ce885a178556ba3bdf33cb6f43308035/rtu_schedule_parser/constants.py#L8)
