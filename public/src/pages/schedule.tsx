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

const getSchedule = async (group: string) => {
  const url = "/api/groups/name/{name}";

  const response = await axios.get(url.replace("{name}", group));

  return response.data;
};

const getLessonDuration = (timeStart: string, timeEnd: string) => {
  const [startHour, startMinute] = timeStart.split(":");
  const [endHour, endMinute] = timeEnd.split(":");
  const start = new Date();
  const end = new Date();
  start.setHours(Number(startHour));
  start.setMinutes(Number(startMinute));
  end.setHours(Number(endHour));
  end.setMinutes(Number(endMinute));
  return end.getTime() - start.getTime();
};

const getLessonsForDate = (
  lessons: components["schemas"]["Group"]["lessons"],
  date: Date
) => {
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

const Schedule: NextPage = () => {
  const router = useRouter();
  const group = router.query.group as string;

  const currentDate = new Date();

  const [selectedDate, setSelectedDate] = useState(currentDate);
  const [monthToDisplay, setMonthToDisplay] = useState(selectedDate.getMonth());
  const [yearToDisplay, setYearToDisplay] = useState(
    selectedDate.getFullYear()
  );

  const [schedule, setSchedule] = useState<
    components["schemas"]["Group"] | null
  >(null);

  const { data, error } = useQuery(["group", group], () => getSchedule(group), {
    enabled: !!group,
  });

  useEffect(() => {
    if (data) {
      setSchedule(data);
    }
  }, [data]);

  const getEventsByDate = () => {
    if (!schedule) {
      return {};
    }

    const lessons = schedule.lessons;
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

        eventsByDate[key] = lessonsForDate.map((lesson) => ({
          name: lesson.lesson_type?.name || "",
        }));
      }
    });

    return eventsByDate;
  };

  const getLessonGridRow = (lesson: components["schemas"]["Lesson"]) => {
    const row = lesson.calls.num === 1 ? 2 : lesson.calls.num * 2;
    return `${row} / span 2`;
  };

  return (
    <>
      <Head>
        <title>Расписание группы</title>
        <meta name="description" content="Расписание группы" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
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
                  <ol
                    className="col-start-1 col-end-2 row-start-1 grid grid-cols-1"
                    style={{
                      // 1.75rem for the time labels + 288 rows for 12 hours * 24 (min-height)
                      gridTemplateRows:
                        "1.75rem repeat(16, minmax(0, 1fr)) auto",
                    }}
                  >
                    {schedule != null &&
                      getLessonsForDate(schedule.lessons, selectedDate).map(
                        (lesson) => (
                          <li
                            key={lesson.id}
                            className="relative mt-px flex"
                            // calls.time_start и calls.time_end в формате HH:MM:SS
                            style={{
                              gridRow: getLessonGridRow(lesson),
                            }}
                          >
                            <div
                              className={
                                "group absolute inset-1 flex flex-col overflow-y-auto rounded-lg p-2 text-xs leading-5 " +
                                getLessonTypeBackgroundColor(
                                  lesson.lesson_type?.name as string
                                )
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
                                        {teacher.name}
                                      </Link>
                                    ))}
                                  </p>

                                  <p className="text-sm font-medium text-gray-900">
                                    {lesson.room && (
                                      <RoomsLinks
                                        room={lesson.room}
                                        selectedDate={selectedDate}
                                      />
                                    )}
                                  </p>
                                </div>

                                <p className="text-sm text-gray-500">
                                  <span
                                    className={
                                      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium " +
                                      getLessonTypeColor(
                                        lesson.lesson_type?.name as string
                                      )
                                    }
                                  >
                                    {lesson.lesson_type?.name}
                                  </span>
                                </p>
                              </div>
                            </div>
                          </li>
                        )
                      )}
                  </ol>
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
