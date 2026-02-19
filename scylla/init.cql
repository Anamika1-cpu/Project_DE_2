CREATE KEYSPACE IF NOT EXISTS finance
WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

USE finance;

CREATE TABLE IF NOT EXISTS daily_customer_totals (
    customer_id text,
    transaction_date date,
    daily_total double,
    PRIMARY KEY (customer_id, transaction_date)
);
