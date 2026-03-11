# This program is read the csv file data to dump this data into sql database. step-2
import pyodbc
import csv
from datetime import datetime
import schedule
import time


def main():
    # Database config
    server = 'tcp:192.168.100.11'
    database = 'BuyFromDB'
    username = 'hyd_scrape'
    password = 'hyd$cr@93#@@@'
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

    # Connect to the database
    conn = pyodbc.connect(connection_string)
    cursor = conn.cursor()

    # Read data from CSV file
    csv_file_path = r'C:\Users\Test\Documents\thatsmystuff\rpa-scraping\ContarMarketScraping\Test1.csv'
    with open(csv_file_path, 'r') as file:
        reader = csv.DictReader(file)
        data = [row for row in reader]
        # print("data:::::::",data)

    # Insert data into the database
    for row in data:
        # print(row)
        scraped_date = None
        if row['ScrapedDate'] and row['ScrapedDate'] != '0':
            try:
                d1 = datetime.strptime(row['ScrapedDate'], '%m/%d/%Y').date()
                scraped_date = d1.strftime("%m/%d/%Y")
            except Exception as e:
                print(e)

            cursor.execute(
                "INSERT INTO Tbl_ContarmarketMainScrap (SKU, Title, QntyText, Quantity, StatusText, Status, UPC, Price, MPrice, AsinPack, ScrapedDate) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)",
                (row['Asin'], row['Title'], row['Qntytext'], row['Qnty'], row['statustext'], row['status'], row['UPC'], row['price'], row['mprice'], row['unit_box'], scraped_date))

    # Commit and close the connection
    conn.commit()
    conn.close()
    print("compleated")

# This is without cron!
# main()


def job():
    main()
# Schedule the job to run every day at 17:30
schedule.every().day.at("05:00").do(job)

# Run the scheduler continuously
while True:
    print("Task started successfully!!!!!!!!!!")
    schedule.run_pending()
    time.sleep(1800)


