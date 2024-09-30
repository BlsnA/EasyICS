from ics import Event, Calendar, DisplayAlarm
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from tzlocal import get_localzone
import re
import os
import pytz

def set_end(begin: str, duration: str) -> datetime:
    end = begin + timedelta(hours=int(duration))
    
    return end  # e.g. "2024-09-09T14:00:00+02:00"


def is_date_dst(date: datetime) -> bool:
    user_timezone = str(get_localzone())
    timezone = pytz.timezone(user_timezone)
    localized_date = timezone.localize(date)     # Localize the date to the given timezone
    is_in_dst = localized_date.dst() != timedelta(0)     # Check if DST is active
    return is_in_dst


def set_begin(date: str, time: str) -> datetime:
    # get the offset from UTF of user 
    local_time = datetime.now()
    utc_time = datetime.now(ZoneInfo("UTC"))
    utc_offset = local_time.hour - utc_time.hour    

    is_current_date_dst = is_date_dst(local_time)
    event_date = datetime.strptime(date, "%Y.%m.%d") # format the event date for is_date_dst() check
    is_event_date_dst = is_date_dst(event_date)

    # adjust the time according to time changes
    # if current date and event time are in the same time change -> pass
    if (is_current_date_dst and is_event_date_dst) or (not is_current_date_dst and not is_event_date_dst):
        pass
    elif not is_current_date_dst and is_event_date_dst:
        utc_offset += 1
    elif is_current_date_dst and not is_event_date_dst:
        utc_offset -= 1

    formatted_date = date.replace(".", "-") # format date to iso format

    # round minutes to the earlier quarter hour, e.g.: 20:05 -> 20:00
    event_start_hours = time.split(":")[0] # minutes of event start, e.g.: 20
    event_start_minutes = time.split(":")[1] # minutes of event start, e.g.: 45

    if int(event_start_minutes) < 15:
        event_start_time = f"{event_start_hours}:00:00"
    elif int(event_start_minutes) < 30:
        event_start_time = f"{event_start_hours}:15:00"
    elif int(event_start_minutes) < 45:
        event_start_time = f"{event_start_hours}:30:00"
    elif int(event_start_minutes) < 60:
        event_start_time = f"{event_start_hours}:45:00"
    else:
        raise Exception("Invalid Start Time")

    if utc_offset >= 0:
        formatted_time = f"T{event_start_time}+0{utc_offset}:00" # format timestamp to iso format
    else:
        formatted_time = f"T{event_start_time}-0{utc_offset}:00" # format timestamp to iso format
    
    begin = datetime.fromisoformat(formatted_date + formatted_time)

    return begin # e.g. "2024-09-09T12:00:00+02:00"


def validate_event(event: str):
    event = event.replace("\n", "") # remove newline
    event_components = event.split(",")
    assert len(event_components) == 6, f"The event is not correctly formatted. Must have 6 columns but found {len(event_components)}"
    
    # date
    assert re.match(r"\d\d\d\d[.]\d\d[.]\d\d", event_components[2].strip()), f"The event date '{event_components[2]}' does not match the required pattern 'YYYY.MM.DD' (e.g. 2024.12.01). Please revise the input csv."
    # starttime
    assert re.match(r"\d\d[:]\d\d", event_components[3].strip()), f"The event starttime '{event_components[3]}' does not match the required pattern 'hh:mm' (e.g. 12:00). Please revise the input csv."
    # duration
    assert re.match(r"\d", event_components[4].strip()) or re.match(r"\d\d", event_components[4].strip()), f"The event duration must match the required pattern 'h' or 'hh' (e.g. '2' or '10') lease revise the input csv."
    # notification
    assert re.match(r"\d", event_components[5].strip()) or re.match(r"\d\d", event_components[5].strip()), f"The time before the notification must match the required pattern 'm' or 'mm' (e.g. '5' or '15') lease revise the input csv."


def event_str_to_ics(event: str) -> Event:
    validate_event(event)
    event = event.replace("\n", "") # remove newline
    event_components = event.split(",")
    # assign event components to vars
    title = event_components[0].strip()
    location = event_components[1].strip()
    raw_date = event_components[2].strip()
    raw_starttime = event_components[3].strip()
    duration = event_components[4].strip()
    raw_notification = event_components[5].strip()
    
    # format vars as needed
    begin = set_begin(raw_date, raw_starttime)
    end = set_end(begin, duration)
    notification = [DisplayAlarm(trigger=timedelta(minutes=-int(raw_notification)))] # e.g. raw_notification == "15" => timedelta(minutes=-15)

    try:
        ics_event = Event(name=title, begin=begin, end=end, location=location, alarms=notification)
    except Exception as e:
        raise Exception("Error creating event", e)
    return ics_event


def write_events_to_calendar(events: str):
    calendar = Calendar()
    for event in events:
        if not event.rstrip("\n").strip(): # pass over empty lines
            continue
        ics_event = event_str_to_ics(event)
        calendar.events.add(ics_event)

    # throw error if no events are in the events.csv
    if not len(calendar.events):
        raise Exception("No events that can be created found!")

    return calendar



def load_events() -> list[str]:
    try:
        with open("events.csv", "r") as f:
            content = f.readlines()
    except FileNotFoundError:
        raise Exception("events.csv file is not at the correct location")
    except Exception as e:
        raise Exception("Something unexcepted happend!", e)
    
    # remove header row with the format info
    return content[1:]


def write_calendar_to_file(calendar: Calendar):
    username = os.getlogin()
    desktop_path = f"C:\\Users\\{username}\\Desktop"
    timestamp_for_filename = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    
    try:
        with open(f"{desktop_path}\\events_{timestamp_for_filename}.ics", "w") as f:
            f.writelines(calendar.serialize())
    except Exception as e:
        raise Exception("Something unexcepted happend while saving the calendar to the desktop!", e)


def write_log(calendar: Calendar):
    timestamp_for_log = datetime.now().strftime("%Y-%m-%d %H:%M:%S") # e.g.: 2024-09-29 18:22:31
    log_start = "############### LOG ENTRY START ###############\n"
    log_end = "############### LOG ENTRY END ###############\n"

    with open("log.txt", "a") as file:
        file.write(log_start)
        file.write(f"Created {len(calendar.events)} events on {timestamp_for_log}\n\n")
        for event in calendar.events:
            file.write(event.__repr__())
            event_string = str(event)
            file.write(event_string.replace("\n", "") + "\n") # remove all the newlines except the one at the end
            file.write("\n") # empty line after each event
        file.write(log_end)
        file.write("\n")


def main():
    events = load_events()
    calendar_with_events = write_events_to_calendar(events)
    write_calendar_to_file(calendar_with_events)
    print("Successfully created .ics file!")
    write_log(calendar_with_events)
    print("Successfully written to log.")


if __name__ == "__main__":
    main()