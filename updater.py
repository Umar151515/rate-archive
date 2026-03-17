import json
import sqlite3
from http import client
from datetime import datetime, timedelta, timezone


API_CONFIGS = [
    {"host": "cdn.jsdelivr.net", "path": "/npm/@fawazahmed0/currency-api@{date}/v1/currencies/{currency}.min.json"},
    {"host": "{date}.currency-api.pages.dev", "path": "/v1/currencies/{currency}.min.json"}
]

def main():
    with open("currency_history.json") as file:
        currency_history = json.load(file)

    rates_history: dict[str, dict[str, float]] = currency_history["rates_history"]
    base_currency: str = currency_history["base_currency"].lower()

    latest_update_date = datetime.strptime(currency_history["latest_update"], "%Y-%m-%d")
    current_date = datetime.now()

    days_to_fetch = (current_date - latest_update_date).days

    if days_to_fetch < 1:
        return
    
    for i in range(days_to_fetch):
        date_str = (latest_update_date + timedelta(days=i)).strftime("%Y-%m-%d")

        for cfg in API_CONFIGS:
            try:
                host = cfg["host"].format(date=date_str)
                path = cfg["path"].format(date=date_str, currency=base_currency)
                
                conn = client.HTTPSConnection(host)
                conn.request("GET", path)
                response = conn.getresponse()
                
                if response.status == 200:
                    data = json.loads(response.read().decode())
                    rates_history[date_str] = data[base_currency]
                    break
            except:
                pass
            finally:
                conn.close()

    currency_history["latest_update"] = current_date.strftime("%Y-%m-%d")
    rates_history = dict(sorted(rates_history.items(), key=lambda x: datetime.strptime(x[0], "%Y-%m-%d")))
    
    with open("currency_history.json", "w") as file:
        json.dump(currency_history, file, indent=4)

    conn = sqlite3.connect("currency_history.db")
    cur = conn.cursor()

    cur.executescript("""
        DROP TABLE IF EXISTS rates;
        CREATE TABLE IF NOT EXISTS rates (
            date INTEGER NOT NULL,
            currency TEXT NOT NULL,
            rate REAL NOT NULL,
            PRIMARY KEY (date, currency)
        )
    """)
    cur.executescript("""
        DROP TABLE IF EXISTS info;
        CREATE TABLE IF NOT EXISTS info (
            base_currency TEXT NOT NULL,
            latest_update INTEGER NOT NULL
        )
    """
    )

    rates_history_list = [
        (int(datetime.strptime(date, "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp()), code, value) 
        for date, currencies in rates_history.items() 
        for code, value in currencies.items()
    ]
    cur.executemany("INSERT INTO rates VALUES (?, ?, ?)", rates_history_list)
    cur.execute("INSERT INTO info VALUES (?, ?)", (base_currency, int(datetime.strptime(currency_history["latest_update"], "%Y-%m-%d").replace(tzinfo=timezone.utc).timestamp())))

    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()