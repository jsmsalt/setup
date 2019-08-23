#!/usr/bin/env python
from exchange import Binance
import sys, time, datetime

args_len = len(sys.argv)
args = list(sys.argv)

key = 'xxxxxxxx'
secret = 'xxxxxxxxxx'

if args_len > 1 and args[1] == '--pump':
	binance = Binance(key, secret)
	binance.pump()
elif args_len > 1 and args[1] == '--trade':
	binance = Binance(key, secret)
	binance.trade()
else:
	minutes = 4
	delta = int(time.mktime((datetime.datetime.now() + datetime.timedelta(minutes = minutes)).timetuple()))
	now = int(time.mktime((datetime.datetime.now()).timetuple()))
	print delta - now
	pass
