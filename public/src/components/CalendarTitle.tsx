import { ChevronLeftIcon, ChevronRightIcon } from "@heroicons/react/20/solid";
import { getAcademicWeek } from "../utils";
import ComboboxGroups from "./ComboboxGroups";

interface CalendarTitleProps {
  onClickLeft: () => void;
  onClickRight: () => void;
  selectedDate: Date;

  selectedGroups: string[];
  setSelectedGroups: (groups: string[]) => void;
  availableGroups: string[];
}

const lessonsForCompareColorsClassNames = [
  "bg-blue-300 hover:bg-blue-700",
  "bg-green-300 hover:bg-green-700",
  "bg-yellow-300 hover:bg-yellow-700",
];

const CalendarTitle = (props: CalendarTitleProps) => {
  return (
    <>
      <header className="relative z-20 mx-2 flex flex-none items-center justify-between border-b border-gray-200 py-4 sm:px-6">
        <button type="button" className="md:hidden">
          <ChevronLeftIcon
            className="mr-1 h-6 w-6 text-gray-400 hover:text-gray-500"
            aria-hidden="true"
            onClick={props.onClickLeft}
          />
        </button>

        <div className="flex w-full flex-row items-center justify-between">
          <div>
            <h1 className="text-sm font-semibold text-gray-900 sm:text-lg sm:leading-6">
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

            <p className="mt-0 text-sm text-gray-500 sm:mt-1">
              {props.selectedDate.toLocaleDateString("ru-RU", {
                weekday: "long",
              })}{" "}
              {getAcademicWeek(props.selectedDate)} неделя
            </p>
          </div>

          {props.selectedGroups.length > 0 && (
            <ComboboxGroups
              availableGroups={props.availableGroups}
              selectedGroups={props.selectedGroups}
              setSelectedGroups={props.setSelectedGroups}
            />
          )}
        </div>

        <button type="button" className="md:hidden">
          <ChevronRightIcon
            className="ml-1 h-6 w-6 text-gray-400 hover:text-gray-500"
            aria-hidden="true"
            onClick={props.onClickRight}
          />
        </button>
      </header>
      {props.selectedGroups.length > 1 && (
        <div className="flex flex-row items-center px-2 py-2">
          {props.selectedGroups.map((group, index) => (
            <div className="flex flex-row items-center px-2" key={group}>
              <div
                className={
                  lessonsForCompareColorsClassNames[index] +
                  " h-2 w-2 rounded-full"
                }
              ></div>
              <div className="ml-1 text-sm text-gray-800">{group}</div>
            </div>
          ))}
        </div>
      )}
    </>
  );
};
export default CalendarTitle;
