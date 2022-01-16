

# Time-Date-DK

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg?style=for-the-badge)](https://github.com/hacs/integration)

Time-Date sensor with many attributes for a more accurate use of name of times and dates in Danish.

For installation instructions [see this guide](https://hacs.xyz/docs/faq/custom_repositories).
## Quick start
Add the following to your configuration.yaml
```yaml
time_date_dk:
```
## State and attributes
![Screenshot](https://github.com/J-Lindvig/Time-Date-DK/blob/main/images/screenshot.png)
### Documentation
| Attribute name             | Example value                             | Description                        |
|----------------------------|-------------------------------------------|------------------------------------|
| attribution                | Created by J-Lindvig                      | Name of the creator                |
| ts                         | 1642334220.007388                         | Current timestamp                  |
| day                        | 16                                        | Number of day in the month         |
| day_tts                    | sekstende                                 | Spoken name of the day             |
| month_names                | Januar, Februar, Marts, April, ...        | List of the months in danish       |
| month_name                 | Januar                                    | Name of the current month          |
| year                       | 2022                                      | Current year in 4 digits           |
| weeknumber                 | 2                                         | Current weeknumber                 |
| weekday                    | 7                                         | Current number of weekday          |
| weekdays_names_short       | Man, Tirs, Ons, Tors, Fre, ...            | List of the weekdays in short form |
| weekday_name_short         | Søn                                       | Name of the weekday in short form  |
| weekday_name               | Søndag                                    | Name of the weekday in long form   |
| time                       | 12:57                                     | Time in HH:MM format               |
| time_tts                   | 3 minutter i 1 om middagen                | Time as snaturally spoken          |
| advents_dates              | 27-11-2022, 04-12-2022, ...               | List of the adventsdates           |
| sun_next_rising            | 08:32                                     | Time of the next sunrise in HH:MM  |
| sun_next_rising_tts        | 32 minutter over 8 om morgenen            | Time if the next sunrise as TTS    |
| sun_next_setting           | 16:24                                     | Time of the next sunset in HH:MM   |
| sun_next_setting_tts       | 24 minutter over 4 om eftermiddagen       | Time of the next sunset in TTS     |
| friendly_name              | Time, Date and other attributes in Danish | Friendly name of the sensor        |
