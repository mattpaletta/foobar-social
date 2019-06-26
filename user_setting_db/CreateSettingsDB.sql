CREATE TABLE user_settings (
  user_id SERIAL PRIMARY KEY,
  username VARCHAR(50) UNIQUE NOT NULL,
  passw VARCHAR(50) NOT NULL,
  phone_number VARCHAR(50),
  verification BOOLEAN,
  pirvate BOOLEAN

);