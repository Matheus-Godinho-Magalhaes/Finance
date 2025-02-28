# C$50 Finance

C$50 Finance is a web application that allows users to "buy" and "sell" stocks using real-time stock prices from the IEX Cloud API. This project was developed as part of Harvard University's **CS50: Introduction to Computer Science** course.

## Features

- **User Registration**: Users can register by providing a username and password.
- **Login/Logout**: Users can log in and out of their accounts.
- **Stock Lookup**: Users can look up the current price of any stock.
- **Buy Stocks**: Users can buy stocks if they have sufficient cash.
- **Sell Stocks**: Users can sell stocks they own.
- **Portfolio**: Users can view their stock portfolio, including total holdings and cash balance.
- **Transaction History**: Users can view a history of all their transactions.
- **Add Cash**: Users can add additional cash to their account.

## Technologies Used

- **Flask**: Python web framework for building the application.
- **SQLite**: Database for storing user and transaction data.
- **IEX Cloud API**: API for fetching real-time stock prices.
- **Jinja2**: Templating engine for rendering HTML pages.
- **Bootstrap**: CSS framework for styling the interface.

## Project Structure

- **app.py**: Main application logic, including routes and request handling.
- **helpers.py**: Helper functions, such as `lookup` for stock prices and `login_required` for route protection.
- **templates/**: HTML templates for the application pages.
- **static/**: Static files like CSS and JavaScript.
- **finance.db**: SQLite database storing user and transaction data.

## Routes

- **`/`**: Homepage displaying the user's portfolio.
- **`/login`**: User login page.
- **`/logout`**: Logs out the user.
- **`/register`**: User registration page.
- **`/quote`**: Page to look up stock prices.
- **`/buy`**: Page to buy stocks.
- **`/sell`**: Page to sell stocks.
- **`/history`**: Page displaying transaction history.
- **`/addsaldo`**: Page to add cash to the user's account.

## Usage Examples

1. **Register and Login**:
   - Visit `/register` to create a new account.
   - Log in at `/login`.

2. **Look Up Stock Prices**:
   - Visit `/quote` and enter a stock symbol (e.g., NFLX) to view its current price.

3. **Buy Stocks**:
   - Visit `/buy`, enter a stock symbol, and specify the number of shares to purchase.

4. **Sell Stocks**:
   - Visit `/sell`, select a stock, and specify the number of shares to sell.

5. **Add Cash**:
   - Visit `/addsaldo` to add cash to your account.
