#!/usr/bin/env python
import mysql.connector as mariadb

class DB:

	def __init__(self, db, user, password):
		self.db = db
		self.user = user
		self.password = password
		self.connected = False
		self.connect()

	def connect(self):
		if self.connected == False:
			self.connection = mariadb.connect(user=self.user, password=self.password, database=self.db)
			self.cursor = self.connection.cursor()
			self.connected = True

	def close(self):
		if self.connected == True:
			self.connection.commit()
			self.connection.close()
			self.connected = False

	def execute(self, sql, args = None):
		self.connect()
		if args == None:
			self.cursor.execute(sql)
		elif type(args) is list:
			self.cursor.executemany(sql, args)
		else:
			self.cursor.execute(sql, args)

		if sql.upper().startswith('SELECT'):
			self.data = self.cursor.fetchall()
			if self.data == None:
				self.data = []
		elif sql.upper().startswith('INSERT'):
			self.data = self.cursor.lastrowid
		elif sql.upper().startswith('DELETE'):
			self.data = True
		elif sql.upper().startswith('UPDATE'):
			self.data = True
		self.close()
		return self.data

	def one(self):
		return self.data[0] if type(self.data) is list and len(self.data) > 0 else None

	def all(self):
		return self.data if type(self.data) is list else []

	def id(self):
		return self.data if type(self.data) is int else None