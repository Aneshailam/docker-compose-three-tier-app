-- Runs automatically the first time the database volume is created.
-- The database and user come from the MYSQL_* variables in .env.
CREATE TABLE IF NOT EXISTS tasks (
  id         INT AUTO_INCREMENT PRIMARY KEY,
  title      VARCHAR(200) NOT NULL,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
