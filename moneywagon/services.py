from .core import Service, NoService, NoData, SkipThisService
import arrow

class Bitstamp(Service):
    supported_cryptos = ['btc']

    def get_current_price(self, crypto, fiat):
        if fiat.lower() != 'usd':
            raise SkipThisService('Bitstamp only does USD->BTC')

        url = "https://www.bitstamp.net/api/ticker/"
        response = self.get_url(url).json()
        return (float(response['last']), 'bitstamp')


class BlockCypher(Service):
    supported_cryptos = ['btc', 'ltc', 'uro']

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://api.blockcypher.com/v1/%s/main/addrs/%s" % (crypto, address)
        response = self.get_url(url)
        return response.json()['balance'] / 1.0e8


class Blockr(Service):
    supported_cryptos = ['btc', 'ltc', 'ppc', 'mec', 'qrk', 'dgc', 'tbtc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://%s.blockr.io/api/v1/address/info/%s" % (crypto, address)
        response = self.get_url(url)
        return response.json()['data']['balance']

    def get_transactions(self, crypto, address, confirmations=1):
        url = 'http://%s.blockr.io/api/v1/address/txs/%s' % (crypto, address)
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            transactions.append(dict(
                date=arrow.get(tx['time_utc']).datetime,
                amount=tx['amount'],
                txid=tx['tx'],
                confirmations=tx['confirmations'],
            ))
        return transactions

    def push_tx(self, crypto, tx):
        url = "http://%s.blockr.io/api/v1/tx/push" % crypto
        response = self.post_url(url, {'tx': tx})
        return response.json()['data']


class Toshi(Service):
    url = "https://bitcoin.toshi.io/api/v0"

    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/addresses/%s" % (self.url, address)
        response = self.get_url(url).json()
        return response['balance'] / 1e8

    def get_transactions(self, crypto, address, confirmations=1):
        """
        This call also returns unconfirmed transactions.
        """
        url = "%s/addresses/%s/transactions" % (self.url, address)
        response = self.get_url(url).json()

        if confirmations == 0:
            to_iterate = response['transactions'] + response['unconfirmed_transactions']
        else:
            to_iterate = response['transactions']

        transactions = []
        for tx in to_iterate:
            transactions.append(dict(
                amount=sum([x['amount'] / 1e8 for x in tx['outputs'] if address in x['addresses']]),
                txid=tx['hash'],
            ))
        return transactions

    def push_tx(self, tx):
        url = "%s/transactions/%s" % (self.url, tx)
        return self.get_url(url).json()['hash']


class BTCE(Service):
    def get_current_price(self, crypto, fiat):
        pair = "%s_%s" % (crypto, fiat)
        url = "https://btc-e.com/api/3/ticker/" + pair
        response = self.get_url(url).json()
        return (response[pair]['last'], 'btc-e')


class Cryptonator(Service):
    def get_current_price(self, crypto, fiat):
        pair = "%s-%s" % (crypto, fiat)
        url = "https://www.cryptonator.com/api/ticker/%s" % pair
        response = self.get_url(url).json()
        return float(response['ticker']['price']), 'cryptonator'


class Winkdex(Service):
    supported_cryptos = ['btc']

    def get_current_price(self, crypto, fiat):
        if fiat != 'usd':
            raise SkipThisService("winkdex is btc->usd only")
        url = "https://winkdex.com/api/v0/price"
        return self.get_url(url).json()['price'] / 100.0, 'winkdex'


class BlockStrap(Service):
    """
    Documentation here: http://docs.blockstrap.com/en/api/
    """
    domain = 'api.blockstrap.com'
    supported_cryptos = ['btc', 'ltc', 'drk', 'doge']

    def get_balance(self, crypto, address, confirmations=None):
        url = "http://%s/v0/%s/address/id/%s" % (self.domain, crypto, address)
        response = self.get_url(url).json()
        return response['data']['address']['inputs_value_confirmed'] / 1e8

    def pushtx(self, crypto, tx):
        url = "http://%s/v0/%s/transaction/relay/%s" % (self.domain, crypto, tx)
        return self.get_url(url)['data']['id']

    def get_transactions(self, crypto, address):
        url = "http://%s/v0/%s/address/transactions/%s" % (self.domain, crypto, address)
        txs = []
        for tx in self.get_url(url).json()['data']['address']['transactions']:
            s_amount = tx['tx_address_input_value'] or tx['tx_address_output_value'] * -1
            txs.append(dict(
                date=arrow.get(tx['block_time']).datetime,
                amount=s_amount / 1e8,
                confirmations=tx['confirmations'],
                txid=tx['id'],
            ))
        return txs


class BitEasy(Service):
    """
    Most functions from this servie require an API key. therefore only
    address balance is supported at this time.
    """
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "https://api.biteasy.com/blockchain/v1/addresses/" + address
        response = self.get_url(url)
        return response.json()['data']['balance'] / 1e8


class BlockChainInfo(Service):
    supported_cryptos = ['btc']

    def get_balance(self, crypto, address, confirmations=1):
        url = "http://blockchain.info/address/%s?format=json" % address
        response = self.get_url(url)
        return float(response.json()['final_balance']) * 1e-8

##################################

class BitcoinAbe(Service):
    supported_cryptos = ['btc']
    base_url = "http://bitcoin-abe.info/chain/Bitcoin"

    def get_balance(self, crypto, address, confirmations=1):
        url = self.base_url + "/q/addressbalance/" + address
        response = self.get_url(url)
        return float(response.content)

class LitecoinAbe(BitcoinAbe):
    supported_cryptos = ['ltc']
    base_url = "http://bitcoin-abe.info/chain/Litecoin"

class NamecoinAbe(BitcoinAbe):
    supported_cryptos = ['nmc']
    base_url = "http://bitcoin-abe.info/chain/Namecoin"

class DogeChainInfo(BitcoinAbe):
    supported_cryptos = ['doge']
    base_url = "https://dogechain.info/chain/Dogecoin"

class AuroraCoinEU(BitcoinAbe):
    supported_cryptos = ['aur']
    base_url = 'http://blockexplorer.auroracoin.eu/chain/AuroraCoin'

class Atorox(BitcoinAbe):
    supported_cryptos = ['aur']
    base_url = "http://auroraexplorer.atorox.net/chain/AuroraCoin"

##################################

class FeathercoinCom(Service):
    supported_cryptos = ['ftc']

    def get_balance(self, crypto, address, confirmations=1):
        url= "http://api.feathercoin.com/?output=balance&address=%s&json=1" % address
        response = self.get_url(url)
        return float(response.json()['balance'])


class NXTPortal(Service):
    supported_cryptos = ['nxt']

    def get_balance(self, crypto, address, confirmations=1):
        url='http://nxtportal.org/nxt?requestType=getAccount&account=' + address
        response = self.get_url(url)
        return float(response.json()['balanceNQT']) * 1e-8

    def get_transactions(self, crypto, address):
        url = 'http://nxtportal.org/transactions/account/%s?num=50' % address
        response = self.get_url(url)
        transactions = []
        for tx in txs:
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=tx['value'],
                txid=tx['txid'],
                confirmations=tx['confirmations'],
            ))

        return transactions


