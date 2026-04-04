#!/usr/bin/env python3

import csv
from datetime import datetime, time, timedelta
import matplotlib.pyplot as plt

# https://raw.githubusercontent.com/dleshem/israel-alerts-data/refs/heads/main/israel-alerts.csv
FILE = 'israel-alerts.csv'

print(f'Opening and reading {FILE}...')

with open(FILE, 'r', encoding='utf-8') as f:
    raw_data = f.read()

lines = raw_data.splitlines()

print(f'Done reading file! There are {len(lines)} lines.')

MISSILE_ALARM = [
    (1, '\u05d9\u05e8\u05d9 \u05e8\u05e7\u05d8\u05d5\u05ea \u05d5\u05d8\u05d9\u05dc\u05d9\u05dd'),
]
MISSILE_WARNING = [
    (14, '\u05d1\u05d3\u05e7\u05d5\u05ea \u05d4\u05e7\u05e8\u05d5\u05d1\u05d5\u05ea \u05e6\u05e4\u05d5\u05d9\u05d5\u05ea \u05dc\u05d4\u05ea\u05e7\u05d1\u05dc \u05d4\u05ea\u05e8\u05e2\u05d5\u05ea \u05d1\u05d0\u05d6\u05d5\u05e8\u05da'),
    (14, '\u05d1\u05d3\u05e7\u05d5\u05ea \u05d4\u05e7\u05e8\u05d5\u05d1\u05d5\u05ea \u05e6\u05e4\u05d5\u05d9\u05d5\u05ea \u05dc\u05d4\u05ea\u05e7\u05d1\u05dc \u05d4\u05ea\u05e8\u05e2\u05d5\u05ea \u05d1\u05d0\u05d9\u05d6\u05d5\u05e8\u05d9\u05dd \u05d4\u05d1\u05d0\u05d9\u05dd:'),
    (14, '\u05e9\u05d4\u05d9\u05d9\u05d4 \u05d1\u05e1\u05de\u05d9\u05db\u05d5\u05ea \u05dc\u05de\u05e8\u05d7\u05d1 \u05de\u05d5\u05d2\u05df'),
    (14, '\u05d9\u05e9 \u05dc\u05e9\u05d4\u05d5\u05ea \u05d1\u05e1\u05de\u05d9\u05db\u05d5\u05ea \u05dc\u05de\u05e8\u05d7\u05d1 \u05d4\u05de\u05d5\u05d2\u05df'),
]
MISSILE_MESSAGE = [
    (13, '\u05d9\u05e8\u05d9 \u05e8\u05e7\u05d8\u05d5\u05ea \u05d5\u05d8\u05d9\u05dc\u05d9\u05dd -  \u05d4\u05d0\u05d9\u05e8\u05d5\u05e2 \u05d4\u05e1\u05ea\u05d9\u05d9\u05dd'),
    (13, '\u05e0\u05d9\u05ea\u05df \u05dc\u05e6\u05d0\u05ea \u05de\u05d4\u05de\u05e8\u05d7\u05d1 \u05d4\u05de\u05d5\u05d2\u05df \u05d0\u05da \u05d9\u05e9 \u05dc\u05d4\u05d9\u05e9\u05d0\u05e8 \u05d1\u05e7\u05e8\u05d1\u05ea\u05d5'),
    (13, '\u05e1\u05d9\u05d5\u05dd \u05e9\u05d4\u05d9\u05d9\u05d4 \u05d1\u05e1\u05de\u05d9\u05db\u05d5\u05ea \u05dc\u05de\u05e8\u05d7\u05d1 \u05d4\u05de\u05d5\u05d2\u05df'),
    (13, '\u05d4\u05d0\u05d9\u05e8\u05d5\u05e2 \u05d4\u05e1\u05ea\u05d9\u05d9\u05dd'),
]
AIRCRAFT_INTRUSION_ALARM = [
    (2, '\u05d7\u05d3\u05d9\u05e8\u05ea \u05db\u05dc\u05d9 \u05d8\u05d9\u05e1 \u05e2\u05d5\u05d9\u05df'),
]
AIRCRAFT_INTRUSION_MESSAGE = [
    (13, '\u05d7\u05d3\u05d9\u05e8\u05ea \u05db\u05dc\u05d9 \u05d8\u05d9\u05e1 \u05e2\u05d5\u05d9\u05df - \u05d4\u05d0\u05d9\u05e8\u05d5\u05e2 \u05d4\u05e1\u05ea\u05d9\u05d9\u05dd'),
    (13, '\u05d4\u05d0\u05d9\u05e8\u05d5\u05e2 \u05d4\u05e1\u05ea\u05d9\u05d9\u05dd'),
]

ALL_CITIES = '\u05d1\u05e8\u05d7\u05d1\u05d9 \u05d4\u05d0\u05e8\u05e5'

# city name (in hebrew)
CITY = None

assert CITY is not None

DATE_FMT = '%d.%m.%YT%H:%M:%S'

# date range (dd.mm.yyyyThh:mm:ss)
START_DATE = None
END_DATE = None

