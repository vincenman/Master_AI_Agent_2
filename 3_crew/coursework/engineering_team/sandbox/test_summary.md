import unittest
from backend import AccountManager, get_share_price

class TestAccountManager(unittest.TestCase):
    def setUp(self):
        self.am = AccountManager()
        self.username = 'testuser'
        self.am.create_account(self.username)

    def test_create_account(self):
        # creating duplicate account should fail
        self.assertFalse(self.am.create_account(self.username))
        # new user
        self.assertTrue(self.am.create_account('newuser'))

    def test_deposit_withdraw(self):
        # deposit positive amount
        self.assertTrue(self.am.deposit_funds(self.username, 1000.0))
        self.assertEqual(self.am.get_balance(self.username), 1000.0)
        # withdraw some amount
        self.assertTrue(self.am.withdraw_funds(self.username, 200.0))
        self.assertEqual(self.am.get_balance(self.username), 800.0)
        # withdraw more than balance
        self.assertFalse(self.am.withdraw_funds(self.username, 1000.0))
        self.assertEqual(self.am.get_balance(self.username), 800.0)
        # deposit negative or zero amount
        self.assertFalse(self.am.deposit_funds(self.username, 0))
        self.assertFalse(self.am.deposit_funds(self.username, -100))
        # withdraw negative or zero amount
        self.assertFalse(self.am.withdraw_funds(self.username, 0))
        self.assertFalse(self.am.withdraw_funds(self.username, -50))
        # deposit to unknown user
        self.assertFalse(self.am.deposit_funds('nouser', 100))
        # withdraw from unknown user
        self.assertFalse(self.am.withdraw_funds('nouser', 100))

    def test_buy_sell_shares(self):
        self.am.deposit_funds(self.username, 10000.0)
        # buy shares with valid symbol and quantity
        self.assertTrue(self.am.buy_shares(self.username, 'AAPL', 10))
        # not enough funds
        self.assertFalse(self.am.buy_shares(self.username, 'TSLA', 1000))
        # invalid quantity
        self.assertFalse(self.am.buy_shares(self.username, 'AAPL', 0))
        self.assertFalse(self.am.buy_shares(self.username, 'AAPL', -1))
        # invalid symbol
        self.assertFalse(self.am.buy_shares(self.username, '', 5))
        self.assertFalse(self.am.buy_shares(self.username, 'INVALID', 5))

        # sell shares valid
        self.assertTrue(self.am.sell_shares(self.username, 'AAPL', 5))
        # sell shares more than owned
        self.assertFalse(self.am.sell_shares(self.username, 'AAPL', 10))
        # sell shares invalid quantity
        self.assertFalse(self.am.sell_shares(self.username, 'AAPL', 0))
        self.assertFalse(self.am.sell_shares(self.username, 'AAPL', -5))
        # sell shares invalid symbol
        self.assertFalse(self.am.sell_shares(self.username, '', 5))
        # sell shares not owned symbol
        self.assertFalse(self.am.sell_shares(self.username, 'TSLA', 1))

    def test_invalid_withdraw(self):
        self.am.deposit_funds(self.username, 50)
        self.assertFalse(self.am.withdraw_funds(self.username, 100))  # withdraw more than balance
        self.assertFalse(self.am.withdraw_funds('nouser', 10))  # unknown user
        self.assertFalse(self.am.withdraw_funds(self.username, -10))  # negative amount
        self.assertFalse(self.am.withdraw_funds(self.username, 0))  # zero amount

    def test_invalid_buy(self):
        # Buy with no funds
        self.assertFalse(self.am.buy_shares(self.username, 'AAPL', 1))
        self.am.deposit_funds(self.username, 100)
        # invalid symbol
        self.assertFalse(self.am.buy_shares(self.username, 'FAKE', 1))
        # invalid quantity
        self.assertFalse(self.am.buy_shares(self.username, 'AAPL', 0))
        self.assertFalse(self.am.buy_shares(self.username, 'AAPL', -1))

    def test_invalid_sell(self):
        self.am.deposit_funds(self.username, 10000)
        self.am.buy_shares(self.username, 'AAPL', 5)
        # sell more than owned
        self.assertFalse(self.am.sell_shares(self.username, 'AAPL', 10))
        # sell invalid quantity
        self.assertFalse(self.am.sell_shares(self.username, 'AAPL', 0))
        self.assertFalse(self.am.sell_shares(self.username, 'AAPL', -5))
        # sell unknown symbol
        self.assertFalse(self.am.sell_shares(self.username, 'TSLA', 1))

    def test_portfolio_value_and_profit_loss(self):
        self.am.deposit_funds(self.username, 10000)
        self.am.buy_shares(self.username, 'AAPL', 10)  # 1500 spent
        self.am.buy_shares(self.username, 'TSLA', 5)   # 3500 spent
        portfolio_value = self.am.get_portfolio_value(self.username)
        self.assertAlmostEqual(portfolio_value, 1500 + 3500)
        profit_loss = self.am.get_profit_loss(self.username)
        expected_balance = 10000 - (1500 + 3500)
        expected_total = expected_balance + portfolio_value
        self.assertAlmostEqual(profit_loss, expected_total - 10000)

    def test_transaction_history(self):
        self.am.deposit_funds(self.username, 1000)
        self.am.buy_shares(self.username, 'AAPL', 5)
        self.am.sell_shares(self.username, 'AAPL', 2)
        txs = self.am.get_transaction_history(self.username)
        self.assertEqual(len(txs), 3)
        self.assertTrue(any(tx['type'] == 'deposit' for tx in txs))
        self.assertTrue(any(tx['type'] == 'buy' for tx in txs))
        self.assertTrue(any(tx['type'] == 'sell' for tx in txs))

if __name__ == '__main__':
    unittest.main()