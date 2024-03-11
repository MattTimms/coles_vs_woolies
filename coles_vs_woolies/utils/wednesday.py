from datetime import date, datetime


def get_next_wednesday() -> datetime:
    year, week, weekday = datetime.now().isocalendar()
    week += weekday > 2
    return datetime.fromisocalendar(year, week, 3)


def get_last_wednesday() -> datetime:
    year, week, weekday = datetime.now().isocalendar()
    week -= weekday < 3
    return datetime.fromisocalendar(year, week, 3)


def get_week_of_month() -> str:
    # Get the current date and month
    current_date = date.today()
    current_month = current_date.strftime("%B")  # Get the full month name (e.g., August)

    # Determine the week number for the current date
    first_day_of_month = current_date.replace(day=1)
    week_number = (current_date - first_day_of_month).days // 7 + 1

    match week_number:
        case 1:
            week_text = "First"
        case 2:
            week_text = "Second"
        case 3:
            week_text = "Third"
        case _:
            week_text = "Last"

    # Construct the desired text format
    return f"{week_text} week of {current_month}"
