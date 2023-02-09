from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.util.dt as dt_util

from dateutil import parser
from datetime import datetime, timedelta
import pytz


from homeassistant.const import ATTR_ATTRIBUTION
from .const import (
    ATTRIBUTION,
    DATE_FORMAT,
    DOMAIN,
    TIME_FORMAT,
    UPDATE_INTERVAL,
    UUID,
)

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)


async def async_setup_platform(
    hass: HomeAssistant,
    config: ConfigType,
    async_add_entities: AddEntitiesCallback,
    discovery_info: DiscoveryInfoType | None = None,
) -> None:
    async_add_entities([TimeDateSensor(hass)])


class TimeDateSensor(SensorEntity):
    def __init__(self, hass) -> None:
        """Initialize the sensor."""
        self.hass = hass
        self.unsub = None

        self.update_internal_state()

    def getDay_TTS(self, day=0):
        ordinalNumbers = {
            1: "første",
            2: "anden",
            3: "tredje",
            4: "fjerde",
            5: "femte",
            6: "sjette",
            7: "syvende",
            8: "ottende",
            9: "niende",
            10: "tiende",
            11: "ellevte",
            12: "tolvte",
            13: "trettende",
            14: "fjortende",
            15: "femtende",
            16: "sekstende",
            17: "syttende",
            18: "attende",
            19: "nittende",
            "a1": "en",
            "a2": "to",
            "a3": "tre",
            "a4": "fire",
            "a5": "fem",
            "a6": "seks",
            "a7": "syv",
            "a8": "otte",
            "a9": "ni",
            "2x": "tyvende",
            "3x": "tredivte",
            "and": "og",
        }

        day = self.dateObj.day if day == 0 else day
        if day < 20:
            return ordinalNumbers[day]
        else:
            day = str(day)
            day_TTS = ""
            if int(day[-1]) > 0:
                day_TTS += (
                    ordinalNumbers["a" + day[-1]] + " " + ordinalNumbers["and"] + " "
                )
            day_TTS += ordinalNumbers[day[0] + "x"]
            return day_TTS

    def getTime(self, format=TIME_FORMAT):
        return self.dateObj.strftime(format)

    def getTime_TTS(self, time=None):
        timeNames = {
            0: "natten",
            6: "morgenen",
            9: "formiddagen",
            12: "middagen",
            14: "eftermiddagen",
            18: "aftenen",
        }

        time = self.dateObj if time is None else parser.parse(time)

        H24 = time.hour
        H12 = H24 - 12 if H24 > 12 else H24
        M = time.minute

        timeName = ""
        for hour, name in timeNames.items():
            if H24 >= hour:
                timeName = name
            else:
                break

        if M == 0:
            return f"{ H12 } om { timeName }"
        elif M == 15:
            return f"kvart over { H12 } om { timeName }"
        elif M == 30:
            return f"halv { 1 if H12 == 12 else H12 + 1 } om { timeName }"
        elif M == 45:
            return f"kvart i { 1 if H12 == 12 else H12 + 1 } om { timeName }"
        elif M <= 35:
            return f'{ M } minut{ "ter" if M > 1 else "" } over { H12 } om { timeName }'
        elif M >= 35:
            return f'{ 60 - M } minut{ "ter" if 60 - M > 1 else "" } i { 1 if H12 == 12 else H12 + 1 } om { timeName }'
        else:
            return f"Error in the TTS machine, time given is: H24 ({ H24 }), H12 ({ H12 }) and M ({ M })"

    def getAdventsDates(self):
        adventDates = []
        XmasDateObj = datetime.strptime(
            str(self.year) + "-12-24 00:00:00", "%Y-%m-%d %H:%M:%S"
        )
        XmasDelta = 22 + XmasDateObj.weekday()

        for x in range(0, 22, 7):
            adventDates.append(
                (XmasDateObj - timedelta(days=XmasDelta - x)).strftime(DATE_FORMAT)
            )
        return adventDates

    @property
    def name(self) -> str:
        """Return the name of the sensor."""
        return "Time, date and more in Danish"

    @property
    def unique_id(self):
        return DOMAIN + "_" + UUID

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return f"{ self.weekdayName} den { self.dateObj.day }. { self.monthName.lower() } { self.year }"

    @property
    def state(self):
        """Return the state of the sensor."""
        return f"{ self.weekdayName} den { self.dateObj.day }. { self.monthName.lower() } { self.year }"

    @property
    def extra_state_attributes(self):
        # Prepare a dictionary with attributes
        attr = {}

        attr[ATTR_ATTRIBUTION] = ATTRIBUTION

        attr["ts"] = self.dateObj.timestamp()
        attr["day"] = self.dateObj.day
        attr["day_tts"] = self.getDay_TTS()

        attr["month_names"] = self.monthNames
        attr["month"] = self.dateObj.month
        attr["month_name"] = self.monthName

        attr["year"] = self.year

        attr["weeknumber"] = self.dateObj.isocalendar()[1]
        attr["even_week"] = int(self.dateObj.isocalendar()[1]) % 2 == 0
        attr["weekday"] = int(self.dateObj.weekday()) + 1
        attr["weekdays_names_short"] = self.weekdaysShort
        attr["weekday_name_short"] = self.weekdaysShort[self.dateObj.weekday()]
        attr["weekday_name"] = self.weekdayName

        attr["time"] = self.getTime()
        attr["time_tts"] = self.getTime_TTS()

        attr["advents_dates"] = self.getAdventsDates()

        attr["sun_next_rising"] = (
            parser.parse(self.hass.states.get("sun.sun").attributes["next_rising"])
            .astimezone(pytz.timezone("Europe/Copenhagen"))
            .strftime(TIME_FORMAT)
        )
        attr["sun_next_rising_tts"] = self.getTime_TTS(attr["sun_next_rising"])
        attr["sun_next_setting"] = (
            parser.parse(self.hass.states.get("sun.sun").attributes["next_setting"])
            .astimezone(pytz.timezone("Europe/Copenhagen"))
            .strftime(TIME_FORMAT)
        )
        attr["sun_next_setting_tts"] = self.getTime_TTS(attr["sun_next_setting"])

        return attr

    async def async_added_to_hass(self) -> None:
        """Set up first update."""
        self.unsub = async_track_point_in_utc_time(
            self.hass, self.point_in_time_listener, self.get_next_interval()
        )

    async def async_will_remove_from_hass(self) -> None:
        """Cancel next update."""
        if self.unsub:
            self.unsub()
            self.unsub = None

    def get_next_interval(self):
        """Compute next time an update should occur."""
        now = dt_util.utcnow()

        timestamp = dt_util.as_timestamp(now)
        interval = UPDATE_INTERVAL

        delta = interval - (timestamp % interval)
        next_interval = now + timedelta(seconds=delta)

        return next_interval

    def update_internal_state(self):

        self.dateObj = datetime.now().astimezone(pytz.timezone("Europe/Copenhagen"))

        self.monthNames = [
            "Januar",
            "Februar",
            "Marts",
            "April",
            "Maj",
            "Juni",
            "Juli",
            "August",
            "September",
            "Oktober",
            "November",
            "December",
        ]
        self.monthName = self.monthNames[self.dateObj.month - 1]

        self.year = self.dateObj.year

        self.weekdaysShort = ["Man", "Tirs", "Ons", "Tors", "Fre", "Lør", "Søn"]
        self.weekdayName = self.weekdaysShort[self.dateObj.weekday()] + "dag"

    @callback
    def point_in_time_listener(self, time_date):
        """Get the latest data and update state."""
        self.update_internal_state()
        self.async_write_ha_state()
        self.unsub = async_track_point_in_utc_time(
            self.hass, self.point_in_time_listener, self.get_next_interval()
        )
