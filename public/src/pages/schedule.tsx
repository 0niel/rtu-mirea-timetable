import { type NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import { useEffect, useState } from "react";
import axios from "axios";
import { useQuery } from "react-query";
import type { components } from "../api/schemas/openapi";
import {
  getLessonTypeBackgroundColor,
  getLessonTypeColor,
  getAcademicWeek,
} from "../utils";
import { useRouter } from "next/router";
import { Calendar } from "../components/Calendar";
import { CalendarHeader } from "../components/CalendarHeader";
import CalendarTitle from "../components/CalendarTitle";
import RoomsLinks from "../components/RoomsLinks";

const getSchedule = async (groups: string[]) => {
  const path = "/api/groups/name/{name}";

  const promises = groups.map((group) => {
    return axios.get(path.replace("{name}", group));
  });

  const responses = await Promise.all(promises);

  return responses.map((response) => response.data);
};

const getGroups = async () => {
  const path = "/api/groups?limit=3000&offset=0";

  const response = await axios.get(path);

  return response.data as components["schemas"]["Groups"];
};

const getLessonsForDate = (
  lessons: components["schemas"]["Group"]["lessons"],
  date: Date
) => {

  if (date >= new Date(2023, 11, 22)) {
    return [];
  }

  const week = getAcademicWeek(date);
  const day = date.getDay();

  if (day === -1) {
    return [];
  }

  const newLessons = lessons.filter((lesson) => {
    return lesson.weeks.includes(week) && lesson.weekday === day;
  });

  return newLessons;
};

const getLessonGridRow = (lesson: components["schemas"]["Lesson"]) => {
  const row = lesson.calls.num === 1 ? 2 : lesson.calls.num * 2;
  return `${row} / span 2`;
};

const lessonsForCompareColorsClassNames = [
  "bg-blue-50 hover:bg-blue-100",
  "bg-green-50 hover:bg-green-100",
  "bg-yellow-50 hover:bg-yellow-100",
];

const getLessonCell = (
  lesson: components["schemas"]["Lesson"],
  selectedDate: Date,
  customColor?: string | undefined | null
) => {
  console.log("custom", customColor);
  return (
    <div
      className={
        "group relative inset-1 mr-2 mb-2 flex w-full flex-col overflow-y-auto rounded-lg p-2 text-xs leading-5 " +
        (customColor ??
          getLessonTypeBackgroundColor(lesson.lesson_type?.name as string))
      }
    >
      <div className="flex font-medium text-blue-600">
        <div className="ml-2 flex flex-auto flex-col">
          <p className="text-sm font-medium text-gray-900">
            {lesson.discipline.name}
          </p>
          <p className="text-sm text-gray-500">
            {lesson.teachers.map((teacher) => (
              <Link
                key={teacher.id}
                href={`/teacher?name=${teacher.name}`}
                className="text-blue-600 hover:text-blue-900"
              >
                {teacher.name}{" "}
              </Link>
            ))}
          </p>

          <p className="text-sm font-medium text-gray-900">
            {lesson.room && (
              <RoomsLinks room={lesson.room} selectedDate={selectedDate} />
            )}
          </p>
        </div>

        <p className="text-sm text-gray-500">
          <span
            className={
              "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium " +
              getLessonTypeColor(lesson.lesson_type?.name as string)
            }
          >
            {lesson.lesson_type?.name}
          </span>
        </p>
      </div>
    </div>
  );
};

const Schedule: NextPage = () => {
  const router = useRouter();

  const [selectedGroups, setSelectedGroups] = useState<string[]>([]);

  useEffect(() => {
    const group = router.query.group as string;
    if (group) {
      setSelectedGroups([group]);
    }
  }, [router.query.group]);

  const currentDate = new Date();

  const [selectedDate, setSelectedDate] = useState(currentDate);
  const [monthToDisplay, setMonthToDisplay] = useState(selectedDate.getMonth());
  const [yearToDisplay, setYearToDisplay] = useState(
    selectedDate.getFullYear()
  );

  const {
    data: schedules,
    error: scheduleError,
    isLoading: scheduleIsLoading,
  } = useQuery(["group", selectedGroups], () => getSchedule(selectedGroups), {
    enabled: !!selectedGroups.length,
  });

  const {
    data: groups,
    error: groupsError,
    isLoading: groupsIsLoading,
  } = useQuery(["groups", selectedGroups], getGroups, {
    enabled: true,
    cacheTime: Infinity,
  });

  const getEventsByDate = () => {
    if (!schedules) {
      return {};
    }

    const lessons = schedules[0].lessons;
    const eventsByDate: { [key: string]: { name: string }[] } = {};

    // daysToEvents - дни предыдущего месяца, текущего и следующего
    const daysToEvents: Date[] = [];

    // Добавляем дни предыдущего месяца
    const daysInPreviousMonth = new Date(
      yearToDisplay,
      monthToDisplay,
      0
    ).getDate();
    for (let i = 0; i < daysInPreviousMonth; i++) {
      daysToEvents.push(new Date(yearToDisplay, monthToDisplay - 1, i + 1));
    }

    // Добавляем дни текущего месяца
    const daysInCurrentMonth = new Date(
      yearToDisplay,
      monthToDisplay + 1,
      0
    ).getDate();
    for (let i = 0; i < daysInCurrentMonth; i++) {
      daysToEvents.push(new Date(yearToDisplay, monthToDisplay, i + 1));
    }

    // Добавляем дни следующего месяца
    const daysInNextMonth = new Date(
      yearToDisplay,
      monthToDisplay + 2,
      0
    ).getDate();
    for (let i = 0; i < daysInNextMonth; i++) {
        daysToEvents.push(new Date(yearToDisplay, monthToDisplay + 1, i + 1));
    }

    daysToEvents.forEach((date) => {
      const lessonsForDate = getLessonsForDate(lessons, date);
      if (lessonsForDate.length > 0) {
        const key = date.toISOString().split("T")[0];

        if (key === undefined) {
          return;
        }

        if (date <= new Date(2023, 11, 21)) {
          eventsByDate[key] = lessonsForDate.map((lesson) => ({
            name: lesson.lesson_type?.name || "",
          }));
        }
      }
    });
    return eventsByDate;
  };

  const groupLessonsForManyGroups = (
    schedules: components["schemas"]["Group"][]
  ) => {
    const lessons = schedules.map((schedule) => schedule.lessons);

    const lessonsByTime: {
      lesson: components["schemas"]["Lesson"];
      groupIndex: number;
    }[][] = [];

    for (let i = 0; i < lessons.length; i++) {
      const lessonsForGroup = lessons[i];

      if (!lessonsForGroup) continue;

      lessonsForGroup.forEach((lesson) => {
        const lessonIndex = lesson.calls.num - 1;

        if (lessonsByTime[lessonIndex] === undefined) {
          lessonsByTime[lessonIndex] = [];
        }

        lessonsByTime[lessonIndex]?.push({
          lesson: lesson,
          groupIndex: i,
        });
      });
    }

    return lessonsByTime;
  };

  return (
    <>
      <Head>
        <title>Расписание группы</title>
        <meta name="description" content="Расписание группы" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      {scheduleError && (
        <div className="fixed inset-0 z-50 flex items-center justify-center">
          <div className="text-red-500">
            Произошла ошибка при загрузке расписания
          </div>
        </div>
      )}

      <div className="flex h-screen flex-col">
        <div className="flex flex-1 flex-col">
          <CalendarTitle
            onClickLeft={() => {
              setSelectedDate(
                new Date(selectedDate.getTime() - 24 * 60 * 60 * 1000)
              );
            }}
            onClickRight={() => {
              setSelectedDate(
                new Date(selectedDate.getTime() + 24 * 60 * 60 * 1000)
              );
            }}
            selectedDate={selectedDate}
            selectedGroups={selectedGroups}
            setSelectedGroups={setSelectedGroups}
            availableGroups={
              groups?.result.reduce((acc: string[], group) => {
                return acc.concat(group.groups);
              }, []) || []
            }
          />

          <div className="flex flex-auto overflow-hidden bg-white">
            <div className="flex flex-auto flex-col overflow-auto">
              <CalendarHeader
                selectedDate={selectedDate}
                setSelectedDate={setSelectedDate}
                eventsByDate={getEventsByDate()}
              />

              <div className="flex w-full flex-auto">
                <div className="w-14 flex-none bg-white ring-1 ring-gray-100" />
                <div className="grid flex-auto grid-cols-1 grid-rows-1">
                  {/* Horizontal lines */}
                  <div
                    className="col-start-1 col-end-2 row-start-1 grid divide-y divide-gray-100"
                    style={{
                      gridTemplateRows: "repeat(16, minmax(3.85rem, 1fr))",
                    }}
                  >
                    <div className="row-end-1 h-7"></div>
                    <div>
                      <div className="sticky left-0 -mt-2.5 -ml-14 w-14 pr-2 text-xs leading-5 text-gray-400">
                        9:00 - 10:30
                      </div>
                    </div>
                    <div />
                    <div>
                      <div className="sticky left-0 -mt-2.5 -ml-14 w-14 pr-2 text-xs leading-5 text-gray-400">
                        10:40 - 12:10
                      </div>
                    </div>
                    <div />
                    <div>
                      <div className="sticky left-0 -mt-2.5 -ml-14 w-14 pr-2 text-xs leading-5 text-gray-400">
                        12:40 - 14:10
                      </div>
                    </div>
                    <div />
                    <div>
                      <div className="sticky left-0 -mt-2.5 -ml-14 w-14 pr-2 text-xs leading-5 text-gray-400">
                        14:20 - 15:50
                      </div>
                    </div>
                    <div />
                    <div>
                      <div className="sticky left-0 -mt-2.5 -ml-14 w-14 pr-2 text-xs leading-5 text-gray-400">
                        16:20 - 17:50
                      </div>
                    </div>
                    <div />
                    <div>
                      <div className="sticky left-0 -mt-2.5 -ml-14 w-14 pr-2 text-xs leading-5 text-gray-400">
                        18:00 - 19:30
                      </div>
                    </div>
                    <div />
                    <div>
                      <div className="sticky left-0 -mt-2.5 -ml-14 w-14 pr-2 text-xs leading-5 text-gray-400">
                        19:40 - 21:10
                      </div>
                    </div>
                    <div />
                  </div>
                  {/* Events */}
                  {schedules && groups && (
                    <ol
                      className="col-start-1 col-end-2 row-start-1 grid grid-cols-1"
                      style={{
                        // 1.75rem for the time labels + 288 rows for 12 hours * 24 (min-height)
                        gridTemplateRows:
                          "1.75rem repeat(16, minmax(0, 1fr)) auto",
                      }}
                    >
                      {schedules.length == 1 &&
                        getLessonsForDate(
                          schedules[0].lessons,
                          selectedDate
                        ).map((lesson) => (
                          <li
                            key={lesson.id}
                            className="relative mt-px flex"
                            style={{
                              gridRow: getLessonGridRow(lesson),
                            }}
                          >
                            {getLessonCell(lesson, selectedDate)}
                          </li>
                        ))}

                      {schedules.length > 1 &&
                        groupLessonsForManyGroups(
                          schedules.map(
                            (schedule: components["schemas"]["Group"]) => {
                              const lessonsForDate = getLessonsForDate(
                                schedule.lessons,
                                selectedDate
                              );

                              const newSchedule = {
                                ...schedule,
                                lessons: lessonsForDate,
                              };

                              return newSchedule;
                            }
                          )
                        ).map((lessons, lessonsIdx) => {
                          return (
                            <li
                              key={lessonsIdx}
                              className="relative mt-px flex"
                              style={{
                                gridRow: getLessonGridRow(lessons[0]!.lesson!),
                              }}
                            >
                              <div className="flex w-full flex-row justify-center space-x-2">
                                {lessons.map((lesson, index) =>
                                  getLessonCell(
                                    lesson.lesson,
                                    selectedDate,
                                    lessonsForCompareColorsClassNames[
                                      lesson.groupIndex
                                    ]
                                  )
                                )}
                              </div>
                            </li>
                          );
                        })}
                    </ol>
                  )}
                </div>
              </div>
            </div>
            <Calendar
              selectedDate={selectedDate}
              setSelectedDate={setSelectedDate}
              monthToDisplay={monthToDisplay}
              setMonthToDisplay={setMonthToDisplay}
              yearToDisplay={yearToDisplay}
              setYearToDisplay={setYearToDisplay}
              eventsByDate={getEventsByDate()}
            />
          </div>
        </div>
      </div>
    </>
  );
};

export default Schedule;
