CREATE TABLE IF NOT EXISTS user_settings (
  post_id SERIAL PRIMARY KEY,
  username VARCHAR(50) NOT NULL,
  post_date TIMESTAMP,
  msg VARCHAR(1000),
  lat FLOAT,
  long FLOAT
  

);