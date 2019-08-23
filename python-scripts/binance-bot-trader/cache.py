#!/usr/bin/env python
import time, datetime

class Cache:
	data = {}

	def getTimeNow(self):
		return int(time.mktime((datetime.datetime.now()).timetuple()))

	def set(self, key, data, expire = 2):
		self.data[key] = {
						'time': self.getTimeNow(),
						'expire': expire,
						'data': data
					}
		return data
	def get(self, key, default = None):
		if key in self.data:
			if self.getTimeNow() - self.data[key]['time'] >= self.data[key]['expire']:
				del self.data[key]
				return default
			else:
				return self.data[key]['data']
		else:
			return default