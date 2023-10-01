import csv
import random
from datetime import datetime, timedelta

# Set the start date and end date
start_date = datetime(2023, 1, 1)  # January 1, 2023
end_date = datetime(2023, 12, 31)  # December 31, 2023

# Define the days of the week you want (Thursday, Friday, Saturday)
days_of_week = [3, 4, 5]  # 3 represents Thursday, 4 represents Friday, 5 represents Saturday

# Set the working hours
start_hour = 19  # 7 PM
end_hour = 24   # Midnight

# Define the maximum number of orders per day
max_orders_per_day = 80

# Create a list to store orders
orders = []

# Generate orders for each day
current_date = start_date
while current_date <= end_date:
    if current_date.weekday() in days_of_week:
        order_count = random.randint(1, max_orders_per_day)
        order_times = []
        for _ in range(order_count):
            hour = random.randint(start_hour, end_hour - 1)  # Adjust end_hour to exclude midnight
            minute = random.randint(0, 59)
            order_times.append(current_date.replace(hour=hour, minute=minute))
        
        # Sort the order times
        order_times.sort()
        
        # Calculate the intervals between orders
        for i in range(1, len(order_times)):
            interval = (order_times[i] - order_times[i - 1]).total_seconds() / 60
            orders.append([order_times[i], interval])

    # Move to the next day
    current_date += timedelta(days=1)

# Sort the orders by date and hour
orders.sort(key=lambda x: (x[0], x[0].hour, x[0].minute))

# Create a CSV file and write the headers
with open('pizza_orders.csv', 'w', newline='') as csv_file:
    csv_writer = csv.writer(csv_file)
    csv_writer.writerow(['Date', 'Hour', 'Interval (minutes)'])

    # Write the ordered orders to the CSV file
    for order in orders:
        order_time = order[0]
        interval_minutes = order[1]
        csv_writer.writerow([order_time.strftime('%Y-%m-%d'), order_time.strftime('%H:%M'), interval_minutes])

print("CSV file 'pizza_orders.csv' has been generated and sorted by date and hour with correct intervals.")