class CryptoID(Service):
    supported_cryptos = [
        'dash', 'bc', 'bay', 'block', 'cann', 'uno', 'vrc', 'xc', 'uro', 'aur',
        'pot', 'cure', 'arch', 'swift', 'karm', 'dgc', 'lxc', 'sync', 'byc',
        'pc', 'fibre', 'i0c', 'nobl', 'gsx', 'flt', 'ccn', 'rlc', 'rby', 'apex',
        'vior', 'ltcd', 'zeit', 'carbon', 'super', 'dis', 'ac', 'vdo', 'ioc',
        'xmg', 'cinni', 'crypt', 'excl', 'mne', 'seed', 'qslv', 'maryj', 'key',
        'oc', 'ktk', 'voot', 'glc', 'drkc', 'mue', 'gb', 'piggy', 'jbs', 'grs',
        'icg', 'rpc', ''
    ]

    def get_balance(self, crypto, address, confirmations=1):
        url ="http://chainz.cryptoid.info/%s/api.dws?q=getbalance&a=%s" % (crypto, address)
        return float(self.get_url(url).content)


class CryptapUS(Service):
    supported_cryptos = [
        'nmc', 'wds', 'ber', 'scn', 'sc0', 'wdc', 'nvc', 'cas', 'myr'
    ]
    def get_balance(self, crypto, address, confirmations=1):
        url = "http://cryptap.us/%s/explorer/q/addressbalance/%s" % (crypto, address)
        return float(self.get_url(url).content)


class BTER(Service):
    def get_current_price(self, crypto, fiat):
        url_template = "http://data.bter.com/api/1/ticker/%s_%s"
        url = url_template % (crypto, fiat)

        response = self.get_url(url).json()

        if response['result'] == 'false': # bter api returns this as string
            # bter doesn't support this pair, we need to make 2 calls and
            # do the math ourselves. The extra http request isn't a problem because
            # of caching. BTER only has USD, BTC and CNY
            # markets, so any other fiat will likely fail.

            url = url_template % (crypto, 'btc')
            response = self.get_url(url)
            altcoin_btc = float(response['last'])

            url = url_template % ('btc', fiat)
            response = self.get_url(url)
            btc_fiat = float(response['last'])

            return (btc_fiat * altcoin_btc), 'bter (calculated)'

        return float(response['last'] or 0), 'bter'


