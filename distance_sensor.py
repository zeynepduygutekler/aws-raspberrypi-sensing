import RPi.GPIO as GPIO
import time
from datetime import datetime
import boto3
import botocore
import threading
from decimal import Decimal

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
		
PIN_TRIGGER = 23
PIN_ECHO = 24 
INTERVAL = 15 # Frequency represented in minute
	
GPIO.setup(PIN_TRIGGER, GPIO.OUT)
GPIO.setup(PIN_ECHO, GPIO.IN)

class AWSDb:
    def __init__(self, table_name='DistanceData'):
        self.table_name = table_name
        self.db = boto3.resource('dynamodb')
        self.table = self.db.Table(table_name)
        self.client = boto3.client('dynamodb')

    def put(self, distance):
        timestamp = int(time.time())
        dateandtime = datetime.fromtimestamp(timestamp).strftime('%Y-%m-%d %H:%M:%S')
        location = "Adrian_Office"
        data_entry = {"Timestamp": timestamp, "Date_Time": dateandtime, "Location": location, "Distance": distance, "Sensor_id": "AO_"+str(timestamp)}
        
        try:
            self.table.put_item(Item=data_entry)
        
        # When there is no internet 
        except botocore.exceptions.EndpointConnectionError: 
            time.sleep(30)

    def distance_detection(self):
        # Initializing the sensor by alternating between high and low values
        GPIO.output(PIN_TRIGGER, False) 
        time.sleep(2) 
        GPIO.output(PIN_TRIGGER, True)
        time.sleep(0.00001)
        GPIO.output(PIN_TRIGGER, False)
					
        pulse_start_time = time.time()
        timeout = pulse_start_time + 0.05
        while GPIO.input(PIN_ECHO) == 0 and pulse_start_time < timeout:
            pulse_start_time = time.time()
        if pulse_start_time > timeout:
            return None
					
        pulse_end_time = time.time()
        timeout = pulse_end_time + 0.05
        while GPIO.input(PIN_ECHO) == 1 and pulse_end_time < timeout:
            pulse_end_time = time.time()
        if pulse_end_time > timeout:
            return None
						
        pulse_duration = pulse_end_time - pulse_start_time
        distance = Decimal(str(round(pulse_duration * 17150, 2)))
        self.put(distance)
	

def main():
	# Schedule main function to be executed every 15 minutes
	threading.Timer(interval=60*INTERVAL, function=main).start() 
	
	# Initialise the database object
	obj = AWSDb()
	obj.distance_detection()
	
	
if __name__ == "__main__":	
	main()
	
