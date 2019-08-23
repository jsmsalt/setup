#!/usr/bin/env python
import time, datetime, re, math
from binance.client import Client
from binance.websockets import BinanceSocketManager
from binance.exceptions import *
from binance.enums import *
from colorama import Fore, Back, Style
from requests.exceptions import Timeout as TimeoutException
from twisted.internet import reactor
import logging
from pushbullet import Pushbullet

class Binance:
	api_calls_count = 0
	api_error_code = 0
	api_error_msj = None
	pause_time = 0
	recomended_coins = ['STRATBTC', 'HSRBTC', 'WTCBTC', 'XZCBTC', 'DASHBTC', 'BNBBTC',
						'GXSBTC', 'NAVBTC', 'NEBLBTC', 'LSKBTC', 'AIONBTC', 'INSBTC',
						'BTGBTC', 'MODBTC', 'NEOBTC', 'KMDBTC', 'BCDBTC', 'BCCBTC',
						'ETCBTC', 'ETHBTC', 'LUNBTC', 'DGDBTC', 'QTUMBTC', 'SALTBTC',
						'TRIGBTC', 'LTCBTC', 'XMRBTC', 'ZECBTC', 'OMGBTC', 'EDOBTC',
						'RLCBTC', 'WAVESBTC', 'GASBTC', 'PPTBTC', 'ICXBTC', 'MTLBTC',
						'GVTBTC', 'MCOBTC', 'ARKBTC', 'XRPBTC', 'FUELBTC', 'SNGLSBTC',
						'OAXBTC', 'ZRXBTC', 'SUBBTC', 'MDABTC', 'KNCBTC', 'ICNBTC',
						'IOTABTC', 'EOSBTC', 'ARNBTC', 'BQXBTC']
	coins_info = {
					'OST': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'EOS': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'LINK': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'OAX': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'STRAT': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'HSR': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'MANA': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'WTC': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'XZC': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'IOTA': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'KNC': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'BNT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'DASH': {'tick_qty': 0.001, 'min_price': 1e-06, 'min_notional': 0.001, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.001, 'max_price': 100000.0}, 
					'BNB': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'BQX': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'VIB': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'SNGLS': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'SNM': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'SNT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'GXS': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'NAV': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'XLM': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'EVX': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'FUN': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'CMT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'NEBL': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'AMB': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'LSK': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'AION': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'ENG': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'ENJ': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'TRX': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'DLT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'XRP': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'LRC': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'BTS': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'WABI': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'CND': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'INS': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'BTG': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'YOYO': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'MOD': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'NEO': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 100000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'KMD': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'SUB': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'CTR': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'BCD': {'tick_qty': 0.001, 'min_price': 1e-06, 'min_notional': 0.001, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.001, 'max_price': 100000.0}, 
					'REQ': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'BCC': {'tick_qty': 0.001, 'min_price': 1e-06, 'min_notional': 0.001, 'tick_price': 1e-06, 'max_qty': 100000.0, 'min_qty': 0.001, 'max_price': 100000.0}, 
					'ETC': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'ETH': {'tick_qty': 0.001, 'min_price': 1e-06, 'min_notional': 0.001, 'tick_price': 1e-06, 'max_qty': 100000.0, 'min_qty': 0.001, 'max_price': 100000.0}, 
					'LUN': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'DGD': {'tick_qty': 0.001, 'min_price': 1e-06, 'min_notional': 0.001, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.001, 'max_price': 100000.0}, 
					'AST': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'POWR': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'QTUM': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'MDA': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'GVT': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'SALT': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'TRIG': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'ELF': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'BCPT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'ADX': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'GTO': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'LTC': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 100000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'DNT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'ADA': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'VEN': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'RDN': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'XMR': {'tick_qty': 0.001, 'min_price': 1e-06, 'min_notional': 0.001, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.001, 'max_price': 100000.0}, 
					'ZEC': {'tick_qty': 0.001, 'min_price': 1e-06, 'min_notional': 0.001, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.001, 'max_price': 100000.0}, 
					'OMG': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'APPC': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'EDO': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'RLC': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'CDT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'WAVES': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'BRD': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'WINGS': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'BAT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'NULS': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'RCN': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'VIBE': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.001, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'GAS': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 100000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'PPT': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'POE': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'TNT': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'ICN': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'LEND': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'ZRX': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'STORJ': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'MTH': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'ICX': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'MTL': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'TNB': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'XVG': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'MCO': {'tick_qty': 0.01, 'min_price': 1e-06, 'min_notional': 0.002, 'tick_price': 1e-06, 'max_qty': 10000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'QSP': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'FUEL': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}, 
					'ARK': {'tick_qty': 0.01, 'min_price': 1e-07, 'min_notional': 0.002, 'tick_price': 1e-07, 'max_qty': 90000000.0, 'min_qty': 0.01, 'max_price': 100000.0}, 
					'ARN': {'tick_qty': 1.0, 'min_price': 1e-08, 'min_notional': 0.002, 'tick_price': 1e-08, 'max_qty': 90000000.0, 'min_qty': 1.0, 'max_price': 100000.0}
				}

	def __init__(self, key, secret):
		self.key = key
		self.secret = secret
		try:
			self.client = Client(self.key, self.secret)
		except (BinanceAPIException, Timeout, Exception) as error:
			self.handleError('__init__', 'Client', error)
			self.client = None

		self.logger = logging.getLogger('binance')
		handler = logging.FileHandler('errores.log')
		formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
		handler.setFormatter(formatter)
		self.logger.addHandler(handler) 
		self.logger.setLevel(logging.DEBUG)
		self.pushbullet = Pushbullet('o.a9rMypX87kSJaIWPhHqXeO6vnSuQd34z')

	def msgInfo(self, title, msg):
		print Back.BLUE + Fore.WHITE + ' ' + str(title) + ' ' + Back.RESET + Fore.RESET + ' ' + str(msg)

	def msgWarning(self, title, msg):
		print Back.YELLOW + Fore.BLACK + ' ' + str(title) + ' ' + Back.RESET + Fore.RESET + ' ' + str(msg)

	def msgSuccess(self, title, msg):
		print Back.GREEN + Fore.WHITE + ' ' + str(title) + ' ' + Back.RESET + Fore.RESET + ' ' + str(msg)

	def msgError(self, title, msg):
		print Back.RED + Fore.WHITE + ' ' + str(title) + ' ' + Back.RESET + Fore.RESET + ' ' + str(msg)

	def msgBlack(self, title, msg):
		print Back.BLACK + Fore.WHITE + ' ' + str(title) + ' ' + Back.RESET + Fore.RESET + ' ' + str(msg)

	def handleError(self, func, section, error):
		self.logger.error('%s/%s %s::%s' % (func, section, error.status_code, error.message))
		if int(error.status_code) == 429:
			self.pause_time = self.getTimeDelta(2)
		elif int(error.status_code) == 418:
			self.pause_time = self.getTimeDelta(60)

	def toSatoshi(self, btc, debug = False):
		return int(float("{0:.8f}".format(float(btc))) * 100000000)

	def toBtc(self, satoshi):
		return "%.8f" % (float(satoshi) / 100000000)

	def floatPrecision(self, f, n):
		n = int(math.log10(1 / float(n)))
		f = math.floor(float(f) * 10 ** n) / 10 ** n
		f = "{:0.0{}f}".format(float(f), n)
		return str(int(f)) if int(n) == 0 else f

	def getTimeNow(self):
		return int(time.mktime((datetime.datetime.now()).timetuple()))

	def getTimeDelta(self, minutes):
		return int(time.mktime((datetime.datetime.now() + datetime.timedelta(minutes = minutes)).timetuple()))

	def getCoinInfo(self, coin):
		return self.coins_info[coin]

	def getAllPrices(self):
		try:
			return self.client.get_all_tickers()
		except (BinanceAPIException, Timeout, Exception) as error:
			self.handleError('getAllPrices', 'get_all_tickers', error)
			return []

	def createOrder(self, side, coin, strategy):
		side_str = 'COMPRA' if side == 'BUY' else 'VENTA'
		order = {'error': True, 'id': 0, 'price': 0, 'amount': 0}
		keep_trying = True
		attemps = 0
		coin_info = self.getCoinInfo(coin)
		tick_price = coin_info['tick_price']
		tick_qty = coin_info['tick_qty']
		max_price = coin_info['max_price']
		max_qty = coin_info['max_qty']
		min_notional = coin_info['min_notional']
		min_price = coin_info['min_price']
		min_qty = coin_info['min_qty']
		price_precision = int(math.log10(1 / tick_price))
		failed_attemps = 0
		previous_failed_price = 0

		self.msgInfo(side_str, 'Estrategia para %s' % coin.upper())

		while keep_trying == True:
			attemps += 1

			if attemps >= strategy['max_attempts']:
				self.msgError(side_str, 'Se supero el numero de intentos')
				keep_trying = False
				break

			try:
				price = float(filter(lambda x: x['symbol'] == coin.upper()+'BTC', self.client.get_all_tickers())[0]['price'])
				price += (tick_price * strategy['tick'])
				price = self.floatPrecision(price, tick_price)
			except (BinanceAPIException, Timeout, Exception) as error:
				self.handleError('createOrder', 'get_all_tickers', error)
				keep_trying = False
				break

			try:
				if side == 'BUY':
					amount = float(self.client.get_asset_balance(asset='BTC')['free'])
					amount = (strategy['balance_percent'] * amount) / float(price)
				elif side == 'SELL':
					amount = float(self.client.get_asset_balance(asset=coin.upper())['free'])
					amount = strategy['balance_percent'] * amount
				amount = self.floatPrecision(amount, tick_qty)
			except (BinanceAPIException, Timeout, Exception) as error:
				self.handleError('createOrder', 'get_asset_balance', error)
				keep_trying = False
				break

			notional = float(price) * float(amount)
			self.msgBlack('Tipo: %s, Precio: %s, Cantidad: %s, Notional: %s, Min Notional: %s' % (side_str, price, amount, notional, min_notional), '')

			cond_notional = notional >= min_notional
			cond_price = (float(price) >= min_price) and (float(price) <= max_price)
			cond_amount = (float(amount) >= min_qty) and (float(amount) <= max_qty)

			if cond_notional and cond_price and cond_amount:
				self.msgInfo(side_str, 'Intentanto %s de %s' % (attemps, strategy['max_attempts']))

				try:				
					o = self.client.create_order(symbol=coin.upper()+'BTC',side=(SIDE_BUY if side == 'BUY' else SIDE_SELL),type=ORDER_TYPE_LIMIT,timeInForce=TIME_IN_FORCE_IOC,quantity=amount,price=price)
					if (o['status'] == 'FILLED' or o['status'] == 'PARTIALLY_FILLED'):
						self.msgSuccess(side_str, 'Orden ejecutada con exito')
						keep_trying = False
						order = {'error': False, 'id': o['orderId'], 'price': self.toSatoshi(price), 'amount': float(amount)}
						break
					else:
						self.msgError(side_str, 'No se pudo ejecutar la orden')
						failed_attemps += 1
						# previous_failed_price = self.toSatoshi(price)
						if side == 'BUY':
							if price_precision in [7, 8]:
								strategy['tick'] += strategy['tick_factor'] * failed_attemps
							else:
								strategy['tick'] += (strategy['tick'] if not strategy['tick'] == 0 else 1) * strategy['tick_factor'] * failed_attemps
						elif side == 'SELL':
							if price_precision in [7, 8]:
								strategy['tick'] -= strategy['tick_factor'] * failed_attemps
							else:
								strategy['tick'] -= (strategy['tick'] if not strategy['tick'] == 0 else 1) * strategy['tick_factor'] * failed_attemps
						keep_trying = True

				except (BinanceAPIException, Timeout, Exception) as error:
					self.handleError('createOrder', 'create_order', error)
					keep_trying = True

			else:
				self.msgError(side_str, 'No se cumplieron las condiciones para enviar la orden')
				keep_trying = False
				break

			time.sleep(.2)

		return order

	def buy(self, coin, strategy):
		return self.createOrder('BUY', coin, strategy)

	def sell(self, coin, strategy):
		return self.createOrder('SELL', coin, strategy)

	def processPumpTicker(self, ticker):

		pump_date = datetime.datetime.strptime("12 Feb 2018 16:00:00 GMT", '%d %b %Y %H:%M:%S %Z')
		pump_date = int(time.mktime((pump_date).timetuple()))
		timenow = self.getTimeNow()

		if ((pump_date - 10) - timenow) <= 0:

			prices = filter(lambda x: x['s'].upper().endswith('BTC'), ticker)
			prices = dict(map(lambda p: (re.sub(r'\BBTC$', "", p['s']), self.toSatoshi(p['c'])), prices))
			
			if self.pumping == 0:

					self.msgInfo('INFO', 'Pump iniciado...')
					self.trading_buy_strategy = {'tick': 3, 'tick_factor': 2, 'max_attempts': 15, 'balance_percent': 1}
					self.trading_sell_strategy = {'tick': 3, 'tick_factor': 2, 'max_attempts': 100, 'balance_percent': 1}
					self.first_prices = {}
					self.pumping = 1

			elif self.pumping == 1:

				if len(self.first_prices) == 0:
					self.first_prices= prices
					self.base_percent = 8 #4
					self.add_percent = 1 #1
					self.high_percent = 35
				else:			
					best_coins = dict((coin, (((price*100.00)/self.first_prices[coin])-100.00)) for (coin, price) in prices.iteritems() if coin in self.first_prices and (((price*100.00)/self.first_prices[coin])-100.00) >= self.base_percent and (((price*100.00)/self.first_prices[coin])-100.00) < self.high_percent)

					if len(best_coins) == 1:
						[(c, p)] = best_coins.items()
						self.trading_coin = c
						self.msgInfo('INFO', 'Moneda encontrada: %s' % self.trading_coin)
						self.pumping = 2
					elif len(best_coins) > 1:
						self.base_percent += self.add_percent
						self.msgWarning('INFO', 'Porcentaje aumentado: %s%%' % self.base_percent)

					if len(self.first_prices) < 100:
						temp = prices
						temp.update(self.first_prices)
						self.first_prices = temp

			elif self.pumping == 2:
				
				buy = self.buy(self.trading_coin, self.trading_buy_strategy)
				
				if buy['error'] == False:
					self.trading_high_price = 0
					self.trading_high_percent = 0.000
					self.trading_high_win = 5.000 #5
					self.trading_high_lose = 7.000 #8
					self.trading_buy_price = buy['price']
					self.trading_buy_amount = buy['amount']
					self.pumping = 3
				else:
					self.msgError('ERROR', 'No se pudo comprar, intentando nuevamente...')
					self.pumping = 1
			
			elif self.pumping == 3:

				if self.trading_coin in prices:
					current_price = prices[self.trading_coin]
					current_percent = float((current_price * 100.000) / self.trading_buy_price)

					if current_percent > 100.000 and current_price > self.trading_high_price:
						self.trading_high_price = current_price
						self.trading_high_percent = current_percent
						self.msgSuccess('%s%%' % self.floatPrecision(current_percent, .001), '**** %s BTC ****' % self.toBtc(current_price))
					else:
						if current_percent < 100.000:
							self.msgError('%s%%' % self.floatPrecision(current_percent, .001), '%s BTC' % self.toBtc(current_price))
						else:
							self.msgSuccess('%s%%' % self.floatPrecision(current_percent, .001), '%s BTC' % self.toBtc(current_price))

					cond_positive_high = current_percent > 100.000 and ((self.trading_high_percent - current_percent) >= self.trading_high_win)
					cond_negative_low = current_percent <= (100.000 - self.trading_high_lose)

					if cond_positive_high or cond_negative_low:
						sell = self.sell(self.trading_coin, self.trading_sell_strategy)
						if sell['error'] == False:
							pump_balance = int((sell['price'] * sell['amount']) - (self.trading_buy_price * self.trading_buy_amount))
							
							if pump_balance < 0:
								self.msgError('BALANCE', '%s satoshi' % pump_balance)
							else:
								self.msgSuccess('BALANCE', '%s satoshi' % pump_balance)
							self.pumping = 4
						self.msgInfo('INFO', 'Trading finalizado...')
			else:
				self.msgInfo('INFO', 'Trading finalizado...')

	def processTradeTicker(self, ticker):
		timenow = self.getTimeNow()

		if self.trading == 1 or self.trading == 3:
			prices = filter(lambda x: x['s'].upper() in self.recomended_coins, ticker)
			prices = dict(map(lambda p: (re.sub(r'\BBTC$', "", p['s']), self.toSatoshi(p['c'])), prices))

		if (self.pause_time - timenow) <= 0:
			if self.trading > 0:
				if (timenow - self.ticker_info_time) >= 600:
					self.volumes = self.client.get_ticker()
					self.volumes = filter(lambda x: x['symbol'] in self.recomended_coins, self.volumes)
					self.volumes = dict(map(lambda x: (re.sub(r'\BBTC$', "", x['symbol']), float(x['quoteVolume'])), self.volumes))
					self.ticker_info_time = timenow

				if (timenow - self.trade_time) >= self.sample_every:
					self.trade_time = timenow
					tickers = self.getAllPrices()
					tickers = filter(lambda x: x['symbol'] in self.recomended_coins, tickers)
					tickers = dict(map(lambda p: (re.sub(r'\BBTC$', "", p['symbol']), self.toSatoshi(p['price'])), tickers))
					self.prices_list.append(tickers)
					self.new_sample = True
					if len(self.prices_list) >= (self.sample_amount + 1):
						self.prices_list.pop(0)

			if self.trading == 0:

				self.msgWarning('TRADING', 'Trading iniciado...')
				self.trading_buy_strategy = {'tick': 0, 'tick_factor': 2, 'max_attempts': 3, 'balance_percent': 1}
				self.trading_sell_strategy = {'tick': 0, 'tick_factor': 2, 'max_attempts': 10, 'balance_percent': 1}
				self.prices_list = []
				self.first_prices = {}
				self.volumes = {}
				self.total_balance = 0
				self.sample_amount = 10
				self.sample_every = 30
				self.new_sample = False
				self.trade_time = timenow
				self.ticker_info_time = 0
				self.trading_success = 0
				self.trading_fail = 0
				self.trading = 1

			elif self.trading == 1:

				if len(self.prices_list) == self.sample_amount and self.new_sample == True:
					self.new_sample = False
					coin_analyzis = []
					
					for coin, info in self.prices_list[0].iteritems():
						coin_rate = 0
						coin_initial = 0
						for i, price_list in enumerate(self.prices_list):

							if self.prices_list[i][coin] > coin_initial:
								coin_rate += 1
							elif self.prices_list[i][coin] == coin_initial:
								coin_rate += .4

							coin_initial = self.prices_list[i][coin]

						coin_analyzis.append({'coin': coin, 'rate': float(coin_rate/self.sample_amount), 'delta': int(self.prices_list[self.sample_amount - 1][coin] - self.prices_list[0][coin]), 'percent': float(((self.prices_list[self.sample_amount - 1][coin] * 100.000) / self.prices_list[0][coin]) - 100.000), 'volume': self.volumes[coin]})

					coin_analyzis = filter(lambda x: x['rate'] >= 0.8 and x['percent'] >= 0.500 and x['volume'] >= 400, coin_analyzis)
					coin_analyzis = sorted(coin_analyzis, key=lambda x: (x['rate'], x['percent']), reverse=True)

					if len(coin_analyzis) > 0:
						self.trading_coin = coin_analyzis[0]['coin']
						self.msgWarning('TRADING', 'Moneda seleccionada: %s' % self.trading_coin)
						self.msgBlack('%s' % coin_analyzis[0], '')
						self.pushbullet.push_note('Moneda seleccionada: %s' % self.trading_coin, '%s' % coin_analyzis[0])
						self.trading = 2

			elif self.trading == 2:
				if self.trading_test == False:
					buy = self.buy(self.trading_coin, self.trading_buy_strategy)
				else:
					coin_info = self.getCoinInfo(self.trading_coin)
					tick_price = coin_info['tick_price']
					tick_qty = coin_info['tick_qty']
					max_price = coin_info['max_price']
					max_qty = coin_info['max_qty']
					min_notional = coin_info['min_notional']
					min_price = coin_info['min_price']
					min_qty = coin_info['min_qty']
					price = float(filter(lambda x: x['symbol'] == self.trading_coin.upper()+'BTC', self.client.get_all_tickers())[0]['price'])
					price += (tick_price * self.trading_buy_strategy['tick'])
					price = self.floatPrecision(price, tick_price)
					amount = float(self.client.get_asset_balance(asset='BTC')['free'])
					amount = (self.trading_buy_strategy['balance_percent'] * amount) / float(price)
					amount = self.floatPrecision(amount, tick_qty)
					buy = {'error': False, 'id': 0, 'price': self.toSatoshi(price), 'amount': float(amount)}

				print buy

				if buy['error'] == False:
					self.trading_buy_price = buy['price']
					self.trading_buy_amount = buy['amount']
					self.trading_high_count = 0
					self.trading_high_price = 0
					self.trading_high_percent = 0.000
					self.stop_loss = 1.000
					self.negative_percent_time = timenow
					self.negative_stop_loss_wait = 60
					self.trading = 3
				else:
					self.msgError('TRADING', 'Error al comprar')
					self.pumping = 1
			
			elif self.trading == 3:

				if self.trading_coin in prices:
					current_price = prices[self.trading_coin]
					current_percent = float((current_price * 100.000) / self.trading_buy_price)

					if current_percent > 100.000 and current_price > self.trading_high_price:
						self.trading_high_price = current_price
						self.trading_high_percent = current_percent
						self.trading_high_count += 1
						self.negative_percent_time = timenow
						self.msgSuccess('%s%%' % self.floatPrecision(current_percent, .001), '**** %s BTC ****' % self.toBtc(current_price))
					else:
						if current_percent < 100.000:
							self.msgError('%s%%' % self.floatPrecision(current_percent, .001), '%s BTC' % self.toBtc(current_price))
						else:
							self.negative_percent_time = timenow
							self.msgSuccess('%s%%' % self.floatPrecision(current_percent, .001), '%s BTC' % self.toBtc(current_price))

					count_1 = (self.trading_high_count == 1) and current_percent >= 100.100
					count_2 = self.trading_high_count >= 2
					count_3 = ((timenow - self.negative_percent_time) >= self.negative_stop_loss_wait) and current_percent < 100.000
					count_4 = current_percent <= (100.000 - self.stop_loss)

					if count_1 or count_2 or count_3 or count_4:

						if self.trading_test == False:
							sell = self.sell(self.trading_coin, self.trading_sell_strategy)
						else:
							coin_info = self.getCoinInfo(self.trading_coin)
							tick_price = coin_info['tick_price']
							tick_qty = coin_info['tick_qty']
							max_price = coin_info['max_price']
							max_qty = coin_info['max_qty']
							min_notional = coin_info['min_notional']
							min_price = coin_info['min_price']
							min_qty = coin_info['min_qty']
							price = float(filter(lambda x: x['symbol'] == self.trading_coin.upper()+'BTC', self.client.get_all_tickers())[0]['price'])
							price += (tick_price * self.trading_sell_strategy['tick'])
							price = self.floatPrecision(price, tick_price)
							amount = float(self.trading_buy_amount)
							# amount = amount - ((0.050*amount)/100.000)
							amount += float(self.client.get_asset_balance(asset=self.trading_coin.upper())['free'])
							# amount += 0.980 if int(tick_price) == 1 else 0.000
							amount = self.trading_sell_strategy['balance_percent'] * amount
							amount = self.floatPrecision(amount, tick_qty)
							sell = {'error': False, 'id': 0, 'price': self.toSatoshi(price), 'amount': float(amount)}

						print sell

						if sell['error'] == False:
							trade_balance = int((sell['price'] * sell['amount']) - (self.trading_buy_price * self.trading_buy_amount))
							self.total_balance += trade_balance

							self.pushbullet.push_note('Balances', 'Trading:: %s Total:: %s' % (trade_balance, self.total_balance))

							if trade_balance < 0:
								self.trading_fail += 1
								self.msgError('TRADING BALANCE', '%s satoshi' % trade_balance)
							else:
								self.trading_success += 1
								self.msgSuccess('TRADING BALANCE', '%s satoshi' % trade_balance)

							if self.total_balance < 0:
								self.msgError('TOTAL TRADING BALANCE', '%s satoshi' % self.total_balance)
							else:
								self.msgSuccess('TOTAL TRADING BALANCE', '%s satoshi' % self.total_balance)

							self.msgWarning('SUCCESS:: %s / FAIL:: %s' % (self.trading_success, self.trading_fail),'')
						else:
							self.msgError('TRADING', 'Error al vender')
							self.msgError('TRADING', 'Trading finalizado...')
							self.trading = 4

						self.msgWarning('TRADING', 'Trading finalizado...')
						self.trading = 1

	def pump(self):
		self.pumping = 0
		self.socket = BinanceSocketManager(self.client)
		self.socket.start_ticker_socket(self.processPumpTicker)
		self.socket.run()

	def trade(self):
		self.trading = 0
		self.trading_test = False
		self.socket = BinanceSocketManager(self.client)
		self.socket.start_ticker_socket(self.processTradeTicker)
		self.socket.run()