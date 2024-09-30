## EasyICS

### Overview

EasyICS is a tool designed to convert CSV-formatted event lists into standard .ics calendar files.

### Input Format

The input CSV file (events.csv) must be structured as follows:

| Column Name  | Description                                                                                                                             |
| ------------ | --------------------------------------------------------------------------------------------------------------------------------------- |
| Title        | Brief description of the event (e.g., "F1: Mexican Grand Prix Qualifying" or "Premier League: Manchester United vs. Tottenham Hotspur") |
| Location     | City and venue (e.g., "Manchester - Old Trafford Stadium")                                                                              |
| Date         | Event date in YYYY.MM.DD format (e.g., "2024.01.28")                                                                                    |
| Time         | Start time in 24-hour format hh:mm (e.g., "18:00")                                                                                      |
| Duration     | Event duration in hours (e.g., "2" or "10")                                                                                             |
| Notification | Default value: 15                                                                                                                       |

### Sample CSV Format

```
csv title,location(city-venue),date(YYYY.MM.DD),time(hh:mm),duration(h or hh),notification(m or mm)
EFL Cup Round 4: Tottenham Hotspur vs Manchester City,Tottenham - Tottenham Hotspur Stadium,2024.10.30,20:45,2,15
MotoGP: Australian Grand Prix,Phillip Island - Phillip Island Circuit,2024.10.20,05:00,2,15
```

### Output

The tool generates a .ics file containing the event details in a standardized calendar format.

### Usage

1. Prepare your CSV file (events.csv) in the projects main directory with event information according to the specified format.
2. Run `main.py`.
3. The resulting .ics file will be saved to the Desktop.

### Packages

Use `pip install requirements.txt` to install the packages used or install them separately:

-   `pip install tzlocal`
-   `pip install pytz`
-   `pip install ics`

### Future Plans

-   GUI for easier use
-   Flexible paths
