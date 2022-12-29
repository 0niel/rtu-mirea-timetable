import { type NextPage } from "next";
import Head from "next/head";
import Link from "next/link";
import Image from "next/image";

// import { Popover, Transition } from '@headlessui/react'
// import { MenuIcon, XIcon } from '@heroicons/react/outline'
import { ArrowSmallRightIcon } from "@heroicons/react/20/solid";
import { Fragment, useEffect, useRef, useState } from "react";
import {
  ChevronDownIcon,
  ChevronLeftIcon,
  ChevronRightIcon,
} from "@heroicons/react/20/solid";
import axios from "axios";
import { useQuery } from "react-query";
import { paths } from "../api/schemas/openapi";
import { components } from "../api/schemas/openapi";
import { getWeek, getWeekByDate } from "../utils";

import { Menu, Transition } from "@headlessui/react";
import { config } from "process";

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
axios.defaults.baseURL = "https://timetable.mirea.ru";
const getSchedule = async (group: string) => {
  const url = "/api/groups/{name}";

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
  const week = getWeekByDate(date);
  const day = date.getDay() - 1;

  if (day === -1) {
    return [];
  }

  const newLessons = lessons.filter((lesson) => {
    return lesson.weeks.includes(week) && lesson.weekday === day;
  });

  console.log("NEW LESSONS", newLessons);

  return newLessons;
};

type Days = {
  date: Date;
  isCurrentMonth?: boolean;
  isToday?: boolean;
  isSelected?: boolean;
}[];

