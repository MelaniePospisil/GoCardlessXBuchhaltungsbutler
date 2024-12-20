import requests
import pandas as pd
from requests.auth import HTTPBasicAuth
import datetime

start_date = "2024-12-01T00:00:00Z"
end_date = "2024-12-17T23:59:59Z"

date_from = datetime.strptime(start_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")
date_to = datetime.strptime(end_date, "%Y-%m-%dT%H:%M:%SZ").strftime("%Y-%m-%d")

# GoCardless API URL and API key
API_URL = "https://api.gocardless.com/payouts"
API_KEY = "***"

# Headers for the GoCardless API request
headers = {
    "Authorization": f"Bearer {API_KEY}",
    "GoCardless-Version": "2015-07-06",
    "Content-Type": "application/json"
}

# Parameters for the GoCardless API request
params = {
    "created_at[gte]": start_date,
    "created_at[lte]": end_date,
    "limit": 100  
}

# Pagination 
def fetch_payouts():
    payouts = []
    next_after = None

    while True:
        if next_after:
            params["after"] = next_after

        response = requests.get(API_URL, headers=headers, params=params)
        if response.status_code != 200:
            print(f"Error fetching payouts: {response.status_code} - {response.text}")
            break

        data = response.json()
        payouts.extend(data.get("payouts", []))

        # Check for pagination and update the cursor for the next page
        next_after = data.get("meta", {}).get("cursors", {}).get("after")
        if not next_after:
            break

    return payouts

payouts = fetch_payouts()

# Built a DataFrame
df_payouts = pd.DataFrame([
    {
        'payout_id': payout['id'],
        'amount': payout['amount'] / 100, 
        'currency': payout['currency'],
        'created_at': payout['created_at'],
        'arrival_date': payout.get('arrival_date', 'N/A'),
        'reference': payout.get('reference', 'N/A'),
        'payout_type': payout.get('payout_type', 'N/A'),
        'deducted_fees': payout['deducted_fees'] / 100  
    }
    for payout in payouts
])

# BuchhaltungsButler API URLs und Zugangsdaten
API_URL_get_trans = "https://app.buchhaltungsbutler.de/api/v1/transactions/get"
API_URL_book = "https://app.buchhaltungsbutler.de/api/v1/postings/add/transaction"
API_KEY = "***"
API_CLIENT = "***"
API_SECRET = "***"


# Get the transactions 
def get_transactions(date_from, date_to):
    headers = {
        "Content-Type": "application/json"
    }

    payload = {
    "api_key": API_KEY,
    "date_from": date_from,  
    "date_to": date_to,     
    "limit": 500
    }
    response = requests.post(API_URL_get_trans, json=payload, headers=headers, auth=HTTPBasicAuth(API_CLIENT, API_SECRET))
    
    #print(f"Status code: {response.status_code}")
    #print(f"Response content: {response.text}")

    if response.status_code == 200:
        try:
            data = response.json()
            transactions = data.get('data', [])
            print(f"Anzahl der zurückgegebenen Transaktionen: {data.get('rows', 0)}")
            return transactions
        except requests.exceptions.JSONDecodeError:
            print("Die Antwort enthielt keine gültigen JSON-Daten.")
            return []
    else:
        print(f"Fehler beim Abrufen der Transaktionen: {response.status_code} - {response.text}")
        return []

# Find a transaction given the Verwendungszweck == Go-Cardless Verwendungszweck
def find_transaction_by_purpose(transactions, search_purpose):
    for transaction in transactions:
        if search_purpose in transaction['purpose']:
            #print(f"Gefundene Transaktion mit Verwendungszweck '{search_purpose}':")
            #print(f"ID by Customer: {transaction['id_by_customer']}")
            return transaction['id_by_customer']
    #print(f"Keine Transaktion mit dem Verwendungszweck '{search_purpose}' gefunden.")
    return None

# Function to book the amount and the fees
def create_transaction_posting(transaction_id, total_amount, deducted_fees):
    payload = {
        "api_key": API_KEY,
        "transaction_id_by_customer": transaction_id,
        "amounts": [f"{total_amount:.2f}", f"{-deducted_fees:.2f}"],
        "postingaccounts": ["64200", "68550"],
        "postingtexts": [
            f"Mitgliedsbeitrag für Transaktion {transaction_id}",
            f"Bankgebühren für Transaktion {transaction_id}"
        ],
        "vats": ["0_none", "0_none"],
        "cost_locations": ["1", "1"],
        "cost_locations_two": ["ETC", "ETC"]
    }
    
    headers = {
        "Content-Type": "application/json"
    }
    
    response = requests.post(API_URL_book, json=payload, headers=headers, auth=HTTPBasicAuth(API_CLIENT, API_SECRET))
    
    print(f"Status code: {response.status_code}")
    print(f"Response content: {response.text}")
    
    if response.status_code == 200:
        print(f"Buchung erfolgreich für Transaktion {transaction_id}.")
    else:
        print(f"Fehler bei der Buchung: {response.status_code} - {response.text}")

transactions = get_transactions(date_from, date_to)

# Finally book everything in the dataframe
for index, row in df_payouts.iterrows():
    search_purpose = row['reference']  
    amount = float(row['amount']) 
    deducted_fees = float(row['deducted_fees']) 
    total_amount = round(amount + deducted_fees, 2)  

    # Find transaction
    transaction_id = find_transaction_by_purpose(transactions, search_purpose)
    
    # Only book if transaction exists
    if transaction_id:
        create_transaction_posting(transaction_id, total_amount, deducted_fees)
    else:
        print(f"Keine Buchung erstellt, da keine passende Transaktion für '{search_purpose}' gefunden wurde.")
