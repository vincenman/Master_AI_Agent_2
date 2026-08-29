import gradio as gr
from backend import AccountManager

# Color palette
COLOR_PRIMARY = "#ecad0a"
COLOR_SECONDARY = "#209dd7"
COLOR_TERTIARY = "#753991"
COLOR_GRAY_LIGHT = "#cccccc"
COLOR_GRAY_DARK = "#444444"

# Instantiate the AccountManager
account_manager = AccountManager()

USERNAME = "user"  # single user system

def create_account():
    created = account_manager.create_account(USERNAME)
    if created:
        return "Account created successfully!"
    else:
        return "Account already exists."

def deposit_funds(amount):
    if amount is None or amount <= 0:
        return "Please enter a positive deposit amount."
    success = account_manager.deposit_funds(USERNAME, amount)
    if success:
        return f"Deposited ${amount:.2f} successfully."
    else:
        return "Deposit failed. Ensure you have an account and amount is positive."

def withdraw_funds(amount):
    if amount is None or amount <= 0:
        return "Please enter a positive withdrawal amount."
    success = account_manager.withdraw_funds(USERNAME, amount)
    if success:
        return f"Withdrew ${amount:.2f} successfully."
    else:
        return "Withdrawal failed. Check balance and amount."

def buy_shares(symbol, quantity):
    if not symbol or quantity is None or quantity <= 0:
        return "Enter valid symbol and positive quantity to buy."
    success = account_manager.buy_shares(USERNAME, symbol.upper(), quantity)
    if success:
        return f"Bought {quantity} shares of {symbol.upper()} successfully."
    else:
        return "Buy failed. Check funds, symbol, and quantity."

def sell_shares(symbol, quantity):
    if not symbol or quantity is None or quantity <= 0:
        return "Enter valid symbol and positive quantity to sell."
    success = account_manager.sell_shares(USERNAME, symbol.upper(), quantity)
    if success:
        return f"Sold {quantity} shares of {symbol.upper()} successfully."
    else:
        return "Sell failed. Check holdings, symbol, and quantity."

def refresh_status():
    if USERNAME not in account_manager.accounts:
        return (
            "No account.",
            [],
            [],
            "$0.00",
            "$0.00",
            "$0.00"
        )
    holdings = account_manager.get_holdings(USERNAME)
    holdings_df = [[sym, qty] for sym, qty in holdings.items()]
    balance = account_manager.get_balance(USERNAME)
    portfolio_val = account_manager.get_portfolio_value(USERNAME)
    profit_loss = account_manager.get_profit_loss(USERNAME)

    # Format values
    balance_str = f"${balance:.2f}"
    portfolio_val_str = f"${portfolio_val:.2f}"
    profit_loss_str = f"${profit_loss:.2f}"

    # Color profit_loss
    # Using text symbols for up/down arrows
    if profit_loss > 0:
        profit_loss_str = f"(\u2191) {profit_loss_str}"
    elif profit_loss < 0:
        profit_loss_str = f"(\u2193) {profit_loss_str}"

    transactions = account_manager.get_transaction_history(USERNAME)
    # Format transactions for Dataframe display
    tx_data = []
    for tx in transactions:
        if tx['type'] == 'deposit':
            tx_data.append(["Deposit", "-", "-", f"${tx['amount']:.2f}"])
        elif tx['type'] == 'withdraw':
            tx_data.append(["Withdraw", "-", "-", f"${tx['amount']:.2f}"])
        elif tx['type'] == 'buy':
            tx_data.append([
                "Buy",
                tx['symbol'],
                tx['quantity'],
                f"-${tx['total_cost']:.2f}"
            ])
        elif tx['type'] == 'sell':
            tx_data.append([
                "Sell",
                tx['symbol'],
                tx['quantity'],
                f"+${tx['total_revenue']:.2f}"
            ])

    return (
        "Account data refreshed.",
        holdings_df,
        tx_data,
        balance_str,
        portfolio_val_str,
        profit_loss_str
    )


