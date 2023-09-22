import Link from "next/link";
import type { components } from "../api/schemas/openapi";

interface RoomsLinksProps {
  room: components["schemas"]["Room"];
  selectedDate: Date;
}

const RoomsLinks = ({ room, selectedDate }: RoomsLinksProps) => {
  return (
    <div className="flex flex-row flex-wrap items-center space-x-3.5">
      {room.name.split(",").map((roomName) => (
        <span key={roomName}>
          <Link
            target="_blank"
            className="flex cursor-pointer items-start space-x-3 text-blue-600 hover:text-blue-500"
            href={`https://map.mirea.ru/?room=${roomName}&campus=${
              room.campus?.short_name
            }&date=${selectedDate.toISOString()}`}
          >
            {roomName}
          </Link>
        </span>
      ))}
    </div>
  );
};

export default RoomsLinks;
