import yaml
import requests
import time
import signal
from collections import defaultdict
import os
class HealthChecker:
    def __init__(self, config_path):
        self.endpoints = self.load_config(config_path)
        self.domain_availability = defaultdict(lambda: {'total': 0, 'up': 0})

    def load_config(self, config_path):
        with open(config_path, 'r') as file:
            return yaml.safe_load(file)

    def send_request(self, endpoint):
        try:
            start_time = time.time()
            response = requests.request(
                method=endpoint.get('method', 'GET'),
                url=endpoint['url'],
                headers=endpoint.get('headers', {}),
                data=endpoint.get('body', '')
            )
            latency = int((time.time() - start_time) * 1000)
            return response.ok and 200 <= response.status_code < 300 and latency < 500
        except requests.RequestException:
            return False

    def run_health_check(self):
        try:
            while True:
                for endpoint in self.endpoints:
                    result = 'UP' if self.send_request(endpoint) else 'DOWN'
                    domain = endpoint['url'].split('//')[1].split('/')[0]
                    self.domain_availability[domain]['total'] += 1
                    self.domain_availability[domain]['up'] += 1 if result == 'UP' else 0
                    print(f"Endpoint {endpoint['name']} is {result}")

                self.log_availability()
                time.sleep(15)

        except KeyboardInterrupt:
            print("\nExiting the program.")
            self.log_availability()

    def log_availability(self):
        for domain, stats in self.domain_availability.items():
            availability_percentage = round((stats['up'] / stats['total']) * 100) if stats['total'] > 0 else 0
            print(f"{domain} has {availability_percentage}% availability percentage")


def signal_handler(sig, frame):
    print("\nReceived SIGINT. Exiting the program.")
    exit(0)


if __name__ == "__main__":
    signal.signal(signal.SIGINT, signal_handler)
    checker = HealthChecker('config.yaml')
    checker.run_health_check()
