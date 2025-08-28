from sqlalchemy import Column, Integer, Text, ARRAY
from sqlalchemy.orm import declarative_base
from typing import List
Base = declarative_base()

class Lieu(Base):
    __tablename__ = 'lieux'
    id = Column(Integer, primary_key=True)
    name = Column(Text, nullable=False)
    type = Column(Text)
    mer_proche = Column(ARRAY(Text))
    capitale = Column(ARRAY(Text))
    montagne = Column(ARRAY(Text))
    riviere = Column(ARRAY(Text))
    bataille = Column(ARRAY(Text))
    peuple = Column(ARRAY(Text))