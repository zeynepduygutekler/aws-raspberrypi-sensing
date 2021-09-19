import RPi.GPIO as GPIO
import time
from datetime import datetime
import boto3
import botocore

GPIO.setmode(GPIO.BCM)
PIR_PIN = 7
GPIO.setup(PIR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)


class AWSDb:
    def __init__(self, table_name='MotionData'):
        self.table_name = table_name
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(table_name)
        self.client = boto3.client('dynamodb')

    def motion_detection(self, PIR_PIN):
        timestamp = int(time.time())
        dateandtime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        location = "Adrian_Office"
        data_entry = {"Timestamp": timestamp, "Date_Time": dateandtime, "Location": location, "Motion": 1, "Sensor_id": "AO_"+str(timestamp)}
        
        try:
            self.table.put_item(Item=data_entry)
        except botocore.exceptions.EndpointConnectionError:
            time.sleep(30)


if __name__ == "__main__":
	# Initialise the database object
	obj = AWSDb()
	GPIO.add_event_detect(PIR_PIN, GPIO.BOTH, callback=obj.motion_detection, bouncetime=10000)  # Frequency 10 sec

	# To make the run active
	try:
		while 1:
			time.sleep(1)
	except KeyboardInterrupt:
		GPIO.cleanup()
