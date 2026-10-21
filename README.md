# Smart Disk Space Prediction Engine

## 1. Project Overview

The **Smart Disk Space Prediction Engine** is a Python-based desktop application designed to monitor disk storage usage, track historical storage data, and estimate the time remaining before a drive reaches its full capacity.

The application integrates Python, Tkinter, and MySQL to provide storage monitoring, historical data visualization, low-storage alerts, and basic storage prediction.

## 2. Project Objectives

* Monitor available disk drives and their storage usage.
* Display total, used, and free disk space.
* Store disk usage measurements in a MySQL database.
* Maintain historical storage records.
* Visualize disk usage trends through graphs.
* Estimate the time required for a drive to reach full capacity.
* Alert users when disk storage usage becomes high.

## 3. Key Features

* **Disk Monitoring:** Retrieves storage information for available drives.
* **Storage Overview:** Displays total, used, and free disk space.
* **Low Storage Alerts:** Warns users when disk usage reaches high levels.
* **MySQL Integration:** Stores disk usage measurements in a database.
* **Historical Tracking:** Displays previously recorded storage measurements.
* **Graphical Visualization:** Plots used and free storage over time.
* **Storage Prediction:** Estimates the time until a drive becomes full based on recent measurements.
* **Database Connection Test:** Checks whether the application can connect to MySQL.

## 4. Technologies Used

| Technology             | Purpose                           |
| ---------------------- | --------------------------------- |
| Python                 | Core application development      |
| Tkinter                | Graphical user interface          |
| MySQL                  | Storage measurement database      |
| MySQL Connector/Python | Database connectivity             |
| Matplotlib             | Storage usage graphs              |
| OS Module              | Identifying available drives      |
| Shutil Module          | Retrieving disk usage information |

## 5. System Requirements

* Windows operating system
* Python 3.x
* MySQL Server
* MySQL Connector/Python
* Matplotlib

## 6. Input

The application uses the following inputs.

### 6.1 Drive Selection

The user selects an available disk drive from the dropdown menu.

### 6.2 Disk Usage Information

The application retrieves:

* Total disk capacity
* Used disk space
* Available free space
* Percentage of disk space used

### 6.3 Historical Measurements

Previously recorded disk usage data is retrieved from MySQL to analyze storage trends and calculate predictions.

### 6.4 Database Configuration

The application requires the following MySQL connection settings:

* Database host
* Database username
* Database password
* Database name

## 7. Processing

The application processes the collected information through the following steps:

1. Detects available disk drives.
2. Retrieves total, used, and free storage information.
3. Calculates the percentage of disk space used.
4. Displays storage information in the graphical interface.
5. Saves measurements to the MySQL database.
6. Checks whether storage usage has reached a warning threshold.
7. Retrieves historical measurements when requested.
8. Generates graphs showing storage usage trends.
9. Estimates the time until the drive becomes full using the two most recent measurements.

### Storage Prediction Formula

**Daily Storage Increase:**

Daily Storage Increase = Change in Used Space / Elapsed Time in Days

**Estimated Time Until Full:**

Estimated Days Until Full = Current Free Space / Daily Storage Increase

The prediction is calculated only when the latest two measurements show increasing disk usage and have a positive time interval.

## 8. Output

### 8.1 Storage Overview

The application displays:

* Total Space
* Used Space
* Free Space
* Disk Usage Percentage

### 8.2 Low Storage Alerts

The application displays warnings when disk usage reaches high levels.

* **75% or above:** Displays a high-storage usage notice.
* **90% or above:** Displays a low-storage warning.

### 8.3 Storage History

The application displays historical records containing:

* Drive name
* Total storage
* Used storage
* Free storage
* Usage percentage
* Recorded date and time

### 8.4 Graphical Output

The application generates a graph showing changes in used and free disk space over recorded measurements.

### 8.5 Storage Prediction

The application estimates how many days remain before a drive becomes full, based on recent storage usage.

**Example Output:**

```text
Drive: C:\
Current free space: 50.00 GB
Estimated increase: 2.000 GB/day
Estimated time until full: 25.0 days
```

This is an illustrative example. Actual predictions depend on the drive's available space and recorded measurements.

## 9. Database Structure

**Database Name:** `disk_prediction`

### Table: `disk_usage`

| Column        | Description                      |
| ------------- | -------------------------------- |
| id            | Unique record identifier         |
| drive_name    | Name of the monitored drive      |
| total_gb      | Total storage capacity in GB     |
| used_gb       | Used storage in GB               |
| free_gb       | Available storage in GB          |
| usage_percent | Percentage of storage used       |
| recorded_at   | Date and time of the measurement |

The database stores historical measurements so the application can display storage history, generate graphs, and calculate basic predictions.

## 10. Installation and Execution

### Step 1: Clone the Repository

```bash
git clone https://github.com/YOUR_USERNAME/Smart-Disk-Space-Prediction-Engine.git
```

Replace `YOUR_USERNAME` with your GitHub username.

### Step 2: Navigate to the Project Folder

```bash
cd Smart-Disk-Space-Prediction-Engine
```

### Step 3: Create a Virtual Environment

```bash
python -m venv .venv
```

Activate it on Windows:

```bat
.venv\Scripts\activate
```

### Step 4: Install Dependencies

```bash
python -m pip install -r requirements.txt
```

### Step 5: Set Up the MySQL Database

Open MySQL Workbench and execute the SQL commands in `schema.sql`.

This creates the `disk_prediction` database and the `disk_usage` table.

### Step 6: Configure Database Credentials

Set your local MySQL connection details in Windows Command Prompt:

```bat
set DB_HOST=localhost
set DB_USER=root
set DB_PASSWORD=your_mysql_password
set DB_NAME=disk_prediction
```

Replace `your_mysql_password` with your actual local MySQL password.

Never upload your actual database password to GitHub.

### Step 7: Run the Application

```bash
python main.py
```

The graphical interface will open if the application starts successfully and its required dependencies are installed.

## 11. How to Use

1. Launch the application.
2. Select a drive from the dropdown menu.
3. Click **Monitor Disk** to retrieve storage information and save a measurement.
4. Click **History** to view previously recorded measurements.
5. Click **Show Graph** to visualize storage usage trends.
6. Click **Predict Storage Usage** to estimate the time remaining before the drive becomes full.
7. Click **Test MySQL** to test the database connection.

At least two saved measurements are required for graphing and prediction. Predictions also require a positive time interval between the latest two measurements.

## 12. Limitations

* The current implementation is designed for Windows drive monitoring.
* Storage prediction uses a simple calculation based on the two latest measurements.
* Predictions are estimates and are not guaranteed to reflect future storage usage.
* The application requires a working MySQL database connection to save and retrieve measurements.
* The application monitors storage usage but does not automatically delete files or free disk space.

## 13. Future Enhancements

* Automated scheduled disk monitoring.
* Email or desktop notifications for low storage.
* More advanced storage prediction algorithms.
* Improved historical analytics and dashboards.
* Exportable storage reports in CSV or PDF format.
* Support for monitoring multiple systems.

## 14. Conclusion

The Smart Disk Space Prediction Engine provides a simple approach to disk storage monitoring and basic capacity forecasting. By combining storage measurements, MySQL-based history tracking, graphical visualization, and prediction calculations, the application helps users understand storage consumption and anticipate potential disk space shortages.

## 15. License

This project can be distributed under the MIT License by including a `LICENSE` file in the repository.
