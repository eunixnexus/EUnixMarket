import redis
import json
import time
from random import randint, uniform

# Connect to Redis
redis_client = redis.StrictRedis(host='localhost', port=6379, db=0)

def send_to_redis(source_name, num_entries=10):
    for _ in range(num_entries):
        # Create random data
        data = {
            "Name": source_name,
            "ID": randint(1, 1000),
            "price": round(uniform(10, 100), 2),
            "qty": randint(1, 20),
            "value": round(uniform(100, 1000), 2),
        }
        # Convert to JSON and push to Redis
        redis_client.rpush("time_series_data", json.dumps(data))
        print(f"Sent data to Redis: {data}")
        time.sleep(1)  # Simulate data sending interval

if __name__ == "__main__":
    # Example: Send data from source1
    send_to_redis("source1")