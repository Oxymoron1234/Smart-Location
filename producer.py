import json
import logging
import random
import threading
from datetime import datetime, timezone
import time
import boto3
from botocore.exceptions import BotoCoreError, NoCredentialsError

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load configuration
with open('config.json') as config_file:
    config = json.load(config_file)


def send_to_kinesis(kinesis_client, stream_name, data):
    try:
        response = kinesis_client.put_record(
            StreamName=stream_name,
            Data=json.dumps(data),
            PartitionKey=data['device_id']
        )
        logging.info(f"Data sent to Kinesis Stream {stream_name}: {data}")
    except (BotoCoreError, NoCredentialsError) as e:
        logging.error(f'Failed to send data to Kinesis Stream {stream_name}: {e}')



def generate_temperature_data(device_id):
    return {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor_type": "temperature",
        "value": round(random.uniform(18.0, 25.0), 2),
        "unit": "Celsius"
    }


def generate_humidity_data(device_id):
    return {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor_type": "humidity",
        "value": round(random.uniform(30.0, 70.0), 2),
        "unit": "Percent"
    }


def generate_energy_data(device_id):
    return {
        "device_id": device_id,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "sensor_type": "energy",
        "value": round(random.uniform(0.5, 5.0), 2),
        "unit": "kWh"
    }


def data_generator(device):
    device_id = device['id']
    device_type = device['type']
    stream_name = device['stream']

    generators = {
        "temperature": generate_temperature_data,
        "humidity": generate_humidity_data,
        "energy": generate_energy_data
    }

    generator_func = generators[device_type]

    while True:
        try:
            data = generator_func(device_id)
            kinesis_client = boto3.client('kinesis')
            send_to_kinesis(kinesis_client, stream_name, data)
            time.sleep(config['interval'])
        except Exception as e:
            logging.error(f"Error generating data for device {device}: {e}")
            time.sleep(config['interval'])


def main():
    threads = []
    for device in config['devices']:
        thread = threading.Thread(target=data_generator, args=(device,))
        thread.start()
        threads.append(thread)

    for thread in threads:
        thread.join()


if __name__ == "__main__":
    main()