def gradio_interface() -> gr.Blocks:
    demo = gr.Blocks()

    # Add components and logic inside the Blocks context
    with demo:
        gr.Markdown("# Trading Simulation Account Management", elem_id="header")

        # Account creation and status
        with gr.Row():
            create_acct_btn = gr.Button("Create Account", elem_classes="primary-btn")
            create_acct_status = gr.Textbox(value="No account created yet.", interactive=False, elem_classes="status-message")

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Deposit Funds")
                deposit_input = gr.Number(label="Amount to deposit ($)")
                deposit_btn = gr.Button("Deposit", elem_classes="primary-btn")
                deposit_status = gr.Textbox(value="", interactive=False)

            with gr.Column():
                gr.Markdown("### Withdraw Funds")
                withdraw_input = gr.Number(label="Amount to withdraw ($)")
                withdraw_btn = gr.Button("Withdraw", elem_classes="primary-btn")
                withdraw_status = gr.Textbox(value="", interactive=False)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Buy Shares")
                buy_symbol_input = gr.Textbox(label="Stock Symbol (e.g. AAPL)")
                buy_quantity_input = gr.Number(label="Quantity")
                buy_btn = gr.Button("Buy", elem_classes="primary-btn")
                buy_status = gr.Textbox(value="", interactive=False)

            with gr.Column():
                gr.Markdown("### Sell Shares")
                sell_symbol_input = gr.Textbox(label="Stock Symbol (e.g. AAPL)")
                sell_quantity_input = gr.Number(label="Quantity")
                sell_btn = gr.Button("Sell", elem_classes="primary-btn")
                sell_status = gr.Textbox(value="", interactive=False)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Holdings")
                holdings_df_output = gr.Dataframe(headers=["Symbol", "Quantity"], interactive=False)

            with gr.Column():
                gr.Markdown("### Transaction History")
                transactions_df_output = gr.Dataframe(headers=["Type", "Symbol", "Quantity", "Amount"], interactive=False)

        with gr.Row():
            with gr.Column():
                gr.Markdown("### Balance")
                balance_label = gr.Label(value="$0.00")

            with gr.Column():
                gr.Markdown("### Portfolio Value")
                portfolio_value_label = gr.Label(value="$0.00")

            with gr.Column():
                gr.Markdown("### Profit / Loss")
                profit_loss_label = gr.Label(value="$0.00")

        # Wire events
        create_acct_btn.click(fn=create_account, inputs=[], outputs=create_acct_status)

        deposit_btn.click(fn=deposit_funds, inputs=deposit_input, outputs=deposit_status).then(
            fn=refresh_status,
            inputs=[],
            outputs=[create_acct_status, holdings_df_output, transactions_df_output, balance_label, portfolio_value_label, profit_loss_label]
        )

        withdraw_btn.click(fn=withdraw_funds, inputs=withdraw_input, outputs=withdraw_status).then(
            fn=refresh_status,
            inputs=[],
            outputs=[create_acct_status, holdings_df_output, transactions_df_output, balance_label, portfolio_value_label, profit_loss_label]
        )

        buy_btn.click(fn=buy_shares, inputs=[buy_symbol_input, buy_quantity_input], outputs=buy_status).then(
            fn=refresh_status,
            inputs=[],
            outputs=[create_acct_status, holdings_df_output, transactions_df_output, balance_label, portfolio_value_label, profit_loss_label]
        )

        sell_btn.click(fn=sell_shares, inputs=[sell_symbol_input, sell_quantity_input], outputs=sell_status).then(
            fn=refresh_status,
            inputs=[],
            outputs=[create_acct_status, holdings_df_output, transactions_df_output, balance_label, portfolio_value_label, profit_loss_label]
        )

        refresh_btn = gr.Button("Refresh Account Data", elem_classes="secondary-btn")
        refresh_btn.click(fn=refresh_status, inputs=[], outputs=[create_acct_status, holdings_df_output, transactions_df_output, balance_label, portfolio_value_label, profit_loss_label])

    return demo

# If run directly, can uncomment below to launch
# if __name__ == "__main__":
#     gradio_interface().launch()
