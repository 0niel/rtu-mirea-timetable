import React from "react";
import { classNames, getWeekDaysByDate } from "../utils";
import { getColorByEvent } from "./Calendar";

interface CalendarHeaderProps {
  selectedDate: Date;
  setSelectedDate: (date: Date) => void;

  // key - isoString даты
  eventsByDate: { [key: string]: { name: string }[] };
}

const getDayString = (day: Date) => {
  return day.toISOString().split("T")[0] ?? "";
};

export const CalendarHeader = (props: CalendarHeaderProps) => {
  return (
    <div className="sticky top-0 z-10 grid flex-none grid-cols-7 bg-white text-xs text-gray-500 shadow ring-1 ring-black ring-opacity-5 md:hidden">
      {getWeekDaysByDate(props.selectedDate).map((day, index) => (
        <button
          key={index}
          type="button"
          className={classNames(
            "flex flex-col items-center pt-3 pb-1.5",
            props.selectedDate.getDate() === day.getDate()
              ? "bg-gray-100 text-gray-900"
              : "text-gray-700"
          )}
          onClick={() => props.setSelectedDate(day)}
        >
          <span>{day.toLocaleString("ru", { weekday: "short" })}</span>
          <span className="mt-3 flex h-8 w-8 items-center justify-center rounded-full text-base font-semibold text-gray-900">
            {day.getDate()}
          </span>
          <div className="flex flex-row justify-center">
            {props.eventsByDate[getDayString(day)]?.map((event, eventIdx) => (
              <div
                key={eventIdx}
                className={classNames(
                  "mx-0.5 mt-1 h-1.5 w-1.5 rounded-full",
                  getColorByEvent(event)
                )}
              ></div>
            ))}
          </div>
        </button>
      ))}
    </div>
  );
};
