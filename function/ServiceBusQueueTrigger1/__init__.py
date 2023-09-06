import logging
import azure.functions as func
import psycopg2
import os
from datetime import datetime
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail

def main(msg: func.ServiceBusMessage):

    notification_id = int(msg.get_body().decode('utf-8'))
    logging.info('Python ServiceBus queue trigger processed message: %s',notification_id)

    # TODO: Get connection to database
    conn = psycopg2.connect(
        dbname='techconfdb',
        user='udacity_admin@migrationpostgres',
        host='migrationpostgres.postgres.database.azure.com',
        password='Az902200923ad'
        )
    cursor = conn.cursor()

    try:
        # TODO: Get notification message and subject from database using the notification_id

        cursor.execute("SELECT message, subject FROM notification WHERE id = %s", (notification_id))
        notification = cursor.fetchone()
        notification_message, notification_subject = notification[0:2]

        
        # TODO: Get attendees email and name
        cursor.execute("SELECT first_name, last_name, email FROM attendee;")
        attendees = cursor.fetchall()
        # TODO: Loop through each attendee and send an email with a personalized subject
        for first_name, last_name, email in attendees:
            subject = "Hey " + first_name + " " + last_name + "! " + notification_subject
            mail = Mail(
                from_email="info@dennisfrankenbach.me",
                to_emails=email,
                subject=subject,
                plain_text_content=notification_message
                )
            #sg = SendGridAPIClient(os.getenv("SENDGRID_API_KEY"))
            #response = sg.send(mail)
    
        # TODO: Update the notification table by setting the completed date and updating the status with the total number of attendees notified
        cursor.execute(
            "UPDATE notification SET completed_date=%s, status=%s WHERE id=%s;",
            (datetime.utcnow(), 'Notified {} attendees'.format(len(attendees)), notification_id))
        conn.commit()
        cursor.close()
    
    except (Exception, psycopg2.DatabaseError) as error:
        logging.error(error)
    finally:
        # TODO: Close connection
        conn.close()


if __name__ == "__main__":
    main("a")