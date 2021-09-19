import RPi.GPIO as GPIO
import time
from datetime import datetime
import boto3

GPIO.setmode(GPIO.BCM)
pir_pin = 7
GPIO.setup(pir_pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


class AWSDb:
    def __init__(self, table_name='MotionData'):
        self.table_name = table_name
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(table_name)
        self.client = boto3.client('dynamodb')

    def motion_detection(self, pir_pin):
        timestamp = int(time.time())
        dateandtime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        location = "Adrian_Office"

        data_entry = {"Timestamp": timestamp, "Date_Time": dateandtime, "Location": location, "Motion": 1, "Sensor_id": "AO_"+str(timestamp)}
        self.table.put_item(Item=data_entry)


if __name__ == "__main__":

    # Initialise the database object
    obj = AWSDb()
    GPIO.add_event_detect(pir_pin, GPIO.BOTH, callback=obj.motion_detection, bouncetime=10000)  # Frequency 10 sec

    # To make the run active
    try:
        while 1:
            time.sleep(1)
    except KeyboardInterrupt:
        GPIO.cleanup()
