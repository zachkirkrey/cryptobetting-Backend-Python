import os
from functools import wraps
from os import environ as env
from sqlalchemy import (BLOB, DECIMAL, SMALLINT, TIMESTAMP, VARCHAR, DateTime,
                        BigInteger, Boolean, Column, Float, ForeignKey, Date, Time,
                        Integer, LargeBinary, String, Text, and_,
                        create_engine, func, not_, or_, text)
from sqlalchemy.exc import OperationalError, StatementError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import event
import numpy as np
import sqlalchemy


DBDATA = os.getenv('BO_DB_URL')
DB_URL = 'mysql+pymysql://{0}:{1}@{2}:{3}/{4}'.format(DBDATA.split(',')[0], DBDATA.split(
    ',')[1], DBDATA.split(',')[2], DBDATA.split(',')[3], DBDATA.split(',')[4])


Base = declarative_base()
engine = create_engine(DB_URL, pool_recycle=3600,
                       connect_args={'connect_timeout': 60})


def add_own_encoders(conn, cursor, query, *args):
    cursor.connection.encoders[np.int64] = lambda value, encoders: int(value)


event.listen(engine, "before_cursor_execute", add_own_encoders)


session = sessionmaker(bind=engine)


class Expiries(Base):
    __tablename__ = 'expiries'
    idexpiries = Column(Integer, primary_key=True)
    expiry = Column(BigInteger)
    btc_price = Column(Float)
    rake_over = Column(Float)
    rake_under = Column(Float) 
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))

class Probabilities(Base):
    __tablename__ = 'probabilities'

    idprobabilities = Column(Integer, primary_key=True)
    idexpiries = Column(ForeignKey('expiries.idexpiries',
                                   ondelete='RESTRICT', onupdate='RESTRICT'), index=True)
    strike = Column(Float)
    over = Column(Float)
    under = Column(Float)
    created_at = Column(TIMESTAMP, server_default=text("CURRENT_TIMESTAMP"))