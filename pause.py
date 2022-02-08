import math
import time
from datetime import datetime, timedelta

def nextMinute(offset=0):
    when = datetime.now()+timedelta(minutes=1)
    when = datetime(when.year, when.month, when.day, when.hour,when.minute)
    return (when-datetime.now()).total_seconds()+offset

def nextQuarterHour(offset=0):
    when = datetime.now()+timedelta(hours=0.25)
    minute = int(math.floor(when.minute/15)*15)
    when = datetime(when.year, when.month, when.day, when.hour,minute)
    return (when-datetime.now()).total_seconds()+offset

def nextHalfHour(offset=0):
    when = datetime.now()+timedelta(hours=0.5)
    minute = int(math.floor(when.minute/30)*30)
    when = datetime(when.year, when.month, when.day, when.hour,minute)
    return (when-datetime.now()).total_seconds()+offset

def nextHour(offset=0):
    when = datetime.now()+timedelta(hours=1)
    when = datetime(when.year, when.month, when.day, when.hour)
    return (when-datetime.now()).total_seconds()+offset

def nextHalfday(offset=0):
    when = datetime.now()+timedelta(days=0.5)
    hour = int(math.floor(when.hour/12)*12)
    when = datetime(when.year, when.month, when.day, hour)
    return (when-datetime.now()).total_seconds()+offset

def nextDay(offset=0):
    when = datetime.now()+timedelta(days=1)
    when = datetime(when.year, when.month, when.day)
    return (when-datetime.now()).total_seconds()+offset

def sleepUntil(sec, exitArray=[ False ]):
    now = 0
    while sec - now > 0:
        if exitArray[0]:
            return
        now = time.time()
        if sec-now > 5:
            time.sleep(5)
        elif sec-now > 1:
            time.sleep(1)
        elif sec-now > 0.1:
            time.sleep(0.1)
        else:
            time.sleep(0.01)
