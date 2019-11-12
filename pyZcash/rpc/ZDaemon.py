import requests
import json
import binascii

from pyZcash.settings import *

class ZDaemon(object):

	id_count = 0

	def __init__(self, network=NETWORK, user=RPCUSER, password=RPCPASSWORD, timeout=TIMEOUT):
		#TODO: check utf safety
		self.network = network
		self.user = user.encode('utf8')
		self.password = password.encode('utf8')
		self.timeout = timeout

	def _call(self,  method, *args):
		jsondata = json.dumps({	'version': '2',
				'method': method,
				'params': args,
				'id': self.id_count})

		r = requests.post(self.network, auth=(self.user,self.password), data=jsondata, timeout=self.timeout)

		self.id_count += 1

		resp = json.loads(r.text)

		#TODO: deal with errors better.
		error = resp['error']
		if error:
			print('Error calling {}:{}'.format(method, error))

		return resp['result']


	#Block Info
	def getBlockHash(self, blockheight):
		return self._call('getblockhash', blockheight)

	def getBlockByHash(self, blockhash):
		return self._call('getblock', blockhash)

	def getRawTransaction(self, txid):
		return self._call('getrawtransaction', txid, 1)

	def getBlockByHeight(self, blockheight):
		return self.getBlockByHash(self.getBlockHash(blockheight))

	# Custom methods to get Network Info
	def getNetworkHeight(self):
		return self._call('getblockcount')

	def getInfo(self):
		return self._call('getinfo')

	def getChainTips(self):
		return self._call('getchaintips')

	def getMempoolInfo(self):
		return self._call('getmempoolinfo')

	def getNetworkSolps(self):
		return self._call('getnetworksolps')

	def getNetTotals(self):
		return self._call('getnettotals')

	def getNetworkDifficulty(self):
		return self._call('getdifficulty')

	def getVersion(self):
		info = self._call('getnetworkinfo')
		client = info['subversion']
		version = client.strip('/').split(':')[1]
		return version

	def getConnectionCount(self):
		return self._call('getconnectioncount')


	# Wallet Info (transparent)
	def getbalance(self):
		return self._call('getbalance')

	def listunspent(self, minconf=1):
		return self._call('listunspent', minconf)

	#Raw Txs
	def gettransaction(self, txid):
		return self._call('gettransaction', txid)

	def getrawtransaction(self, txid, verbose=0):
		# default verbose=0 returns serialized, hex-encoded data
		# verbose=1, returns a JSON obj of tx
		return self._call('getrawtransaction', txid, verbose)

	def decoderawtransaction(self, txhex):
		return self.call('decoderawtransaction', txhex)

	# taddr methods
	def getnewaddress(self):
		return self._call('getnewaddress')

	def sendtoaddress(self, taddress, amount):
		return self._call('sendtoaddress', taddress, amount)

	def listunspent(self):
		return self._call('listunspent')

	# Custom method to find a taddr with spendable utxos for z_sendmany
	def find_taddr_with_unspent(self):
		unspent = self._call('listunspent')
		for utxo in unspent:
			if utxo['spendable'] == True and utxo['amount'] > 0.1:
				# Check that it's not a coinbase tx
				tx = zd.gettransaction(utxo['txid'])
				if 'generated' not in tx:
					return tx['address']

	def sweep_coinbase(self, zaddr):
		addrs = []
		utxos = self.listunspent()
		for utxo in utxos:
			if 'generated' in utxo and utxo['generated'] == True:
				if utxo['address'] not in addrs:
					addrs.append(utxo['address'])
		for addr in addrs:
			res = self._call('z_shieldcoinbase', addr, zaddr)
			print('{}'.format(res))

	# zaddr methods
	def z_gettotalbalance(self):
		return self._call('z_gettotalbalance')

	def z_getnewaddress(self):
		return self._call('z_getnewaddress')

	def z_listaddresses(self):
		return self._call('z_listaddresses')

	def z_listreceivedbyaddress(self, zaddr, minconf=1):
		return self._call('z_listreceivedbyaddress', zaddr, minconf)

	def z_getoperationstatus(self, opid):
		return self._call('z_getoperationstatus', ["{0}".format(opid)])

	def z_getoperationresult(self, opid):
		return self._call('z_getoperationresult', ["{0}".format(opid)])

	# With addition of encrypted memo field
	def z_sendmany(self, sender, receiver, amount=0.0001, memo='', fee=0.0001):
		amts_array = []
		if memo == '':
			amounts = {"address": receiver, "amount": amount}
		else:
			memo = binascii.hexlify(str.encode(memo)).decode()
			amounts = {"address": receiver, "amount": amount, "memo": memo}
		amts_array.append(amounts)
		return self._call('z_sendmany', sender, amts_array, 1, fee)