assert START_DATE is not None
assert END_DATE is not None

MISSILES = True
AIRCRAFT_INTRUSION = True

# TODO deal with daylight saving time properly
# TODO handle timezones properly

start_date = datetime.strptime(START_DATE, DATE_FMT)
if END_DATE != '':
    end_date = datetime.strptime(END_DATE, DATE_FMT)
else:
    end_date = datetime.now()

alerts = []

WARNING, ALARM, QUIET = 1, 2, 3

print('Processing csv...')

for row in csv.DictReader(lines):
    city = row['data']
    if city not in [ALL_CITIES, CITY]:
        # doing this early is a good optimization
        continue
    category = int(row['category'])
    categry_desc = row['category_desc']
    # alertDate has a resolution of 1min, but time has a resolution of 1sec
    alert_date = row['date'] + 'T' + row['time']
    date = datetime.strptime(alert_date, DATE_FMT)
    if start_date <= date <= end_date:
        if MISSILES:
            if (category, categry_desc) in MISSILE_WARNING:
                alerts.append((date, WARNING))
            elif (category, categry_desc) in MISSILE_ALARM:
                alerts.append((date, ALARM))
            elif (category, categry_desc) in MISSILE_MESSAGE:
                alerts.append((date, QUIET))
        if AIRCRAFT_INTRUSION:
            if (category, categry_desc) in AIRCRAFT_INTRUSION_ALARM:
                alerts.append((date, ALARM))
            elif (category, categry_desc) in AIRCRAFT_INTRUSION_MESSAGE:
                alerts.append((date, QUIET))

print(f'Done processing csv! There are {len(alerts)} alerts.')

# it's important to sanitize the data
alerts.sort()

# we assume it was quiet in the beginning
alerts.insert(0, (start_date, QUIET))

events = []

targets = { WARNING: (ALARM, QUIET), ALARM: (QUIET,), QUIET: (WARNING, ALARM) }
i = 0
while i < len(alerts):
    timestamp, event = alerts[i]
    for j in range(i + 1, len(alerts)):
        if alerts[j][1] in targets[event]:
            next_timestamp = alerts[j][0]
            i = j
            break
    else:
        next_timestamp = end_date
        i = len(alerts)
    if next_timestamp > timestamp:
        events.append((timestamp, next_timestamp, event))

timeline = {}

current_day = start_date.date()
while current_day <= end_date.date():
    day_events = { QUIET: [], WARNING: [], ALARM: [] }
    timeline[current_day] = day_events
    current_day += timedelta(days=1)

for event_start, event_end, event in events:
    current_start = event_start
    while current_start < event_end:
        current_day = current_start.date()
        next_day = current_day + timedelta(days=1)
        next_start = datetime.combine(next_day, time.min)
        current_end = min(event_end, next_start)
        timeline[current_day][event].append((current_start, current_end))
        current_start = next_start

row_width = 12.0
row_height = 0.25
ylabel_xoffset = -1.0
ylabel_fontsize = 10.0
xmajor_labelsize = 10.0
xminor_labelsize = 10.0
xmajor_length = 3.5
xminor_length = 2.0

n_days = len(timeline)
_, axes = plt.subplots(figsize=(row_width, n_days * row_height))

colors = {
    QUIET: 'Green',
    WARNING: 'Yellow',
    ALARM: 'Red',
}

for i, (day, events) in enumerate(sorted(timeline.items())):
    y = (n_days - i - 1) * row_height
    for event, color in colors.items():
        bars = []
        for start, end in events[event]:
            h1 = start.hour + start.minute / 60. + start.second / 3600.
            if end.time() == time.min and end.date() > start.date():
                h2 = 24.
            else:
                h2 = end.hour + end.minute / 60. + end.second / 3600.
            bars.append((h1, h2 - h1))
        if bars:
            axes.broken_barh(bars, (y, row_height), facecolors=color)
    axes.text(ylabel_xoffset, y + row_height / 2, day.strftime('%d.%m'), verticalalignment='center', horizontalalignment='right', fontsize=ylabel_fontsize)

axes.set_xlim(0, 24.)
axes.set_xticks(range(24))
axes.set_xticklabels([f'{h:02d}:00' for h in range(24)])
axes.set_xticks([h + 0.5 for h in range(24) for h in range(24)], minor=True)
axes.tick_params(axis='x', which='major', labelsize=xmajor_labelsize, length=xmajor_length)
axes.tick_params(axis='x', which='minor', labelsize=xminor_labelsize, length=xminor_length)

axes.set_ylim(0, n_days * row_height)
axes.set_yticks([i * row_height for i in range(n_days + 1)])
axes.set_yticklabels([])
axes.tick_params(axis='y', length=0)

axes.grid(which='major', axis='x', color='black', linestyle=':', alpha=0.5)
axes.grid(which='major', axis='y', color='black', linestyle=':', alpha=0.5)

plt.xticks(rotation=60, horizontalalignment='center')

OUTPUT = 'chart.svg'

plt.savefig(OUTPUT, format='svg', bbox_inches='tight')
