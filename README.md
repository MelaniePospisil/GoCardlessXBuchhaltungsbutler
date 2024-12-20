# Finance Automation Script

## Overview
This script automates the retrieval and booking of payout transactions from GoCardless to BuchhaltungsButler. It fetches payout data for a specific date range, matches them with transactions based on the reference, and books them into the accounting system.

## Prerequisites
- Python 3.x
- Requests library
- Pandas library
- datetime library

## Configuration
Update the `API_KEY`, `API_CLIENT`, and `API_SECRET` variables in the script with your actual GoCardless and BuchhaltungsButler API credentials.
Also update the booking timespan to the desired timeperiod :)

## Usage
Run the script with:
```bash
python finance_script.py
```
The script will automatically:
1. Fetch payouts from GoCardless.
2. Retrieve transactions from BuchhaltungsButler for the specified date range.
3. Match payouts to transactions based on the reference.
4. Create bookings in BuchhaltungsButler for the matched transactions.

## Functions
### `fetch_payouts()`
Fetches payout data from GoCardless.

### `get_transactions(date_from, date_to)`
Retrieves transactions from BuchhaltungsButler for a specified date range.

### `find_transaction_by_purpose(transactions, search_purpose)`
Finds a transaction by its purpose.

### `create_transaction_posting(transaction_id, total_amount, deducted_fees)`
Posts a transaction booking to BuchhaltungsButler.

## Error Handling
The script includes basic prints to ensure that the user has an overview of the fetched and booked payments.

## Author
Melanie Pospisil
