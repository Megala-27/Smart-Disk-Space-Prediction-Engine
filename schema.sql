CREATE DATABASE IF NOT EXISTS disk_prediction;

USE disk_prediction;

CREATE TABLE IF NOT EXISTS disk_usage (
    id INT AUTO_INCREMENT PRIMARY KEY,
    drive_name VARCHAR(20) NOT NULL,
    total_gb DOUBLE NOT NULL,
    used_gb DOUBLE NOT NULL,
    free_gb DOUBLE NOT NULL,
    usage_percent DOUBLE NOT NULL,
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_disk_usage_drive_recorded
    ON disk_usage (drive_name, recorded_at);
