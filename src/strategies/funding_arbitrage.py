from exchange.binance_client import BinanceClient
from utils.calculator import calculate_position_size
from utils.logger import get_logger
import time

logger = get_logger()

class FundingArbitrage:
    def __init__(self, config):
        self.config = config
        # 初始化币安客户端
        self.exchange = BinanceClient(
            config['api_key'],
            config['api_secret'],
            config.get('is_test', False)
        )
        
        # 策略参数
        self.funding_threshold = config['funding_threshold']
        self.spread_threshold = config['spread_threshold']
        self.check_interval = config['check_interval']
        self.trading_pairs = config['trading_pairs'] # 例如 ['BTC/USDT', 'ETH/USDT']

    def check_arbitrage_opportunity(self, pair):
        """
        检查套利机会
        pair: 例如 "BTC/USDT"
        """
        # 获取现货和永续合约价格
        spot_price = self.exchange.get_ticker(pair, type='spot')
        swap_price = self.exchange.get_ticker(pair, type='future')
        funding_rate = self.exchange.get_funding_rate(pair)

        if not all([spot_price, swap_price, funding_rate is not None]):
            logger.warning(f"{pair} 数据获取不完整")
            return False

        logger.info(f"--- 监控中: {pair} ---")
        logger.info(f"现货价格: {spot_price}")
        logger.info(f"合约价格: {swap_price}")
        logger.info(f"资金费率: {funding_rate * 100:.4f}%") # 转换为百分比显示

        # 逻辑：资金费率为正 -> 做空合约，做多现货
        # 这里的阈值通常很小，例如 0.0001 (0.01%)
        if funding_rate > self.funding_threshold:
            # 计算价差 (合约 - 现货)
            price_diff = swap_price - spot_price
            price_diff_percent = (price_diff / spot_price)
            
            logger.info(f"当前价差: {price_diff_percent*100:.4f}% (阈值: {self.spread_threshold*100}%)")

            if price_diff_percent > self.spread_threshold:
                logger.info(">>> 发现套利机会！ <<<")
                return True
        
        return False

    def execute_arbitrage(self, pair):
        """执行套利交易 (目前仅打印日志，不实盘，防止新手亏损)"""
        try:
            position_size = calculate_position_size(
                self.exchange,
                pair,
                self.config['max_position_size']
            )
            
            logger.info(f"正在执行套利 - {pair}")
            logger.info(f"建议仓位: {position_size}")
            logger.info("警告：实盘交易代码已注释，请先观察日志确认逻辑正确。")
            
            # TODO: 实盘逻辑需要分别下单：
            # 1. self.exchange.spot_exchange.create_market_buy_order(pair, amount)
            # 2. self.exchange.exchange.create_market_sell_order(pair, amount)
            
        except Exception as e:
            logger.error(f"执行套利失败: {str(e)}")

    def run(self):
        """运行套利策略"""
        logger.info("开始运行币安资金费率套利策略...")
        
        while True:
            try:
                for pair in self.trading_pairs:
                    if self.check_arbitrage_opportunity(pair):
                        self.execute_arbitrage(pair)
                
                # 休息一段时间
                time.sleep(self.check_interval)
                
            except Exception as e:
                logger.error(f"策略运行错误: {str(e)}")
                time.sleep(self.check_interval)
