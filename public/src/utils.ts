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
    const start_date = new Date(2023, 1, 9);
    const now = date;

    if (now < start_date) {
        return 1;
    }

    const week = getWeek(now) - getWeek(start_date);

    return week + 1;
}
