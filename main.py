import tkinter as tk
from tkinter import ttk, messagebox
import os
import shutil
import mysql.connector

DB_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "user": os.getenv("DB_USER", "root"),
    "password": os.getenv("DB_PASSWORD", ""),
    "database": os.getenv("DB_NAME", "disk_prediction")
}

BG, NAVY, BLUE, WHITE = "#f3f6fb", "#172554", "#2563eb", "#ffffff"
TEXT, MUTED, GREEN, ORANGE = "#172033", "#64748b", "#15803d", "#c2410c"
BORDER = "#e2e8f0"


def connect_db():
    return mysql.connector.connect(**DB_CONFIG)


def available_drives():
    return [f"{letter}:\\" for letter in "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
            if os.path.exists(f"{letter}:\\")]


def disk_info(drive):
    try:
        disk = shutil.disk_usage(drive)
        total, used, free = [value / 1024**3
                             for value in (disk.total, disk.used, disk.free)]
        percent = disk.used / disk.total * 100 if disk.total else 0
        return total, used, free, percent
    except OSError as error:
        messagebox.showerror("Disk Error", f"Could not read {drive}\n\n{error}")


def save_record(drive, values):
    connection = cursor = None
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("""
            INSERT INTO disk_usage
                (drive_name, total_gb, used_gb, free_gb, usage_percent)
            VALUES (%s, %s, %s, %s, %s)
        """, (drive, *values))
        connection.commit()
        return True
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error",
            f"Could not save the disk record.\n\n{error}\n\n"
            "Check that MySQL is running and the database/table and password are correct.")
        return False
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def monitor_disk():
    drive = drive_box.get()
    if not drive:
        messagebox.showwarning("Select Drive", "Please select a drive first.")
        return

    values = disk_info(drive)
    if values is None:
        return

    total, used, free, percent = values

    total_label.config(text=f"Total Space: {total:.2f} GB")
    used_label.config(text=f"Used Space: {used:.2f} GB")
    free_label.config(text=f"Free Space: {free:.2f} GB")
    usage_label.config(text=f"Disk Usage: {percent:.2f}%")

    progress_bar["value"] = percent
    progress_caption.config(
        text=f"{percent:.1f}% of total capacity is currently used",
        fg="#b91c1c" if percent >= 90 else ORANGE if percent >= 75 else GREEN
    )

    if save_record(drive, values):
        status_label.config(text=f"Saved {drive} measurement to MySQL.")
    else:
        status_label.config(text="Measurement displayed; database save failed.")

    if percent >= 90:
        messagebox.showwarning("Low Storage Alert",
            f"Drive {drive} is using {percent:.1f}% of its capacity.\n"
            f"Free space: {free:.2f} GB")
    elif percent >= 75:
        status_label.config(text=f"Notice: {drive} storage usage is high ({percent:.1f}%).")


