from sqlalchemy import Column, Integer, String, Boolean, DateTime, JSON, Text
from sqlalchemy.ext.declarative import declarative_base
import datetime
Base = declarative_base()

class UserCalendar(Base):
    __tablename__ = "user_calendars"
    id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String, unique=True, index=True)
    access_token = Column(String)
    refresh_token = Column(String)
    token_expiry = Column(DateTime)
    calendar_id = Column(String, default="primary")
    sync_token = Column(String, nullable=True)  # Google syncToken for incremental sync
    is_synced = Column(Boolean, default=False)
    webhook_channel_id = Column(String, nullable=True)
    webhook_resource_id = Column(String, nullable=True)
    opted_out = Column(Boolean, default=False)
    extra = Column(JSON, default={})
