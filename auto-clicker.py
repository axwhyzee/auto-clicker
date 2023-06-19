import argparse
import datetime
import logging
import time

import pyautogui
import tqdm

logger = logging.getLogger()
logging.basicConfig(level = logging.INFO)

def epochnow():
    return datetime.datetime.utcnow().timestamp()

class DatetimeTarget():
    def __init__(
        self, 
        day: int,
        month: int,
        year: int,
        hour: int, 
        minute: int, 
        second: int=0, 
        utcoffset: int=8
    ):
        self.__datetime = datetime.datetime(
            year,
            month,
            day,
            hour,
            minute,
            second,
        ) - datetime.timedelta(hours=utcoffset)
        self.__utcoffset = utcoffset

    def time_diff(
        self
    ) -> float:
        target = self.__datetime.timestamp()
        return target - epochnow()
    
    def tz_adjusted_dt(
        self
    ) -> datetime.datetime:
        return self.__datetime + datetime.timedelta(hours=self.__utcoffset)
    
    def __repr__(
        self
    ):
        timenow = epochnow()
        _repr_str = '[Timenow]\n'
        _repr_str += f'├─[UTC +0] {datetime.datetime.utcfromtimestamp(timenow)} / {timenow}\n'
        timenow += self.__utcoffset * 60 * 60
        _repr_str += f'└─[GMT +{self.__utcoffset}] {datetime.datetime.utcfromtimestamp(timenow)} / {timenow}\n'

        _repr_str += '[Target]\n'    
        _repr_str += f'├─[UTC +0] {self.__datetime} / {self.__datetime.timestamp()}\n'
        _repr_str += f'└─[GMT +{self.__utcoffset}] {self.tz_adjusted_dt()} / {self.tz_adjusted_dt().timestamp()}'

        return _repr_str


def main():
    TQDM_INTERVAL = 50

    # defaults
    dtnow = datetime.datetime.now()
    _year = dtnow.year
    _month = dtnow.month
    _day = dtnow.day
    _hour = dtnow.hour
    _minute = dtnow.minute
    _second = 0
    _utcoffset = 8
    _wait = 3

    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-y',
        '--year',
        type=int,
        nargs='?',
        default=_year,
        help='Year'
    )
    parser.add_argument(
        '-m',
        '--month',
        type=int,
        nargs='?',
        default=_month,
        help='Month'
    )
    parser.add_argument(
        '-d',
        '--day',
        type=int,
        nargs='?',
        default=_day,
        help='Day of the month. E.g., 8, 14'
    )
    parser.add_argument(
        '-H',
        '--hour',
        type=int,
        nargs='?',
        default=_hour,
        help='Hour (24-hour format). E.g., 8, 14'
    )
    parser.add_argument(
        '-M',
        '--minute',
        type=int,
        nargs='?',
        default=_minute,
        help='Minutes. E.g., 0, 47'
    )
    parser.add_argument(
        '-S',
        '--second',
        type=int,
        nargs='?',
        default=_second,
        help='Seconds. E.g., 0, 47'
    )
    parser.add_argument(
        '-u',
        '--utcoffset',
        type=int,
        nargs='?',
        default=_utcoffset,
        help='Timezone offset from UTC. Defaults to 8 (GMT+8). E.g., 1, 8'
    )
    parser.add_argument(
        '-w',
        '--wait',
        type=float,
        nargs='?',
        default=_wait,
        help='Lock in mouse cursor coordinates after <n> seconds'
    )
    args = parser.parse_args()
    config = vars(args)

    _wait = config.pop('wait')
    T = DatetimeTarget(**config)
    if T.time_diff() <= _wait:
        logger.error('Enter a later timing')
        exit()

    logger.info(f'Hover your cursor where you want to click. Mouse coordinates will lock in after {_wait} secs')
    
    _step = _wait/TQDM_INTERVAL
    for _ in tqdm.tqdm(range(TQDM_INTERVAL)):
        time.sleep(_step)
    _x, _y = pyautogui.position()

    logger.info('You may move your cursor away now')
    logger.info('<CTRL+C> to kill program')
    logger.info(f'[SCHEDULED] Click @ (X: {_x}, Y: {_y}) in ({T.time_diff():.6f}) secs')

    try:
        time.sleep(T.time_diff())
    except:
        logger.error('Target timing has elapsed. Enter a later timing')
        exit()

    pyautogui.click(x=_x, y=_y)
    logger.info(f'[TRIGGERED] {datetime.datetime.now()}')

if __name__ == '__main__':
    main()