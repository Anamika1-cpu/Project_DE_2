import pandas as pd
import uuid
import random
from faker import Faker
from datetime import datetime, timedelta

fake = Faker()

records = []

for _ in range(1000):
    transaction_id = str(uuid.uuid4())

    # introduce duplicates (5%)
    if random.random() < 0.05:
        transaction_id = "DUPLICATE-ID"

    amount = round(random.uniform(-50, 500), 2)

    record = {
        "transaction_id": transaction_id,
        "customer_id": f"C{random.randint(10000,99999)}",
        "amount": amount,
        "timestamp": fake.date_time_this_year().isoformat(),
        "merchant": f"STORE_{random.randint(1,50)}"
    }

    records.append(record)

df = pd.DataFrame(records)
df.to_csv("transactions.csv", index=False)

print("Data Generated Successfully!")