const Schedule: NextPage = () => {
  const container = useRef(null);
  const containerNav = useRef(null);
  const containerOffset = useRef(null);

  const currentDate = new Date();
  const [monthToDisplay, setMonthToDisplay] = useState(currentDate.getMonth());
  const [yearToDisplay, setYearToDisplay] = useState(currentDate.getFullYear());
  const [selectedDate, setSelectedDate] = useState(currentDate);
  const [days, setDays] = useState<Days>(
    generateDays(
      currentDate,
      currentDate.getMonth() + 1,
      currentDate.getFullYear()
    )
  );

  useEffect(() => {
    setDays(
      days.map((d) => {
        if (
          d.date?.getDate() === selectedDate.getDate() &&
          d.date?.getMonth() === selectedDate.getMonth() &&
          d.date?.getFullYear() === selectedDate.getFullYear()
        ) {
          return { ...d, isSelected: true };
        }
        return { ...d, isSelected: false };
      })
    );
  }, [selectedDate]);

  const [schedule, setSchedule] = useState<
    components["schemas"]["Group"] | null
  >(null);

  useQuery("schedule", () => getSchedule("ИКБО-30-20"), {
    onSuccess: (data) => {
      setSchedule(data);
    },
  });

  useEffect(() => {
    setDays(generateDays(currentDate, monthToDisplay + 1, yearToDisplay));
  }, [monthToDisplay, yearToDisplay]);

  useEffect(() => {
    // Set the container scroll position based on the current time.
    const currentMinute = new Date().getHours() * 60;

    if (container.current) {
      container.current.scrollTop =
        (currentMinute / 1440) * container.current.scrollHeight;
    }

    if (containerOffset.current) {
      containerOffset.current.scrollTop =
        (currentMinute / 1440) * containerOffset.current.scrollHeight;
    }
  }, []);

  const getLessonGridRow = (lesson: components["schemas"]["Lesson"]) => {
    const row = lesson.calls.num === 1 ? 2 : lesson.calls.num * 2;
    return `${row} / span 1`;
  };

  const getLessonTypeColor = (type: string) => {
    switch (type) {
      case "пр":
        return "bg-blue-100 text-blue-800";
      case "лек":
        return "bg-green-100 text-green-800";
      case "лаб":
        return "bg-yellow-100 text-yellow-800";
      case "зач":
        return "bg-red-100 text-red-800";
      default:
        return "bg-gray-100 text-gray-800";
    }
  };

  const getLessonTypeBackgroundColor = (type: string) => {
    switch (type) {
      case "пр":
        return "bg-blue-50 hover:bg-blue-100";
      case "лек":
        return "bg-green-50 hover:bg-green-100";
      case "лаб":
        return "bg-yellow-50 hover:bg-yellow-100";
      case "зач":
        return "bg-red-50 hover:bg-red-100";
      default:
        return "bg-gray-50 hover:bg-gray-100";
    }
  };

  const getWeekDaysByDate = (date: Date) => {
    const week = getWeek(date);

    const days = [];

    for (let i = 1; i <= 7; i++) {
      const day = new Date(date);
      day.setDate(day.getDate() - day.getDay() + i);
      days.push(day);
    }

    return days;
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
            <div className="flex items-center">
              <div className="flex items-center rounded-md shadow-sm md:items-stretch">
                <button
                  type="button"
                  className="flex items-center justify-center rounded-l-md border border-r-0 border-gray-300 bg-white py-2 pl-3 pr-4 text-gray-400 hover:text-gray-500 focus:relative md:w-9 md:px-2 md:hover:bg-gray-50"
                >
                  <span className="sr-only">Previous month</span>
                  <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
                </button>
                <button
                  type="button"
                  className="hidden border-t border-b border-gray-300 bg-white px-3.5 text-sm font-medium text-gray-700 hover:bg-gray-50 hover:text-gray-900 focus:relative md:block"
                >
                  Сегодня
                </button>
                <span className="relative -mx-px h-5 w-px bg-gray-300 md:hidden" />
                <button
                  type="button"
                  className="flex items-center justify-center rounded-r-md border border-l-0 border-gray-300 bg-white py-2 pl-4 pr-3 text-gray-400 hover:text-gray-500 focus:relative md:w-9 md:px-2 md:hover:bg-gray-50"
                >
                  <span className="sr-only">Next month</span>
                  <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>
              <div className="hidden md:ml-4 md:flex md:items-center">
                <Menu as="div" className="relative">
                  <Menu.Button
                    type="button"
                    className="flex items-center rounded-md border border-gray-300 bg-white py-2 pl-3 pr-2 text-sm font-medium text-gray-700 shadow-sm hover:bg-gray-50"
                  >
                    Просмотр дня
                    <ChevronDownIcon
                      className="ml-2 h-5 w-5 text-gray-400"
                      aria-hidden="true"
                    />
                  </Menu.Button>

                  <Transition
                    as={Fragment}
                    enter="transition ease-out duration-100"
                    enterFrom="transform opacity-0 scale-95"
                    enterTo="transform opacity-100 scale-100"
                    leave="transition ease-in duration-75"
                    leaveFrom="transform opacity-100 scale-100"
                    leaveTo="transform opacity-0 scale-95"
                  >
                    <Menu.Items className="absolute right-0 mt-3 w-36 origin-top-right overflow-hidden rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                      <div className="py-1">
                        <Menu.Item>
                          {({ active }) => (
                            <a
                              href="#"
                              className={classNames(
                                active
                                  ? "bg-gray-100 text-gray-900"
                                  : "text-gray-700",
                                "block px-4 py-2 text-sm"
                              )}
                            >
                              Day view
                            </a>
                          )}
                        </Menu.Item>
                        <Menu.Item>
                          {({ active }) => (
                            <a
                              href="#"
                              className={classNames(
                                active
                                  ? "bg-gray-100 text-gray-900"
                                  : "text-gray-700",
                                "block px-4 py-2 text-sm"
                              )}
                            >
                              Week view
                            </a>
                          )}
                        </Menu.Item>
                        <Menu.Item>
                          {({ active }) => (
                            <a
                              href="#"
                              className={classNames(
                                active
                                  ? "bg-gray-100 text-gray-900"
                                  : "text-gray-700",
                                "block px-4 py-2 text-sm"
                              )}
                            >
                              Month view
                            </a>
                          )}
                        </Menu.Item>
                        <Menu.Item>
                          {({ active }) => (
                            <a
                              href="#"
                              className={classNames(
                                active
                                  ? "bg-gray-100 text-gray-900"
                                  : "text-gray-700",
                                "block px-4 py-2 text-sm"
                              )}
                            >
                              Year view
                            </a>
                          )}
                        </Menu.Item>
                      </div>
                    </Menu.Items>
                  </Transition>
                </Menu>
              </div>
              <Menu as="div" className="relative ml-6 md:hidden">
                <Menu.Button className="-mx-2 flex items-center rounded-full border border-transparent p-2 text-gray-400 hover:text-gray-500">
                  <span className="sr-only">Открыть меню</span>

                  <svg
                    xmlns="http://www.w3.org/2000/svg"
                    className="h-5 w-5"
                    aria-hidden="true"
                    role="img"
                    id="footer-sample-full"
                    width="1em"
                    height="1em"
                    preserveAspectRatio="xMidYMid meet"
                    viewBox="0 0 24 24"
                  >
                    <path
                      fill="currentColor"
                      d="M16 12a2 2 0 0 1 2-2a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2m-6 0a2 2 0 0 1 2-2a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2m-6 0a2 2 0 0 1 2-2a2 2 0 0 1 2 2a2 2 0 0 1-2 2a2 2 0 0 1-2-2Z"
                    ></path>
                  </svg>
                </Menu.Button>

                <Transition
                  as={Fragment}
                  enter="transition ease-out duration-100"
                  enterFrom="transform opacity-0 scale-95"
                  enterTo="transform opacity-100 scale-100"
                  leave="transition ease-in duration-75"
                  leaveFrom="transform opacity-100 scale-100"
                  leaveTo="transform opacity-0 scale-95"
                >
                  <Menu.Items className="absolute right-0 mt-3 w-36 origin-top-right divide-y divide-gray-100 overflow-hidden rounded-md bg-white shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none">
                    <div className="py-1">
                      <Menu.Item>
                        {({ active }) => (
                          <a
                            href="#"
                            className={classNames(
                              active
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "block px-4 py-2 text-sm"
                            )}
                          >
                            Create event
                          </a>
                        )}
                      </Menu.Item>
                    </div>
                    <div className="py-1">
                      <Menu.Item>
                        {({ active }) => (
                          <a
                            href="#"
                            className={classNames(
                              active
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "block px-4 py-2 text-sm"
                            )}
                          >
                            Экспорт в календарь
                          </a>
                        )}
                      </Menu.Item>
                    </div>
                    <div className="py-1">
                      <Menu.Item>
                        {({ active }) => (
                          <a
                            href="#"
                            className={classNames(
                              active
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "block px-4 py-2 text-sm"
                            )}
                          >
                            День
                          </a>
                        )}
                      </Menu.Item>
                      <Menu.Item>
                        {({ active }) => (
                          <a
                            href="#"
                            className={classNames(
                              active
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "block px-4 py-2 text-sm"
                            )}
                          >
                            Неделя
                          </a>
                        )}
                      </Menu.Item>
                      <Menu.Item>
                        {({ active }) => (
                          <a
                            href="#"
                            className={classNames(
                              active
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "block px-4 py-2 text-sm"
                            )}
                          >
                            Месяц
                          </a>
                        )}
                      </Menu.Item>
                      <Menu.Item>
                        {({ active }) => (
                          <a
                            href="#"
                            className={classNames(
                              active
                                ? "bg-gray-100 text-gray-900"
                                : "text-gray-700",
                              "block px-4 py-2 text-sm"
                            )}
                          >
                            Год
                          </a>
                        )}
                      </Menu.Item>
                    </div>
                  </Menu.Items>
                </Transition>
              </Menu>
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
                    <div ref={containerOffset} className="row-end-1 h-7"></div>
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
                    {/* for lesson in schedule.lessons if schedule != null */}
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
                            <a
                              href="#"
                              className={
                                "group absolute inset-1 flex flex-col overflow-y-auto rounded-lg p-2 text-xs leading-5 " +
                                getLessonTypeBackgroundColor(
                                  lesson.lesson_type?.name
                                )
                              }
                            >
                              <div className="flex font-medium text-blue-600">
                                <div className="ml-2 flex flex-auto flex-col">
                                  <p className="text-sm font-medium text-gray-900">
                                    {lesson.discipline.name}
                                  </p>
                                  <p className="text-sm text-gray-500">
                                    {lesson.teachers
                                      .map((teacher) => teacher.name)
                                      .join(", ")}
                                  </p>

                                  <p className="text-sm font-medium text-gray-900">
                                    {lesson.room?.name}
                                  </p>
                                </div>

                                <p className="text-sm text-gray-500">
                                  <span
                                    className={
                                      "inline-flex items-center rounded-full px-2.5 py-0.5 text-xs font-medium " +
                                      getLessonTypeColor(
                                        lesson.lesson_type?.name
                                      )
                                    }
                                  >
                                    {lesson.lesson_type?.name}
                                  </span>
                                </p>
                              </div>
                            </a>
                          </li>
                        )
                      )}
                  </ol>
                </div>
              </div>
            </div>
            <div className="hidden w-1/2 max-w-md flex-none border-l border-gray-100 py-10 px-8 md:block">
              <div className="flex items-center text-center text-gray-900">
                <button
                  type="button"
                  className="-m-1.5 flex flex-none items-center justify-center p-1.5 text-gray-400 hover:text-gray-500"
                  onClick={() => {
                    if (monthToDisplay === 0) {
                      setMonthToDisplay(11);
                      setYearToDisplay(yearToDisplay - 1);
                    } else {
                      setMonthToDisplay(monthToDisplay - 1);
                    }
                  }}
                >
                  <span className="sr-only">Предыдущий месяц</span>
                  <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
                </button>
                <div className="flex-auto font-semibold">
                  {new Date(yearToDisplay, monthToDisplay)
                    .toLocaleString("ru", {
                      month: "long",
                      year: "numeric",
                    })
                    .charAt(0)
                    .toUpperCase() +
                    new Date(yearToDisplay, monthToDisplay)
                      .toLocaleString("ru", {
                        month: "long",
                        year: "numeric",
                      })
                      .slice(1)}
                </div>
                <button
                  type="button"
                  className="-m-1.5 flex flex-none items-center justify-center p-1.5 text-gray-400 hover:text-gray-500"
                  onClick={() => {
                    if (monthToDisplay === 11) {
                      setMonthToDisplay(0);
                      setYearToDisplay(yearToDisplay + 1);
                    } else {
                      setMonthToDisplay(monthToDisplay + 1);
                    }
                  }}
                >
                  <span className="sr-only">Следующий месяц</span>
                  <ChevronRightIcon className="h-5 w-5" aria-hidden="true" />
                </button>
              </div>
              <div className="mt-6 grid grid-cols-7 text-center text-xs leading-6 text-gray-500">
                <div>ПН</div>
                <div>ВТ</div>
                <div>СР</div>
                <div>ЧТ</div>
                <div>ПТ</div>
                <div>СБ</div>
                <div>ВС</div>
              </div>
              <div className="isolate mt-2 grid grid-cols-7 gap-px rounded-lg bg-gray-200 text-sm shadow ring-1 ring-gray-200">
                {days.map((day, dayIdx) => (
                  <button
                    key={day.date}
                    type="button"
                    className={classNames(
                      "py-1.5 hover:bg-gray-100 focus:z-10",
                      day.isCurrentMonth ? "bg-white" : "bg-gray-50",
                      (day.isSelected || day.isToday) && "font-semibold",
                      day.isSelected && "text-white",
                      !day.isSelected &&
                        day.isCurrentMonth &&
                        !day.isToday &&
                        "text-gray-900",
                      !day.isSelected &&
                        !day.isCurrentMonth &&
                        !day.isToday &&
                        "text-gray-400",
                      day.isToday && !day.isSelected && "text-indigo-600",
                      dayIdx === 0 && "rounded-tl-lg",
                      dayIdx === 6 && "rounded-tr-lg",
                      dayIdx === days.length - 7 && "rounded-bl-lg",
                      dayIdx === days.length - 1 && "rounded-br-lg"
                    )}
                    onClick={() => {
                      setSelectedDate(day.date);
                    }}
                  >
                    <time
                      dateTime={day.date}
                      className={classNames(
                        "mx-auto flex h-7 w-7 items-center justify-center rounded-full",
                        day.isSelected && day.isToday && "bg-indigo-600",
                        day.isSelected && !day.isToday && "bg-gray-900"
                      )}
                    >
                      {day.date?.getDate()}
                    </time>
                  </button>
                ))}
              </div>
            </div>
          </div>
        </div>
      </div>
    </>
  );
};

export default Schedule;
