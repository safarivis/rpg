from dataclasses import dataclass, field
from typing import Dict, List
import random
from datetime import datetime, timedelta

@dataclass
class TimeManager:
    """Manages game time and scheduled events."""
    current_date: int = 0
    crew_birthdays: Dict[str, int] = field(default_factory=dict)
    events_calendar: Dict[str, List[str]] = field(default_factory=dict)

    def initialize_crew_birthdays(self, crew):
        """Assign random but fixed birthday dates to crew members."""
        for member in crew:
            if member not in self.crew_birthdays:
                self.crew_birthdays[member] = random.randint(1, 365)

    def check_birthdays(self, current_date):
        """Return list of crew members whose birthdays are today."""
        birthday_celebrants = []
        for member, birthday in self.crew_birthdays.items():
            if birthday == (current_date % 365):
                birthday_celebrants.append(member)
        return birthday_celebrants

    def advance_time(self, days=1):
        """Advance time by specified number of days."""
        self.current_date += days
        return self.check_events()

    def check_events(self):
        """Check for any scheduled events on the current date."""
        date_key = str(self.current_date)
        if date_key in self.events_calendar:
            return self.events_calendar[date_key]
        return []

    def schedule_event(self, event_id, days_from_now):
        """Schedule an event to occur in the future."""
        target_date = str(self.current_date + days_from_now)
        if target_date not in self.events_calendar:
            self.events_calendar[target_date] = []
        self.events_calendar[target_date].append(event_id)

    def get_current_date_string(self):
        """Get a formatted string of the current date."""
        start_date = datetime(2500, 1, 1)  # Game starts in year 2500
        current_date = start_date + timedelta(days=self.current_date)
        return current_date.strftime("%B %d, %Y")
