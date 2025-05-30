import enum
from datetime import datetime
from sqlalchemy import Column, Integer, String, Enum, ForeignKey, Time, Date
from sqlalchemy.orm import relationship


from utils.database_utils import Base


# TODO: generalisation is future scope?
class CalendarEventType(enum.Enum):
    interview = "interview"


class CalendarEvent(Base):
    __tablename__ = "calendar_event"

    id = Column(Integer, primary_key=True, index=True)

    interview_schedule_id = Column(
        Integer,
        ForeignKey("interview_schedule.id"),
        nullable=True,
    )
    interview_schedule = relationship(
        "InterviewSchedule",
        backref="calendar_event",
    )

    panel_id = Column(
        Integer,
        ForeignKey("interview_panel.id"),
        nullable=False,
    )
    panel = relationship(
        "InterviewPanel",
        backref="calendar_event",
    )

    interview_slot_id = Column(
        Integer,
        ForeignKey("interview_slot.id"),
        nullable=False,
    )
    interview_slot = relationship(
        "InterviewSlot",
        backref="calendar_event",
    )

    # TODO: check with CC data/dummy data
    # if null, visible to all users
    # else, it's the applicant user
    # always visible to club members
    visible_to_user = Column(
        String,
        ForeignKey("users.uid"),
        nullable=True,
    )
    # user = relationship(
    #     "User",
    #     backref="calendar_event",
    # )

    # TODO: check with CC data/dummy data
    club_id = Column(
        String,
        ForeignKey("clubs.cid"),
        nullable=True,
    )
    # club = relationship(
    #     "Club",
    #     backref="calendar_event",
    # )

    type = Column(
        Enum(CalendarEventType),
        nullable=False,
    )
    title = Column(String, nullable=False)
    # description = Column(String, nullable=True)
    start_time = Column(Time, nullable=False)
    end_time = Column(Time, nullable=False)
    date = Column(Date, nullable=False)
    # location = Column(String, nullable=True)

    @property
    def start(self):
        return datetime.combine(self.date, self.start_time).isoformat()

    @property
    def end(self):
        if self.end_time:
            return datetime.combine(self.date, self.end_time).isoformat()
        return None

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "start": self.start,
            "end": self.end,
            "color": "#00FF00",  # green
        }
