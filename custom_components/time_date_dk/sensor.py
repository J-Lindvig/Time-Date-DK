from __future__ import annotations

import logging

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.event import async_track_point_in_utc_time
from homeassistant.helpers.typing import ConfigType, DiscoveryInfoType
import homeassistant.util.dt as dt_util

import datetime as DT
from datetime import timedelta

_LOGGER: logging.Logger = logging.getLogger(__package__)
_LOGGER = logging.getLogger(__name__)

async def async_setup_platform(
	hass: HomeAssistant,
	config: ConfigType,
	async_add_entities: AddEntitiesCallback,
	discovery_info: DiscoveryInfoType | None = None,
) -> None:
	async_add_entities([ExampleSensor(hass)])

class ExampleSensor(SensorEntity):
	"""Representation of a sensor."""

	def __init__(self, hass) -> None:
		"""Initialize the sensor."""
		self.hass = hass
		self.unsub = None

		self._update_internal_state()

	def _getDay_TTS(self, day = 0):
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
			"and": "og"
		}

		day = self._day if day == 0 else day
		if day < 20:
			return ordinalNumbers[day]
		else:
			day = str(day)
			day_TTS = ''
			if int(day[-1]) > 0:
				day_TTS += ordinalNumbers["a" + day[-1]] + " " + ordinalNumbers["and"] + " "
			day_TTS += ordinalNumbers[day[0] + "x"]
			return day_TTS

	def _getTime(self, format = '%H:%M:%S'):
		return self._dateObj.strftime(format)

	def _getTime_TTS(self):
		timeNames = {0: "natten", 6: "morgenen", 9: "formiddagen", 12: "middagen", 14: "eftermiddagen", 18: "aftenen" }
		H24 = self._getTime('%-H')
		H12 = int(self._getTime('%-I'))
		M = int(self._getTime('%-M'))

		timeName = timeNames[min(timeNames, key=lambda x:abs(x-int(H24)))]
		if M == 0:
			return f'{ H12 } om { timeName }'
		elif M == 15:
			return f'kvart over { H12 } om { timeName }'
		elif M == 30:
			return f'halv { 1 if H12 == 12 else H12 + 1 } om { timeName }'
		elif M == 45:
			return f'kvart i { 1 if H12 == 12 else H12 + 1 } om { timeName }'
		elif M <= 35:
			return f'{ M } minut{ "ter" if M > 1 else "" } over { H12 } om { timeName }'
		elif M >= 35:
			return f'{ 60 - M } minut{ "ter" if 60 - M > 1 else "" } i { 1 if H12 == 12 else H12 + 1 } om { timeName }'
		else:
			return f'Error in the TTS machine, time given is: H24 ({ H24 }), H12 ({ H12 }) and M ({ M })'

	def _getAdventsDates(self):
		adventDates = []
		format = '%d-%m-%Y'
		XmasDateObj = DT.datetime.strptime(str(self._year) + '-12-24 00:00:00', '%Y-%m-%d %H:%M:%S')
		XmasDelta = 22 + XmasDateObj.weekday()

		adventDates.append((XmasDateObj - timedelta(days = XmasDelta      )).strftime(format))
		adventDates.append((XmasDateObj - timedelta(days = XmasDelta - 7  )).strftime(format))
		adventDates.append((XmasDateObj - timedelta(days = XmasDelta - 14 )).strftime(format))
		adventDates.append((XmasDateObj - timedelta(days = XmasDelta - 21 )).strftime(format))

		return adventDates

	@property
	def name(self) -> str:
		"""Return the name of the sensor."""
		return 'time_date_dk'

	@property
	def native_value(self):
		"""Return the state of the sensor."""
		return self._state

	@property
	def state(self):
		"""Return the state of the sensor."""
		return self._state

	@property
	def extra_state_attributes(self):
		# Prepare a dictionary with attributes
		attr = {}

		attr['ts'] = self._ts
		attr['day'] = self._day
		attr['day_tts'] = self._day_TTS

		attr['month_names'] = self._monthNames
		attr['month'] = self._month
		attr['month_name'] = self._monthName

		attr['year'] = self._year

		attr['weeknumber'] = self._weekNumber
		attr['weekday'] = int(self._weekday) + 1
		attr['weekdays_names_short'] = self._weekdaysShort
		attr['weekday_name_short'] = self._weekdayNameShort
		attr['weekday_name'] = self._weekdayName

		attr['time'] = self._time
		attr['time_hhmm'] = self._time_HHMM
		attr['time_tts'] = self._time_TTS

		attr['advents_dates'] = self._adventsDates

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
		interval = 60

		delta = interval - (timestamp % interval)
		next_interval = now + timedelta(seconds=delta)

		return next_interval

	def _update_internal_state(self):
		self._dateObj = DT.datetime.now()
		self._ts = self._dateObj.timestamp()

		self._day = self._dateObj.day

		self._day_TTS = self._getDay_TTS()

		self._monthNames =  ['Januar', 'Februar', 'Marts', 'April', 'Maj', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'December']
		self._month = self._dateObj.month
		self._monthName = self._monthNames[self._month - 1]

		self._year = self._dateObj.year

		self._weekNumber = self._dateObj.isocalendar()[1]
		self._weekdaysShort = ['Man', 'Tirs', 'Ons', 'Tors', 'Fre', 'Lør']
		self._weekday = self._dateObj.weekday()
		self._weekdayNameShort = self._weekdaysShort[self._weekday]
		self._weekdayName = self._weekdayNameShort + 'dag'

		self._time = self._getTime()
		self._time_HHMM = self._getTime('%H:%M')
		self._time_TTS = self._getTime_TTS()

		self._adventsDates = self._getAdventsDates()

		self._state = f'{ self._weekdayName} den { self._day }. { self._monthName } { self._year }'

	@callback
	def point_in_time_listener(self, time_date):
		"""Get the latest data and update state."""
		self._update_internal_state()
		self.async_write_ha_state()
		self.unsub = async_track_point_in_utc_time(
			self.hass, self.point_in_time_listener, self.get_next_interval()
		)
