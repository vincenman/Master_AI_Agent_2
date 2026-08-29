# backend.py

from typing import Dict, List, Any

# Test implementation for get_share_price() function
# Returns fixed prices for AAPL, TSLA, GOOGL as per design

def get_share_price(symbol: str) -> float:
    prices = {
        'AAPL': 150.0,
        'TSLA': 700.0,
        'GOOGL': 2700.0
    }
    return prices.get(symbol, 0.0)

class AccountManager:
    def __init__(self):
        # Store accounts data keyed by username
        # Each account stores initial_deposit(float), balance(float), holdings(dict symbol->int), transactions(list)
        self.accounts: Dict[str, Dict[str, Any]] = {}

    def create_account(self, username: str) -> bool:
        if username in self.accounts:
            return False
        self.accounts[username] = {
            'initial_deposit': 0.0,
            'balance': 0.0,
            'holdings': {},  # symbol to quantity
            'transactions': []  # list of transaction dicts
        }
        return True

    def deposit_funds(self, username: str, amount: float) -> bool:
        if username not in self.accounts or amount <= 0:
            return False
        account = self.accounts[username]
        account['balance'] += amount
        if account['initial_deposit'] == 0:
            account['initial_deposit'] = amount
        else:
            account['initial_deposit'] += amount
        transaction = {
            'type': 'deposit',
            'amount': amount
        }
        account['transactions'].append(transaction)
        return True

    def withdraw_funds(self, username: str, amount: float) -> bool:
        if username not in self.accounts or amount <= 0:
            return False
        account = self.accounts[username]
        if account['balance'] < amount:
            return False
        account['balance'] -= amount
        transaction = {
            'type': 'withdraw',
            'amount': amount
        }
        account['transactions'].append(transaction)
        return True

    def buy_shares(self, username: str, symbol: str, quantity: int) -> bool:
        if username not in self.accounts or quantity <= 0 or not symbol:
            return False
        price = get_share_price(symbol)
        if price <= 0:
            return False
        total_cost = price * quantity
        account = self.accounts[username]
        if account['balance'] < total_cost:
            return False
        # Deduct cash
        account['balance'] -= total_cost
        # Add shares
        holdings = account['holdings']
        holdings[symbol] = holdings.get(symbol, 0) + quantity
        # Record transaction
        transaction = {
            'type': 'buy',
            'symbol': symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_cost': total_cost
        }
        account['transactions'].append(transaction)
        return True

    def sell_shares(self, username: str, symbol: str, quantity: int) -> bool:
        if username not in self.accounts or quantity <= 0 or not symbol:
            return False
        account = self.accounts[username]
        holdings = account['holdings']
        if symbol not in holdings or holdings[symbol] < quantity:
            return False
        price = get_share_price(symbol)
        if price <= 0:
            return False
        total_revenue = price * quantity
        # Remove shares
        holdings[symbol] -= quantity
        if holdings[symbol] == 0:
            del holdings[symbol]
        # Add cash
        account['balance'] += total_revenue
        # Record transaction
        transaction = {
            'type': 'sell',
            'symbol': symbol,
            'quantity': quantity,
            'price_per_share': price,
            'total_revenue': total_revenue
        }
        account['transactions'].append(transaction)
        return True

    def get_portfolio_value(self, username: str) -> float:
        if username not in self.accounts:
            return 0.0
        account = self.accounts[username]
        holdings = account['holdings']
        total_value = 0.0
        for symbol, qty in holdings.items():
            price = get_share_price(symbol)
            total_value += price * qty
        return round(total_value, 2)

    def get_profit_loss(self, username: str) -> float:
        if username not in self.accounts:
            return 0.0
        account = self.accounts[username]
        initial = account['initial_deposit']
        if initial == 0:
            return 0.0
        current_total = account['balance'] + self.get_portfolio_value(username)
        profit_loss = current_total - initial
        return round(profit_loss, 2)

    def get_holdings(self, username: str) -> Dict[str, int]:
        if username not in self.accounts:
            return {}
        return dict(self.accounts[username]['holdings'])

    def get_transaction_history(self, username: str) -> List[Dict[str, Any]]:
        if username not in self.accounts:
            return []
        return list(self.accounts[username]['transactions'])

    def get_balance(self, username: str) -> float:
        if username not in self.accounts:
            return 0.0
        return round(self.accounts[username]['balance'], 2)

