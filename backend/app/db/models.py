from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Driver(Base):
    __tablename__ = "drivers"
    id = Column(Integer, primary_key=True, index=True)
    driver_id = Column(String, unique=True, index=True) # e.g., 'max_verstappen'
    code = Column(String) # e.g., 'VER'
    number = Column(Integer)
    first_name = Column(String)
    last_name = Column(String)
    nationality = Column(String)

class Team(Base):
    __tablename__ = "teams"
    id = Column(Integer, primary_key=True, index=True)
    constructor_id = Column(String, unique=True, index=True)
    name = Column(String)
    nationality = Column(String)

class Race(Base):
    __tablename__ = "races"
    id = Column(Integer, primary_key=True, index=True)
    season = Column(Integer, index=True)
    round = Column(Integer)
    name = Column(String) # e.g., 'Monaco Grand Prix'
    date = Column(DateTime)
    circuit_id = Column(String)

class Telemetry(Base):
    __tablename__ = "telemetry"
    id = Column(Integer, primary_key=True, index=True)
    race_id = Column(Integer, ForeignKey("races.id"), index=True)
    driver_id = Column(Integer, ForeignKey("drivers.id"), index=True)
    lap_number = Column(Integer, index=True)
    time = Column(Float) # Time relative to session start
    speed = Column(Integer)
    rpm = Column(Integer)
    gear = Column(Integer)
    throttle = Column(Float)
    brake = Column(Float)
    drs = Column(Integer)
    x = Column(Float)
    y = Column(Float)
    z = Column(Float)
