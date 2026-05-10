CREATE EXTENSION IF NOT EXISTS timescaledb;

-- create a table for stores
CREATE TABLE stores (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,          
  base_url TEXT NOT NULL
);

-- create a table for products within that store
CREATE TABLE products (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  brand TEXT,
  unit TEXT,        
  store_id INTEGER REFERENCES stores(id)
);

-- create a table for the prices of each product
CREATE TABLE price_observations (
  id BIGSERIAL,
  product_id INTEGER REFERENCES products(id),
  price NUMERIC(10, 2) NOT NULL,
  in_stock BOOLEAN DEFAULT TRUE,
  observed_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- This is the TimescaleDB magic: turns price_observations into a hypertable
-- partitioned by time. Queries like "last 30 days" become dramatically faster.
SELECT create_hypertable('price_observations', 'observed_at');

-- Index for fast per-product lookups
CREATE INDEX ON price_observations (product_id, observed_at DESC);

-- Seed stores
INSERT INTO stores (name, base_url) VALUES
  ('walmart', 'https://www.walmart.com'),
  ('kroger',  'https://www.kroger.com'),
  ('aldi',    'https://www.aldi.us');

CREATE TABLE watchlist (
  id SERIAL PRIMARY KEY,
  user_email TEXT NOT NULL,
  product_id INTEGER REFERENCES products(id),
  target_price NUMERIC(10,2),
  created_at TIMESTAMPTZ DEFAULT NOW()
);