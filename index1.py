# This program is scraping all the details from marketplace!!!!!!

import csv
import datetime
import re
import time

import pyodbc
import schedule
from playwright.sync_api import sync_playwright, TimeoutError

# -------------------- DB CONFIG -------------------- #
# Database configuration
server = 'tcp:192.168.100.11'
database = 'BuyFromDB'
username = 'hyd_scrape'
password = 'hyd$cr@93#@@@'

connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'

connection = pyodbc.connect(connection_string)
cursor = connection.cursor()

# -------------------- DB QUERY -------------------- #
# cursor.execute(""" SELECT
#                     SKU, Title AS ProductTitle, UPC AS Barcode, AsinPack AS Box,
#                     Price, MPrice MemberPrice, CreatedDate
#                 FROM Tbl_ContarmarketMainScrap
#                 WHERE AsinPack=0
#                 AND Title != 'ProductNotFound'""")


cursor.execute(""" SELECT SKU
                    FROM LinkedASL.Products.dbo.ContarMarketCatalogue_log 
                    WHERE CAST(CrDate AS DATE)='2026-02-04'
                    AND SKU NOT IN (
                                    SELECT
                                        DISTINCT bd.Asin AS SKU
                                    FROM LINKEDASL.OrdersDB.dbo.buyfromasindetailsdata bd
                                    JOIN LINKEDASL.OrdersDB.dbo.BuyFromMainAsin bm ON bm.id=bd.BuyFromMainID
                                    JOIN LINKEDASL.OrdersDB.dbo.MarketPlaceMaster mp ON mp.MarketPlaceID=bd.BuyFromId
                                    WHERE BuyFromId=379
                    )
                    ORDER BY SKU
                    OFFSET 0 ROWS FETCH NEXT 300 ROWS ONLY """)

rows = cursor.fetchall()
# print("rows:::::", rows)


def main():
    # -------------------- SCRAPING FUNCTION -------------------- #
    def scrape_product_data_selenium(asin):
        # print("\nOpening:", url)
        # page.goto(url, timeout=60000)
        # page.wait_for_load_state("domcontentloaded")
        try:
            page.wait_for_selector("#header-search")
            search_box = page.locator("#header-search")
            search_box.fill(asin)
            search_box.press("Enter")
            page.wait_for_load_state("networkidle")
            print("Search executed!")
        except:
            print("Search is not executed!")

        # Click first product image
        try:
            page.locator("img.card__main-image").first.click()
            print("Clicked product!")
        except:
            print("Image Tag Is Not Available!!!!!!")

        # -------- Product Title -------- #
        try:
            page.wait_for_selector(".product-title.h4", timeout=10000)
            title = page.locator(".product-title.h4").inner_text().strip()
        except TimeoutError:
            title = "ProductNotFound"
            return title, "", 0, "", 0, "", 0, 0, 0
        print("Product Title:", title)

        # -------- Product Price -------- #
        try:
            price_locator = page.locator("span.price__current").filter(has_text="$")
            price_text = price_locator.inner_text()
            price = price_text.replace("$", "").replace(",", "").strip()

        except Exception as e:
            print("Error occured:",e)
            price = 0.0
        print("Price:", price)

        # -------- Member price -------- #
        try:
            price_text = page.locator("span.MembersPrice").first.text_content(timeout=2000)
            match = re.search(r"\d+\.\d+", price_text)
            mprice = match.group()
        except:
            try:
                price_text = page.locator("span.cp-price-final").first.text_content(timeout=2000)
                match = re.search(r"\d+\.\d+", price_text)
                mprice = match.group()
            except Exception as e:
                print("Error occured", e)
                mprice = 0.0
        print("Member Price:", mprice)

        # -------- Product pack -------- #
        try:
            row = page.locator("div.info-row").filter(has_text="Unit Box:")
            unit_box = row.locator("div.value").inner_text().strip()
        except Exception as e:
            try:
                row = page.locator("div.info-row").filter(has_text="Units:")
                unit_box = row.locator("div.value").inner_text().strip()
            except:
                print("Error Occured", e)
                unit_box = 0
        print("Unit Box:", unit_box)

        # -------- Stock Status -------- #
        try:
            page.wait_for_selector("button[class='btn js-add-to-cart btn--primary w-full']", timeout=10000)
            statustext = page.locator("button[class='btn js-add-to-cart btn--primary w-full']").inner_text().strip()
            status = 1
            try:
                page.wait_for_selector("div[class='preorder-minimum'] p", timeout=10000)
                Qntytext = page.locator("div[class='preorder-minimum'] p").inner_text().strip()
                # extract number using regex
                if Qntytext:
                    match = re.search(r"\d+", Qntytext)
                    Qnty = match.group() if match else 99
            except TimeoutError:
                Qntytext = "QntyNotFound"
                Qnty = 99
        except TimeoutError:
            Qntytext = "QntyNotFound"
            Qnty = 0
            try:
                statustext = page.locator(".restock-rocket-button-cover").inner_text().strip()
                status = 0
            except:
                statustext = "Status Text NotFound"
                status = 0
        print("Status Text:", statustext)
        print("status:", status)

        # -------- BarCode -------- #
        try:
            page.wait_for_selector("div.info-row:has-text('UPC') div.value", timeout=10000)
            UPC = page.locator("div.info-row:has-text('UPC') div.value").inner_text().strip()
        except TimeoutError:
            UPC = "BarCodeNotFound"
        print("BarCode", UPC)

        return title, Qntytext, Qnty, statustext, status, UPC, price, mprice, unit_box



    # -------------------- MAIN EXECUTION -------------------- #
    try:
        # Open a CSV file for writing
        with open("Test1.csv", "w", newline="", encoding="utf-8") as csv_file:
            csv_writer = csv.writer(csv_file)
            current_date = datetime.date.today().strftime("%m/%d/%Y")

            # Write headers to the CSV file
            csv_writer.writerow(
                ["Asin", "Title", "Qntytext", "Qnty", "statustext", "status", "UPC", "price", "mprice", "unit_box", "ScrapedDate"])

            with sync_playwright() as p:
                browser = p.chromium.launch(headless=False)
                context = browser.new_context()
                page = context.new_page()

                page.goto("https://www.contarmarket.com", timeout=60000)
                page.wait_for_load_state("domcontentloaded")

                for row in rows:
                    Asin = row[0].strip()
                    # Scrape product data using Selenium Function!
                    Title, Qntytext, Qnty, statustext, status, UPC, price, mprice, unit_box  = scrape_product_data_selenium(Asin)
                    # Write data to CSV
                    csv_writer.writerow(
                        [Asin, Title, Qntytext, Qnty, statustext, status, UPC, price, mprice, unit_box, current_date])
                    csv_file.flush()

                browser.close()

    except Exception as e:
        print("Exception occurred:", e)


# main()

def job():
    main()
# Schedule the job to run every day at 17:30
schedule.every().day.at("01:00").do(job)

# Run the scheduler continuously
while True:
    print("Task started successfully!!!!!!!!!!")
    schedule.run_pending()
    time.sleep(1800)