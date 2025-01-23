from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()

class Answers(Base):
    __tablename__ = "Ответы"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)


class Metrics(Base):
    __tablename__ = "Метрики"

    id = Column(Integer, primary_key=True, unique=True, nullable=False)
    name = Column(String, nullable=False)
    description = Column(String, nullable=False)
