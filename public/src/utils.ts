export function classNames(...classes: unknown[]) {
    return classes.filter(Boolean).join(" ");
}

// Returns the week number for this date. ISO 8601 week number
export function getWeek(date: Date) {
    const d = new Date(Date.UTC(date.getFullYear(), date.getMonth(), date.getDate()));
    const dayNum = d.getUTCDay() || 7;
    d.setUTCDate(d.getUTCDate() + 4 - dayNum);
    const yearStart = new Date(Date.UTC(d.getUTCFullYear(), 0, 1));
    return Math.ceil((((d.getTime() - yearStart.getTime()) / 86400000) + 1) / 7);
}

export function getWeekByDate(date: Date) {
    // 9 февраля 2023 года
    const start_date = new Date(2023, 9, 1);
    const now = date;

    if (now < start_date) {
        return 1;
    }

    const week = getWeek(now) - getWeek(start_date);

    return week + 1;
}


export function getWeekDaysByDate(date: Date) {
    const days = [];

    for (let i = 1; i <= 7; i++) {
        const day = new Date(date);
        if (date.getDay() === 0) {
            day.setDate(day.getDate() - day.getDay() + i - 7);
        } else {
            day.setDate(day.getDate() - day.getDay() + i);
        }
        days.push(day);
    }

    return days;
}

export function getLessonTypeColor(type: string) {
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
}

export function getLessonTypeBackgroundColor(type: string) {
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
}