def predict_storage():
    drive = drive_box.get()
    if not drive:
        messagebox.showwarning("Select Drive", "Please select a drive first.")
        return

    connection = cursor = None
    try:
        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT used_gb, recorded_at, id FROM disk_usage
            WHERE drive_name = %s
            ORDER BY recorded_at DESC, id DESC LIMIT 2
        """, (drive,))
        records = cursor.fetchall()

        if len(records) < 2:
            messagebox.showinfo("Not Enough Data",
                "At least two saved measurements are needed.\n\n"
                "Click Monitor Disk now, then click it again later to collect another measurement.")
            return

        latest, previous = records
        elapsed = (latest[1] - previous[1]).total_seconds() / 86400
        if elapsed <= 0:
            messagebox.showinfo("Not Enough Time Between Records",
                "The latest two records have no positive time gap.\n"
                "Wait a little while and monitor the drive again.")
            return

        daily_change = (float(latest[0]) - float(previous[0])) / elapsed
        info = disk_info(drive)
        if info is None:
            return
        total, used, free, percent = info

        if daily_change <= 0:
            messagebox.showinfo("Prediction Result",
                "The latest two records do not show increasing disk usage.\n\n"
                "A time-until-full estimate cannot be calculated. Collect more measurements over several days.")
            return

        messagebox.showinfo("Storage Prediction",
            f"Drive: {drive}\nCurrent free space: {free:.2f} GB\n"
            f"Estimated increase: {daily_change:.3f} GB/day\n"
            f"Estimated time until full: {free / daily_change:.1f} days\n\n"
            "This is a simple estimate based on the latest two records, not a guarantee.")
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Could not read prediction data.\n\n{error}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def view_history():
    connection = cursor = None
    try:
        connection = connect_db()
        cursor = connection.cursor()
        drive = drive_box.get()
        query = """
            SELECT drive_name, total_gb, used_gb, free_gb, usage_percent, recorded_at
            FROM disk_usage
        """
        if drive:
            query += " WHERE drive_name = %s"
            cursor.execute(query + " ORDER BY recorded_at DESC, id DESC LIMIT 100", (drive,))
        else:
            cursor.execute(query + " ORDER BY recorded_at DESC, id DESC LIMIT 100")

        records = cursor.fetchall()
        window = tk.Toplevel(root)
        window.title("Storage History")
        window.geometry("1000x420")
        columns = ("Drive", "Total GB", "Used GB", "Free GB", "Usage %", "Recorded At")
        table = ttk.Treeview(window, columns=columns, show="headings")
        for column, width in zip(columns, (90, 110, 110, 110, 100, 250)):
            table.heading(column, text=column)
            table.column(column, width=width, anchor="center")

        for record in records:
            row = list(record)
            for index in range(1, 5):
                row[index] = f"{float(row[index]):.2f}"
            table.insert("", tk.END, values=row)

        scrollbar = ttk.Scrollbar(window, orient="vertical", command=table.yview)
        table.configure(yscrollcommand=scrollbar.set)
        table.pack(side="left", fill="both", expand=True, padx=(10, 0), pady=10)
        scrollbar.pack(side="right", fill="y", padx=(0, 10), pady=10)
        if not records:
            messagebox.showinfo("Storage History", "No saved records were found yet.")
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Could not load history.\n\n{error}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()

def show_storage_graph():
    drive = drive_box.get()
    if not drive:
        messagebox.showwarning("Select Drive", "Please select a drive first.")
        return

    connection = cursor = None
    try:
        import matplotlib
        matplotlib.rcParams["toolbar"] = "None"

        import matplotlib.pyplot as plt

        connection = connect_db()
        cursor = connection.cursor()
        cursor.execute("""
            SELECT recorded_at, used_gb, free_gb FROM disk_usage
            WHERE drive_name = %s ORDER BY recorded_at, id
        """, (drive,))
        records = cursor.fetchall()
        if len(records) < 2:
            messagebox.showinfo("Not Enough Data",
                "At least two saved measurements are needed to draw a useful graph.")
            return

        dates = [row[0].strftime("%Y-%m-%d %H:%M:%S") for row in records]
        plt.figure(figsize=(10, 5))
        plt.plot(dates, [float(row[1]) for row in records], marker="o", label="Used Space (GB)")
        plt.plot(dates, [float(row[2]) for row in records], marker="s", label="Free Space (GB)")
        plt.title(f"Storage Usage History - {drive}")
        plt.xlabel("Recorded Date and Time")
        plt.ylabel("Storage (GB)")
        plt.xticks(rotation=45, ha="right")
        plt.grid(True)
        plt.legend()
        plt.tight_layout()
        plt.show()
    except ImportError:
        messagebox.showerror("Missing Library",
            "Matplotlib is not installed.\n\nRun: py -m pip install matplotlib")
    except mysql.connector.Error as error:
        messagebox.showerror("Database Error", f"Could not create graph.\n\n{error}")
    finally:
        if cursor:
            cursor.close()
        if connection and connection.is_connected():
            connection.close()


def test_database():
    connection = None
    try:
        connection = connect_db()
        messagebox.showinfo("Database Test", "Connected to MySQL successfully.")
    except mysql.connector.Error as error:
        messagebox.showerror("Database Test Failed",
            f"{error}\n\nCheck MySQL is running and DB_CONFIG is correct.")
    finally:
        if connection and connection.is_connected():
            connection.close()


def button(parent, text, command, bg=BLUE, fg=WHITE):
    return tk.Button(parent, text=text, command=command, bg=bg, fg=fg,
        activebackground=bg, activeforeground=fg, relief="flat", bd=0,
        cursor="hand2", font=("Segoe UI", 9, "bold"), padx=15, pady=9)


def metric_card(parent, title, initial, accent):
    card = tk.Frame(parent, bg=WHITE, highlightbackground=BORDER, highlightthickness=1)
    card.pack(side="left", fill="both", expand=True, padx=(0, 12))
    tk.Frame(card, bg=accent, height=4).pack(fill="x")
    tk.Label(card, text=title, bg=WHITE, fg=MUTED,
             font=("Segoe UI", 9, "bold")).pack(anchor="w", padx=16, pady=(14, 6))
    value = tk.Label(card, text=initial, bg=WHITE, fg=TEXT,
                     font=("Segoe UI", 19, "bold"))
    value.pack(anchor="w", padx=16, pady=(0, 16))
    return value

root = tk.Tk()
root.title("Smart Disk Space Prediction")
root.geometry("900x600")
root.configure(bg="#f0f4f8")

# Title
tk.Label(
    root,
    text="SMART DISK SPACE MONITOR",
    font=("Arial", 20, "bold"),
    bg="#172554",
    fg="white",
    pady=20
).pack(fill="x")

# Drive Selection
frame = tk.Frame(root, bg="white", pady=15)
frame.pack(fill="x", padx=20, pady=15)

tk.Label(frame, text="Select Drive:", bg="white").pack(side="left", padx=10)

drive_box = ttk.Combobox(
    frame,
    values=available_drives(),
    state="readonly",
    width=15
)
drive_box.pack(side="left", padx=10)
if drive_box["values"]:
    drive_box.current(0)

# Buttons
tk.Button(frame, text="Monitor Disk", width=15,
          command=monitor_disk).pack(side="left", padx=5)
tk.Button(frame, text="History", width=10,
          command=view_history).pack(side="left", padx=5)
tk.Button(frame, text="Show Graph", width=12,
          command=show_storage_graph).pack(side="left", padx=5)
tk.Button(frame, text="Test MySQL", width=12,
          command=test_database).pack(side="left", padx=5)

# Storage Overview
tk.Label(
    root,
    text="STORAGE OVERVIEW",
    font=("Arial", 14, "bold"),
    bg="#f0f4f8"
).pack(anchor="w", padx=25, pady=10)

details = tk.Frame(root, bg="white", pady=20)
details.pack(fill="x", padx=20)

total_label = tk.Label(
    details, text="Total Space: -- GB",
    bg="white", font=("Arial", 12)
)
total_label.pack(pady=8)

used_label = tk.Label(
    details, text="Used Space: -- GB",
    bg="white", font=("Arial", 12)
)
used_label.pack(pady=8)

free_label = tk.Label(
    details, text="Free Space: -- GB",
    bg="white", font=("Arial", 12)
)
free_label.pack(pady=8)

usage_label = tk.Label(
    details, text="Disk Usage: -- %",
    bg="white", font=("Arial", 12)
)
usage_label.pack(pady=8)

# Progress Bar
progress_caption = tk.Label(
    root, text="No measurement collected yet",
    bg="#f0f4f8", fg="#64748b", font=("Arial", 10)
)
progress_caption.pack(pady=(5, 0))

progress_bar = ttk.Progressbar(
    root,
    length=500,
    maximum=100,
    mode="determinate"
)
progress_bar.pack(padx=20, pady=15, fill="x")

# Prediction
tk.Button(
    root,
    text="Predict Storage Usage",
    width=25,
    bg="#2563eb",
    fg="white",
    command=predict_storage
).pack(pady=15)

# Status
status_label = tk.Label(
    root,
    text="Ready - Select a drive",
    bg="#dbeafe",
    pady=10
)
status_label.pack(side="bottom", fill="x")

root.mainloop()
