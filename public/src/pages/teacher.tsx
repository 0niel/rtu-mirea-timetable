import { type NextPage } from "next";
import Head from "next/head";

import { ClockIcon, MapIcon, UserIcon } from "@heroicons/react/20/solid";
import { TbNumber } from "react-icons/tb";
import { useEffect, useState } from "react";
import axios from "axios";
import { useQuery } from "react-query";
import type { components } from "../api/schemas/openapi";
import {
  getLessonTypeColor,
  getAcademicWeek,
  getNormalizedWeekday,
} from "../utils";
import { useRouter } from "next/router";
import { Calendar } from "../components/Calendar";
import { CalendarHeader } from "../components/CalendarHeader";
import CalendarTitle from "../components/CalendarTitle";
import RoomsLinks from "../components/RoomsLinks";

const searchTeacherSchedule = async (name: string) => {
  axios.defaults.baseURL = "https://timetable.mirea.ru";
  const url = "/api/teachers/search/{name}";

  const response = await axios.get(url.replace("{name}", name));

  const data = response.data;

  //   если больше одного препода, то выбираем первого
  return data[0];
};

const joinLessonsByGroups = (
  lessons: components["schemas"]["Teacher"]["lessons"]
) => {
  console.log("LESSONS", lessons);
  const newLessons: components["schemas"]["Teacher"]["lessons"] = [];

  lessons?.forEach((lesson) => {
    const newLesson = newLessons.find((newLesson) => {
      return (
        newLesson.discipline.name === lesson.discipline.name &&
        newLesson.weekday === lesson.weekday &&
        newLesson.calls.time_start === lesson.calls.time_start
      );
    });

    if (newLesson) {
      if (newLesson.group.name.indexOf(lesson.group.name) === -1) {
        newLesson.group.name += `, ${lesson.group.name}`;
      }
    } else {
      newLessons.push(lesson);
    }
  });
  return newLessons;
};

const getLessonsForDate = (lessons: any, date: Date) => {
  const week = getAcademicWeek(date);
  const day = getNormalizedWeekday(date);

  if (day === -1) {
    return [];
  }

  if (lessons === undefined) {
    return [];
  }

  const newLessons = (lessons as components["schemas"]["Lesson"][]).filter(
    (lesson: components["schemas"]["Lesson"]) => {
      return lesson.weeks.includes(week) && lesson.weekday === day;
    }
  );

  return newLessons.sort((a, b) => a.calls.num - b.calls.num);
};

const Teacher: NextPage = () => {
  const { name } = useRouter().query as { name: string };

  const currentDate = new Date();

  const [selectedDate, setSelectedDate] = useState(currentDate);
  const [monthToDisplay, setMonthToDisplay] = useState(selectedDate.getMonth());
  const [yearToDisplay, setYearToDisplay] = useState(
    selectedDate.getFullYear()
  );

  const [teacher, setTeacher] = useState<
    components["schemas"]["Teacher"] | null
  >(null);

  const { data, isLoading } = useQuery(
    ["teacher", name],
    () => searchTeacherSchedule(name),
    {
      enabled: !!name,
    }
  );

  useEffect(() => {
    if (data) {
      setTeacher(data);
    }
  }, [data]);

  const getEventsByDate = () => {
    const lessons = teacher?.lessons;
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

      // Не добавляем в качестве события одинаковые занятия в одно и то же время,
      // но с разными группами (лекции)
      const lessonsGrouped = lessonsForDate.reduce((acc, lesson) => {
        const newLesson = acc.find((accLesson) => {
          return (
            accLesson.calls.time_start === lesson.calls.time_start &&
            accLesson.calls.time_end === lesson.calls.time_end &&
            accLesson.lesson_type?.name === lesson.lesson_type?.name
          );
        });

        if (!newLesson) {
          acc.push(lesson);
        }

        return acc;
      }, [] as components["schemas"]["Lesson"][]);

      if (lessonsGrouped.length > 0) {
        const key = date.toISOString().split("T")[0];

        if (key === undefined) {
          return;
        }

        eventsByDate[key] = lessonsGrouped.map((lesson) => ({
          name: lesson.lesson_type?.name || "",
        }));
      }
    });

    return eventsByDate;
  };

  return (
    <>
      <Head>
        <title>Расписание преподавателя {name}</title>
        <meta name="description" content="Расписание преподавателя" />
        <link rel="icon" href="/favicon.ico" />
      </Head>
      <div className="flex h-screen flex-col">
        <h2 className="text-lg font-semibold text-gray-900">
          Расписание преподавателя {name}
        </h2>
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
              <ol className="mt-4 divide-y divide-gray-100 text-sm leading-6 lg:col-span-7 xl:col-span-8">
                {teacher &&
                  joinLessonsByGroups(
                    getLessonsForDate(teacher.lessons, selectedDate)
                  ).map((lesson, index) => (
                    <li
                      key={index}
                      className="relative flex space-x-6 py-6 xl:static"
                    >
                      <div className="flex-auto">
                        <div className="flex items-center space-x-3">
                          <h3 className="pr-10 font-semibold text-gray-900 xl:pr-0">
                            {lesson.discipline.name}
                          </h3>
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

                        <dl className="mt-2 flex flex-col text-gray-500 xl:flex-row">
                          <div className="flex items-start space-x-3">
                            <dt className="mt-0.5">
                              <span className="sr-only">Номер пары</span>
                              <TbNumber
                                className="h-5 w-5 text-gray-400"
                                aria-hidden="true"
                              />
                            </dt>
                            <dd>{lesson.calls.num} пара</dd>
                          </div>
                          <div className="mt-2 flex items-start space-x-3 xl:mt-0 xl:ml-3.5 xl:border-l xl:border-gray-400 xl:border-opacity-50 xl:pl-3.5">
                            <dt className="mt-0.5">
                              <span className="sr-only">Время</span>
                              <ClockIcon
                                className="h-5 w-5 text-gray-400"
                                aria-hidden="true"
                              />
                            </dt>
                            <dd>
                              <time>
                                {lesson.calls.time_start.slice(0, 5)} -{" "}
                                {lesson.calls.time_end.slice(0, 5)}
                              </time>
                            </dd>
                          </div>
                          <div className="mt-2 flex items-center space-x-3 xl:mt-0 xl:ml-3.5 xl:border-l xl:border-gray-400 xl:border-opacity-50 xl:pl-3.5">
                            <dt className="mt-0.5">
                              <span className="sr-only">Аудитория</span>
                              <MapIcon
                                className="h-5 w-5 text-gray-400"
                                aria-hidden="true"
                              />
                            </dt>
                            <dd>
                              {lesson.room && (
                                <RoomsLinks
                                  room={lesson.room}
                                  selectedDate={selectedDate}
                                />
                              )}
                            </dd>
                          </div>
                          {/* Список групп */}
                          <div className="mt-2 flex items-start space-x-3 xl:mt-0 xl:ml-3.5 xl:border-l xl:border-gray-400 xl:border-opacity-50 xl:pl-3.5">
                            <dt className="mt-0.5">
                              <span className="sr-only">Группы</span>
                              <UserIcon
                                className="h-5 w-5 text-gray-400"
                                aria-hidden="true"
                              />
                            </dt>
                            <dd>{lesson.group.name}</dd>
                          </div>
                        </dl>
                      </div>
                    </li>
                  ))}
              </ol>
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

export default Teacher;
