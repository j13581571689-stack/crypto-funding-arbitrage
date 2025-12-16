import ccxt
from utils.logger import get_logger

logger = get_logger()

class BinanceClient:
    def __init__(self, api_key, api_secret, is_test=False):
        """
        初始化币安客户端 (使用 CCXT)
        """
        self.exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'future',  # 默认为合约账户
                'adjustForTimeDifference': True, # 自动校准时间
            }
        })
        
        # 如果是测试环境 (Binance Testnet)
        if is_test:
            self.exchange.set_sandbox_mode(True)
            
        # 初始化现货客户端用于查询现货价格
        self.spot_exchange = ccxt.binance({
            'apiKey': api_key,
            'secret': api_secret,
            'enableRateLimit': True,
            'options': {
                'defaultType': 'spot', 
            }
        })

    def get_funding_rate(self, symbol):
        """
        获取资金费率
        symbol格式: 'BTC/USDT'
        """
        try:
            # 币安合约获取资金费率
            funding_info = self.exchange.fetch_funding_rate(symbol)
            return float(funding_info['fundingRate'])
        except Exception as e:
            logger.error(f"获取资金费率失败 {symbol}: {str(e)}")
            return None

    def get_ticker(self, symbol, type='future'):
        """
        获取最新价格
        type: 'future' (合约) 或 'spot' (现货)
        """
        try:
            if type == 'spot':
                ticker = self.spot_exchange.fetch_ticker(symbol)
            else:
                ticker = self.exchange.fetch_ticker(symbol)
            return float(ticker['last'])
        except Exception as e:
            logger.error(f"获取价格失败 {symbol} ({type}): {str(e)}")
            return None

    def get_balance(self):
        """获取USDT余额"""
        try:
            balance = self.exchange.fetch_balance()
            return float(balance['USDT']['free'])
        except Exception as e:
            logger.error(f"获取余额失败: {str(e)}")
            return 0.0
