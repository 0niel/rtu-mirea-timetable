import { useState } from "react";
import { CheckIcon, ChevronUpDownIcon } from "@heroicons/react/20/solid";
import { Combobox } from "@headlessui/react";

function classNames(...classes: (string | boolean)[]) {
  return classes.filter(Boolean).join(" ");
}

interface ComboboxProps {
  availableGroups: string[];
  selectedGroups: string[];
  setSelectedGroups: (items: string[]) => void;
}

export default function ComboboxGroups(props: ComboboxProps) {
  const [query, setQuery] = useState("");

  const filtredGroups = props.availableGroups
    .filter((group) => group.toLowerCase().includes(query.toLowerCase()))

    .sort((a, b) => {
      // Сначала выбранные группы, потом остальные
      if (
        props.selectedGroups.includes(a) &&
        !props.selectedGroups.includes(b)
      ) {
        return -1;
      } else if (
        !props.selectedGroups.includes(a) &&
        props.selectedGroups.includes(b)
      ) {
        return 1;
      } else {
        return 0;
      }
    })
    .sort((a, b) => {
      // Первый элемент в props.selectedGroups должен быть первым в списке
      if (props.selectedGroups.includes(a)) {
        return -1;
      } else if (props.selectedGroups.includes(b)) {
        return 1;
      } else {
        return 0;
      }
    })
    .slice(0, 30);

  console.log(props.selectedGroups);

  const isSelected = (group: string) => {
    return props.selectedGroups.includes(group);
  };

  return (
    <Combobox
      as="div"
      value={props.selectedGroups}
      onChange={(item: any) => {
        if (props.selectedGroups.includes(item)) {
          props.setSelectedGroups(
            props.selectedGroups.filter((group) => group !== item)
          );
        } else if (props.selectedGroups.length < 3) {
          props.setSelectedGroups([...props.selectedGroups, item]);
        }
      }}
      className="max-w-sm sm:max-w-xs"
    >
      {/* <Combobox.Label className="block text-sm font-medium text-gray-700">
        Группы
      </Combobox.Label> */}
      <div className="relative mt-1">
        <Combobox.Input
          className="w-full rounded-md border border-gray-300 bg-white py-1 shadow-sm focus:border-blue-500 focus:outline-none focus:ring-1 focus:ring-blue-500 sm:pl-3 sm:pr-2 sm:text-sm"
          onChange={(event) => setQuery(event.target.value)}
          displayValue={() => {
            return props.selectedGroups.join(", ");
          }}
        />
        <Combobox.Button className="absolute inset-y-0 right-0 flex items-center rounded-r-md px-2 focus:outline-none">
          <ChevronUpDownIcon
            className="h-5 w-5 text-gray-400"
            aria-hidden="true"
          />
        </Combobox.Button>

        {filtredGroups.length > 0 && (
          <Combobox.Options className="absolute z-10 mt-1 max-h-60 w-full overflow-auto rounded-md bg-white py-1 text-base shadow-lg ring-1 ring-black ring-opacity-5 focus:outline-none sm:text-sm">
            {filtredGroups.map((group, groupIdx) => (
              <Combobox.Option
                key={groupIdx}
                value={group}
                className={({ active }) =>
                  classNames(
                    "relative cursor-default select-none py-2 pl-8 pr-4",
                    active ? "bg-indigo-600 text-white" : "text-gray-900"
                  )
                }
              >
                {({ active, selected }) => (
                  <>
                    {!isSelected(group) && props.selectedGroups.length == 3 && (
                      <span
                        className={classNames(
                          "pointer-events-none block cursor-default truncate text-gray-300",
                          isSelected(group) && "font-semibold"
                        )}
                      >
                        {group}
                      </span>
                    )}

                    {!isSelected(group) && props.selectedGroups.length < 3 && (
                      <span
                        className={classNames(
                          "block truncate",
                          isSelected(group) && "font-semibold"
                        )}
                      >
                        {group}
                      </span>
                    )}

                    {isSelected(group) && (
                      <>
                        <span
                          className={classNames(
                            "absolute inset-y-0 left-0 flex items-center pl-1.5 text-blue-500"
                          )}
                        >
                          <CheckIcon className="h-5 w-5" aria-hidden="true" />
                        </span>
                        <span className="block truncate font-semibold">
                          {group}
                        </span>
                      </>
                    )}
                  </>
                )}
              </Combobox.Option>
            ))}
          </Combobox.Options>
        )}
      </div>
    </Combobox>
  );
}
