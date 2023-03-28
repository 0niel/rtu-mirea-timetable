import { type NextPage } from "next";
import Head from "next/head";

import {
  CalendarIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
  ClockIcon,
  MapIcon,
  UserIcon,
} from "@heroicons/react/20/solid";
import { useEffect, useRef, useState } from "react";
import axios from "axios";
import { useQuery } from "react-query";
import { components } from "../api/schemas/openapi";
import { getLessonTypeColor, getWeekByDate, getWeekDaysByDate } from "../utils";
import { useRouter } from "next/router";
import { Calendar } from "../components/Calendar";

const generateDays = (
  currentDate = new Date(),
  monthToDisplay: number,
  yearToDisplay: number
) => {
  const days = [];

  const firstDayOfMonth = new Date(yearToDisplay, monthToDisplay - 1, 1);
  const lastDayOfMonth = new Date(yearToDisplay, monthToDisplay, 0);

  let lastDayOfPreviousMonth = new Date(yearToDisplay, monthToDisplay - 1, 0);

  if (monthToDisplay === 1) {
    lastDayOfPreviousMonth = new Date(yearToDisplay - 1, 12, 0);
  }

  const daysInMonth = lastDayOfMonth.getDate();
  const daysInLastMonth = lastDayOfPreviousMonth.getDate();

  const dayOfWeek = firstDayOfMonth.getDay() - 1;

  let daysBefore = dayOfWeek;

  // Если первый день месяца - воскресенье, то нужно отобразить 6 дней предыдущего месяца
  if (dayOfWeek === -1) {
    daysBefore = 6;
  }

  // Начало предыдущего месяца
  for (let i = daysBefore; i > 0; i--) {
    days.push({
      date: new Date(
        yearToDisplay,
        monthToDisplay - 2,
        daysInLastMonth - i + 1
      ),
      isCurrentMonth: false,
    });
  }

  // Текущий месяц
  for (let i = 1; i <= daysInMonth; i++) {
    days.push({
      date: new Date(yearToDisplay, monthToDisplay - 1, i),
      isCurrentMonth: true,
      isToday:
        currentDate.getFullYear() === yearToDisplay &&
        currentDate.getMonth() === monthToDisplay - 1 &&
        currentDate.getDate() === i,
      isSelected:
        currentDate.getFullYear() === yearToDisplay &&
        currentDate.getMonth() === monthToDisplay - 1 &&
        currentDate.getDate() === i,
    });
  }

  // Конец текущего месяца
  const daysAfter = 7 - (days.length % 7);

  for (let i = 1; i <= daysAfter; i++) {
    days.push({
      date: new Date(yearToDisplay, monthToDisplay, i),
    });
  }

  return days;
};

function classNames(...classes: unknown[]) {
  return classes.filter(Boolean).join(" ");
}

const searchTeacherSchedule = async (name: string) => {
  axios.defaults.baseURL = "https://timetable.mirea.ru";
  const url = "/api/teacher/search/{name}";

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
  const week = getWeekByDate(date);
  const day = date.getDay();

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

type Days = {
  date: Date;
  isCurrentMonth?: boolean;
  isToday?: boolean;
  isSelected?: boolean;
}[];

const Teacher: NextPage = () => {
  const { name } = useRouter().query as { name: string };

  const container = useRef(null);
  const containerNav = useRef(null);

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
        eventsByDate[date.toISOString()] = lessonsGrouped.map((lesson) => ({
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
          {/* Header with date */}
          <header className="relative z-20 flex flex-none items-center justify-between border-b border-gray-200 py-4 px-6">
            <div>
              <h1 className="text-lg font-semibold leading-6 text-gray-900">
                <time className="sm:hidden" dateTime="2022-01-22">
                  {/* by selected date */}
                  {selectedDate.toLocaleDateString("ru-RU", {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })}
                </time>
                <time dateTime="2022-01-22" className="hidden sm:inline">
                  {selectedDate.toLocaleDateString("ru-RU", {
                    month: "long",
                    day: "numeric",
                    year: "numeric",
                  })}
                </time>
              </h1>
              <p className="mt-1 text-sm text-gray-500">
                {selectedDate.toLocaleDateString("ru-RU", {
                  weekday: "long",
                })}{" "}
                {getWeekByDate(selectedDate)} неделя
              </p>
            </div>
          </header>
          <div className="flex flex-auto overflow-hidden bg-white">
            <div
              ref={container}
              className="flex flex-auto flex-col overflow-auto"
            >
              <div
                ref={containerNav}
                className="sticky top-0 z-10 grid flex-none grid-cols-7 bg-white text-xs text-gray-500 shadow ring-1 ring-black ring-opacity-5 md:hidden"
              >
                {getWeekDaysByDate(selectedDate).map((day, index) => (
                  <button
                    key={index}
                    type="button"
                    className={classNames(
                      "flex flex-col items-center pt-3 pb-1.5",
                      selectedDate.getDate() === day.getDate()
                        ? "bg-gray-100 text-gray-900"
                        : "text-gray-700"
                    )}
                    onClick={() => setSelectedDate(day)}
                  >
                    <span>
                      {day.toLocaleString("ru", { weekday: "short" })}
                    </span>
                    <span className="mt-3 flex h-8 w-8 items-center justify-center rounded-full text-base font-semibold text-gray-900">
                      {day.getDate()}
                    </span>
                  </button>
                ))}
              </div>
              <ol className="mt-4 divide-y divide-gray-100 text-sm leading-6 lg:col-span-7 xl:col-span-8">
                {/* if teacher, then map it lessons */}
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
                              <ClockIcon
                                className="h-5 w-5 text-gray-400"
                                aria-hidden="true"
                              />
                            </dt>
                            <dd>{lesson.calls.num} пара</dd>
                          </div>
                          <div className="mt-2 flex items-start space-x-3 xl:mt-0 xl:ml-3.5 xl:border-l xl:border-gray-400 xl:border-opacity-50 xl:pl-3.5">
                            <dt className="mt-0.5">
                              <span className="sr-only">Дата</span>
                              <CalendarIcon
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
                          <div className="mt-2 flex items-start space-x-3 xl:mt-0 xl:ml-3.5 xl:border-l xl:border-gray-400 xl:border-opacity-50 xl:pl-3.5">
                            <dt className="mt-0.5">
                              <span className="sr-only">Аудитория</span>
                              <MapIcon
                                className="h-5 w-5 text-gray-400"
                                aria-hidden="true"
                              />
                            </dt>
                            <dd>{lesson.room?.name}</dd>
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
