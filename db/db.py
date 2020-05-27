#!/usr/bin/env python

import os, sys
import csv
import datetime as dt
from dateutil import parser
import sqlalchemy as sa
from sqlalchemy import and_, func, exc, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.sql import select
from sqlalchemy.pool import Pool
import pandas as pd
import numpy as np
from functools import reduce
from math import ceil, floor
import datetime
import numpy as np

def create_engine():
   url = 'sqlite:///../db.sqlite3'

   # Engineおよびconnectionの取得
   engine = sa.create_engine(url, echo=False)
   return engine

def create_session():
   engine = create_engine()
   conn = engine.connect()

   session = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))
   metadata = sa.MetaData(engine)

   return session, conn

# dat_forex追加
def addForex(sess, no, dtime, open, high, low, close, volume):
   try:
      query = sess.query(DatForex).filter(and_(DatForex.no == no, DatForex.dtime == dtime))
      result = query.all()

      if len(result) == 0:
         sess.add(DatForex(no=no, dtime=dtime, open=open, high=high, low=low, close=close, volume=volume, created_at=dt.datetime.now(), updated_at=dt.datetime.now()))
         sess.commit()
      else:
         stock = result[0]
         stock.open  = open
         stock.high  = high
         stock.low   = low
         stock.close  = close
         stock.volume = volume
         stock.update_at = dt.datetime.now()
         sess.commit()
   except Exception as e:
      print(e)

Base = declarative_base()

class DatForex(Base):
   __tablename__ = 'dat_forex'

   id     = sa.Column(sa.Integer, primary_key=True, autoincrement=True)
   no     = sa.Column(sa.String(10), index=True)
   dtime  = sa.Column(sa.DateTime, index=True)
   open   = sa.Column(sa.Float)
   high   = sa.Column(sa.Float)
   low    = sa.Column(sa.Float)
   close  = sa.Column(sa.Float)
   volume = sa.Column('volume', sa.Integer, nullable=True)
   created_at = sa.Column(sa.DateTime, nullable=False)
   updated_at = sa.Column(sa.DateTime, nullable=False)

def string_to_date(string):
    return datetime.datetime.strptime(string, "%Y-%m-%d").date()

def max_win_agg(s):
    _ans = s.max()
    return _ans

def week_of_month(dt):
    """ Returns the week of the month for the specified date.
    """
    week_of_month = ceil(dt.day / 7)
    return week_of_month

# csvファイルをdbにロード
def load_forex(session, no, filename):
   with open(filename, 'r') as fp:
      reader = csv.reader(fp)
      header = next(reader)

      for row in reader:
         print(row)

         _datetime = row[0]
         #_dtime = dt.datetime.strptime(_datetime, '%Y-%m-%d %H:%M:%S %z')
         _dtime = parser.parse(_datetime)
         _open = row[1]
         _high = row[2]
         _low = row[3]
         _close = row[4]

         addForex(session, no, _dtime, _open, _high, _low, _close, 0)


if __name__ == "__main__":
   argvs = sys.argv  # コマンドライン引数を格納したリストの取得
   argc = len(argvs)  # 引数の個数

   (session, conn) = create_session()
   if len(argvs) > 2:
      # csvファイルロード
      no = argvs[1]
      for argv in argvs[2:]:
         print(argv)
         load_forex(session, no, argv)

   else:
      # table作成
      engine = create_engine()
      Base.metadata.create_all(bind=engine)
      print("CREATE TABLE DONE")




