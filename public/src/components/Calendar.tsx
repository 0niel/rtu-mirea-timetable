import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";
import { useEffect, useState } from "react";
import { classNames } from "../utils";

export const getColorByEvent = (event: { name: string }) => {
  switch (event.name) {
    case "пр":
      return "bg-blue-400";
    case "лек":
      return "bg-green-400";
    case "лаб":
      return "bg-yellow-400";
    case "зач":
      return "bg-red-400";
    default:
      return "bg-gray-400";
  }
};

type Days = {
  date: Date;
  isCurrentMonth?: boolean;
  isToday?: boolean;
  isSelected?: boolean;
}[];

interface CalendarProps {
  selectedDate: Date;
  setSelectedDate: (date: Date) => void;

  monthToDisplay: number;
  setMonthToDisplay: (month: number) => void;

  yearToDisplay: number;
  setYearToDisplay: (year: number) => void;

  // key - isoString даты
  eventsByDate: { [key: string]: { name: string }[] };
}

export const Calendar = (props: CalendarProps) => {
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

  useEffect(() => {
    setDays(
      generateDays(
        props.selectedDate,
        props.monthToDisplay + 1,
        props.yearToDisplay
      )
    );
  }, [props.monthToDisplay, props.yearToDisplay]);

  useEffect(() => {
    const selectedDate = props.selectedDate;
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
  }, [props.selectedDate]);

  const [days, setDays] = useState<Days>(
    generateDays(
      props.selectedDate,
      props.selectedDate.getMonth() + 1,
      props.selectedDate.getFullYear()
    )
  );

  return (
    <div className="hidden w-1/2 max-w-md flex-none border-l border-gray-100 py-10 px-8 md:block">
      <div className="flex items-center text-center text-gray-900">
        <button
          type="button"
          className="-m-1.5 flex flex-none items-center justify-center p-1.5 text-gray-400 hover:text-gray-500"
          onClick={() => {
            if (props.monthToDisplay === 0) {
              props.setMonthToDisplay(11);
              props.setYearToDisplay(props.yearToDisplay - 1);
            } else {
              props.setMonthToDisplay(props.monthToDisplay - 1);
            }
          }}
        >
          <span className="sr-only">Предыдущий месяц</span>
          <ChevronLeftIcon className="h-5 w-5" aria-hidden="true" />
        </button>
        <div className="flex-auto font-semibold">
          {new Date(props.yearToDisplay, props.monthToDisplay)
            .toLocaleString("ru", {
              month: "long",
              year: "numeric",
            })
            .charAt(0)
            .toUpperCase() +
            new Date(props.yearToDisplay, props.monthToDisplay)
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
            if (props.monthToDisplay === 11) {
              props.setMonthToDisplay(0);
              props.setYearToDisplay(props.yearToDisplay + 1);
            } else {
              props.setMonthToDisplay(props.monthToDisplay + 1);
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
            key={dayIdx}
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
              props.setSelectedDate(day.date);
            }}
          >
            <time
              dateTime={day.date?.toISOString()}
              className={classNames(
                "mx-auto flex h-7 w-7 items-center justify-center rounded-full",
                day.isSelected && day.isToday && "bg-indigo-600",
                day.isSelected && !day.isToday && "bg-gray-900"
              )}
            >
              {day.date?.getDate()}
            </time>

            <div className="flex flex-row justify-center">
              {props.eventsByDate[day.date?.toISOString().split("T")[0]] !==
                undefined &&
                props.eventsByDate[day.date?.toISOString().split("T")[0]]?.map(
                  (event, eventIdx) => (
                    <div
                      key={eventIdx}
                      className={classNames(
                        "mx-0.5 mt-1 h-1.5 w-1.5 rounded-full",
                        getColorByEvent(event)
                      )}
                    ></div>
                  )
                )}
            </div>
          </button>
        ))}
      </div>
    </div>
  );
};