class CoinSwap(Service):
    def get_current_price(self, crypto, fiat):
        chunk = ("%s/%s" % (crypto, fiat)).upper()
        url = "https://api.coin-swap.net/market/stats/%s" % chunk
        response = self.get_url(url).json()
        return float(response['lastprice']), 'coin-swap'


class ChainSo(Service):
    base_url = "https://chain.so/api/v2"
    supported_cryptos = ['doge', 'btc', 'ltc']

    def get_current_price(self, crypto, fiat):
        url = "%s/get_price/%s/%s" % (self.base_url, crypto, fiat)
        resp = self.get_url(url).json()
        items = resp['data']['prices']
        if len(items) == 0:
            raise SkipThisService("Chain.so can't get price for %s/%s" % (crypto, fiat))
        return float(items[0]['price']), "%s via Chain.so" % items[0]['exchange']

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/get_address_balance/%s/%s/%s" % (
            self.base_url, crypto, address, confirmations
        )
        response = self.get_url(url)
        return float(response.json()['data']['confirmed_balance'])

    def get_transactions(self, crypto, address, confirmations=1):
        url = "%s/get_tx_received/%s/%s" % (self.base_url, crypto, address)
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['data']['txs']:
            tx_cons = int(tx['confirmations'])
            if tx_cons < confirmations:
                continue
            transactions.append(dict(
                date=arrow.get(tx['time']).datetime,
                amount=float(tx['value']),
                txid=tx['txid'],
                confirmations=tx_cons,
            ))

        # to conform with monewagon standards, most recent must be first.
        transactions.reverse()
        return transactions

    def pushtx(self, tx):
        url = "%s/send_tx/%s" % (self.base_url, crypto)
        resp = self.post_url(url, {'tx_hex': tx})
        return resp.json()['txid']

    def get_block(self, block_number=None, block_hash=None):
        url = "%s/get_block/%s/%s%s" % (
            self.base_url, crypto, block_number, block_hash
        )
        resp = self.get_url(url).json()


class ExCoIn(Service):
    # decommissioned
    def get_current_price(self, crypto, fiat):
        url = "https://api.exco.in/v1/exchange/%s/%s" % (fiat, crypto)
        response = self.get_url(url).json()
        return float(response['last_price']), 'exco.in'

################################################

class BitpayInsight(Service):
    supported_cryptos = ['btc']
    domain = "http://insight.bitpay.com"

    def get_balance(self, crypto, address, confirmations=1):
        url = "%s/api/addr/%s/balance" % (self.domain, address)
        return float(self.get_url(url).content) / 1e8

    def get_transactions(self, crypto, address):
        url = "%s/api/txs/?address=%s" % (self.domain, address)
        response = self.get_url(url)

        transactions = []
        for tx in response.json()['txs']:
            my_outs = [
                float(x['value']) for x in tx['vout'] if address in x['scriptPubKey']['addresses']
            ]
            transactions.append(dict(
                amount=sum(my_outs),
                date=arrow.get(tx['time']).datetime,
                txid=tx['txid'],
                confirmations=tx['confirmations'],
            ))

        return transactions

class MYRCryptap(BitpayInsight):
    supported_cryptos = ['myr']
    domain = "http://insight-myr.cryptap.us/"

class BirdOnWheels(BitpayInsight):
    supported_cryptos = ['myr']
    domain = "http://birdonwheels5.no-ip.org:3000"

class ThisIsVTC(BitpayInsight):
    supported_cryptos = ['vtc']
    domain = "http://explorer.thisisvtc.com"

class ReddcoinCom(BitpayInsight):
    supported_cryptos = ['rdd']
    domain = "http://live.reddcoin.com"

class FTCe(BitpayInsight):
    supported_cryptos = ['ftc']
    domain = "http://block.ftc-c.com"

class CoinTape(Service):
    supported_cryptos = ['btc']

    def get_optimal_fee(self, crypto, tx_bytes, acceptable_block_delay=0):
        url = "http://www.cointape.com/fees"
        response = self.get_url(url).json()
        for sample in response['fees']:
            if sample['maxDelay'] <= acceptable_block_delay:
                rate = sample['maxFee']
                return tx_bytes * rate


ALL_SERVICES = [
    Bitstamp, BlockCypher, Blockr, BTCE, Cryptonator, Winkdex,
    BitEasy, BlockChainInfo, BitcoinAbe, LitecoinAbe, NamecoinAbe, DogeChainInfo,
    AuroraCoinEU, Atorox, FeathercoinCom, NXTPortal, CryptoID,
    CryptapUS, BTER, CoinSwap, ChainSo, BlockStrap,

    BitpayInsight, ThisIsVTC, BirdOnWheels, MYRCryptap, ReddcoinCom, FTCe,

    CoinTape
]