import time
import schedule
import pyodbc
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


def sendEmail(sub):
    # Your email credentials
    sender_email = "nycrazecaptcha@gmail.com"
    receiver_email = "yedukondalu.bhyrisetti@engro.io"
    password = "tayk xina mqeh klfp"  # Use Gmail App Password here

    # Create the email message
    message = MIMEMultipart()
    message["From"] = sender_email
    message["To"] = receiver_email
    message["Subject"] = sub

    # Email body
    body = """\
    Hi Yedu,


    Member Price Tag is Changed


    B.Yedukondalu
    """

    # Attach the body to the message
    message.attach(MIMEText(body, "plain"))

    # Send the email using Gmail's SMTP server
    try:
        with smtplib.SMTP("smtp.gmail.com", 587) as server:
            server.starttls()  # Start TLS encryption
            server.login(sender_email, password)
            server.sendmail(sender_email, receiver_email, message.as_string())
            print("Email sent successfully! 💌")
    except Exception as e:
        print("Failed to send email. ❌")
        print(f"Error: {e}")


def main():
    # Database configuration
    server = 'tcp:192.168.100.11'
    database = 'BuyFromDB'
    username = 'hyd_scrape'
    password = 'hyd$cr@93#@@@'
    connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};UID={username};PWD={password}'


    try:
        connection = pyodbc.connect(connection_string)
        cursor = connection.cursor()

        # Execute the stored procedure
        cursor.execute(""" SELECT COUNT(*)
                            FROM Tbl_ContarmarketMainScrap
                            WHERE CAST(CreatedDate AS DATE) = CAST(GETDATE() AS DATE)
                            AND Title <> 'ProductNotFound'
                            AND MPrice = 0.00  """)

        rows = cursor.fetchall()[0][0]
        # print("rows:::", rows)
        if rows > 200:
            sendEmail("Member Price Tag is Changed. Once confirm it!!!!!!!")
        # Close the cursor and the connection
        cursor.close()
        connection.close()

        print("Scraping and data storage completed.", datetime.now())
    except:
        print("Connection failed.")
        sendEmail("Connection failed")


# main()

def job():
    main()
# Schedule the job to run every day at 17:30
schedule.every().day.at("06:30").do(job)

# Run the scheduler continuously
while True:
    print("Task started successfully!!!!!!!!!!")
    schedule.run_pending()
    time.sleep(1800)