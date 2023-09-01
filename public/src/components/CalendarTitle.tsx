import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";
import { getWeekByDate } from "../utils";

interface CalendarTitleProps {
  onClickLeft: () => void;
  onClickRight: () => void;
  selectedDate: Date;
}

const CalendarTitle = (props: CalendarTitleProps) => {
  return (
    <header className="relative z-20 flex flex-none items-center justify-between border-b border-gray-200 py-4 px-6">
      <button type="button" className="md:hidden">
        <ChevronLeftIcon
          className="h-6 w-6 text-gray-400 hover:text-gray-500"
          aria-hidden="true"
          onClick={props.onClickLeft}
        />
      </button>
      <div>
        <h1 className="text-lg font-semibold leading-6 text-gray-900">
          <time
            className="sm:hidden"
            dateTime={props.selectedDate.toISOString()}
          >
            {props.selectedDate.toLocaleDateString("ru-RU", {
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </time>
          <time dateTime="2023-09-01" className="hidden sm:inline">
            {props.selectedDate.toLocaleDateString("ru-RU", {
              month: "long",
              day: "numeric",
              year: "numeric",
            })}
          </time>
        </h1>
        <p className="mt-1 text-sm text-gray-500">
          {props.selectedDate.toLocaleDateString("ru-RU", {
            weekday: "long",
          })}{" "}
          {getWeekByDate(props.selectedDate)} неделя
        </p>
      </div>
      <button type="button" className="md:hidden">
        <ChevronRightIcon
          className="h-6 w-6 text-gray-400 hover:text-gray-500"
          aria-hidden="true"
          onClick={props.onClickRight}
        />
      </button>
    </header>
  );
};
export default CalendarTitle;
