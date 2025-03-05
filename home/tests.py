import string
from time import sleep
import unicodedata
from django.test import TestCase
import requests
import random
import json
import copy
import os
import subprocess
import signal
import time
from datetime import datetime
import threading
import coverage
from home.apps import HomeConfig
# Make sure openpyxl is installed: pip install openpyxl
from openpyxl import Workbook, load_workbook

cov = coverage.Coverage()
cov.start()

def start_server(p):
    if p is not None:
        os.kill(p.pid, signal.CTRL_C_EVENT)  # FOR WINDOWS
    command = ["python3", "manage.py", "runserver"]
    try:
        with open("server_output.txt", "a") as out_file, open("server_error.txt", "a") as err_file:
            p = subprocess.Popen(command,
                                 shell=True,  # windows
                                 creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,  # windows
                                 stdout=out_file, 
                                 stderr=err_file)
        print("Server started")
        sleep(1)
        return p
    except Exception as e:
        print(f"Error starting server: {e}")

class FuzzingTestCase(TestCase):
    def setUp(self):
        self.app_name = HomeConfig.name
        self.base_url = 'http://127.0.0.1:8000/datatb/product/'
        self.endpoint_url = 'add/'
        self.url = self.base_url + self.endpoint_url

        self.seedQ = []
        self.failureQ = []
        self.num_iterations = 20
        self.interesting = []
        self.testcases = 0
        self.coverage_before = None
        self.headers = {
            'Cookie': 'csrftoken=jr6DahhKuGKgXX6Dxb3F4iR9FgL; sessionid=bvlvh8bqcwhbzr2eqqk3b',  # Optional
        }
        self.testCheckCov = []

    # def test_fuzzing_request(self):
    #     signal.signal(signal.SIGINT, self.signal_handler)
    #     # Start server
    #     p = start_server(None)
    #     # Populate seedQ from file (seeds should include "name", "info", "price")
    #     with open("seed.json", "r") as f:
    #         self.seedQ = json.load(f)
        
    #     # Start a thread to print interesting vs time to the terminal
    #     stop_event = threading.Event()  # Signal to stop the thread
    #     printer_thread = threading.Thread(target=self.print_interesting_vs_time, args=(self.interesting, stop_event))
        
    #     # Run for a fixed duration (e.g., 300 seconds)
    #     timeout_seconds = 300
    #     start_time = time.time()
    #     printer_thread.start()
    #     while time.time() - start_time < timeout_seconds:
    #         seed = self.choose_next()
    #         energy = self.assign_energy(seed)  # Fixed energy value
    #         get_post_probability = 0.5
    #         for j in range(energy):
    #             mutated_seed = self.mutate_input(seed)
    #             # Build the request JSON using only the required keys
    #             request_json = copy.deepcopy(mutated_seed)
    #             for key in list(request_json.keys()):
    #                 if key not in ("name", "info", "price"):
    #                     del request_json[key]
    #             try:
    #                 print("Requesting...")
    #                 self.testcases += 1
    #                 self.print_interesting_vs_testcases()  # Print testcases info to terminal
    #                 if random.random() < get_post_probability:
    #                     output = requests.post(self.url, headers=self.headers, json=request_json, timeout=2)
    #                     if self.reveals_bug(mutated_seed, output):
    #                         self.failureQ.append({
    #                             "seed": mutated_seed,
    #                             "request": "POST",
    #                             "response": output.text
    #                         })
    #                     elif self.is_interesting():
    #                         cov.start()
    #                         self.seedQ.append(mutated_seed)
    #                         self.interesting.append(mutated_seed)
    #                 else:
    #                     output = requests.get(self.url, params=request_json, timeout=2)
    #                     if self.reveals_bug(mutated_seed, output):
    #                         self.failureQ.append({
    #                             "seed": mutated_seed,
    #                             "request": "GET",
    #                             "response": output.text
    #                         })
    #                     elif self.is_interesting():
    #                         cov.start()
    #                         self.seedQ.append(mutated_seed)
    #                         self.interesting.append(mutated_seed)
    #             except requests.exceptions.RequestException as e:
    #                 self.failureQ.append({
    #                     "seed": mutated_seed,
    #                     "request": output.request.method if hasattr(output, "request") else "UNKNOWN",
    #                     "response": f"Request failed: {e}"
    #                 })
    #                 start_server(p)
    #     stop_event.set()
    #     printer_thread.join()
    #     print(self.testCheckCov)
    #     cov.stop()
    #     cov.save()
    #     cov.report()
        
    #     # Write the updated seed and failure queues to file
    #     with open("seed.json", "w") as f:
    #         json.dump(self.seedQ, f)
    #     with open("failure.json", "w") as f:
    #         json.dump(self.failureQ, f)
    def test_fuzzing_request(self):
        signal.signal(signal.SIGINT, self.signal_handler)
        # Start server
        p = start_server(None)
        # Populate seedQ from file (seeds should include "name", "info", "price")
        with open("seed.json", "r") as f:
            self.seedQ = json.load(f)
        
        # Start a thread to print interesting vs time to the terminal
        stop_event = threading.Event()  # Signal to stop the thread
        printer_thread = threading.Thread(target=self.print_interesting_vs_time, args=(self.interesting, stop_event))
        
        # Run for a fixed duration (e.g., 300 seconds)
        timeout_seconds = 300
        start_time = time.time()
        printer_thread.start()
        while time.time() - start_time < timeout_seconds:
            seed = self.choose_next()
            energy = self.assign_energy(seed)  # Fixed energy value
            get_post_probability = 0.5
            for j in range(energy):
                mutated_seed = self.mutate_input(seed)
                # Build the request JSON using only the required keys
                request_json = copy.deepcopy(mutated_seed)
                for key in list(request_json.keys()):
                    if key not in ("name", "info", "price"):
                        del request_json[key]
                try:
                    print("Requesting...")
                    self.testcases += 1
                    self.print_interesting_vs_testcases()  # Print testcases info to terminal
                    if random.random() < get_post_probability:
                        output = requests.post(self.url, headers=self.headers, json=request_json, timeout=2)
                        if self.reveals_bug(mutated_seed, output):
                            self.failureQ.append({
                                "seed": mutated_seed,
                                "request": "POST",
                                "response": output.text
                            })
                        elif self.is_interesting():
                            cov.start()
                            self.seedQ.append(mutated_seed)
                            self.interesting.append(mutated_seed)
                    else:
                        output = requests.get(self.url, params=request_json, timeout=2)
                        if self.reveals_bug(mutated_seed, output):
                            self.failureQ.append({
                                "seed": mutated_seed,
                                "request": "GET",
                                "response": output.text
                            })
                        elif self.is_interesting():
                            cov.start()
                            self.seedQ.append(mutated_seed)
                            self.interesting.append(mutated_seed)
                except requests.exceptions.RequestException as e:
                    self.failureQ.append({
                        "seed": mutated_seed,
                        "request": "UNKNOWN",
                        "response": f"Request failed: {e}"
                    })
                    start_server(p)
            
            # Print the current seed queue
            print("Current seed queue:", self.seedQ)
            
            # Write interesting inputs to an Excel file
            self.write_interesting_to_excel(self.interesting, "interesting_inputs.xlsx")
        
        stop_event.set()
        printer_thread.join()
        print(self.testCheckCov)
        cov.stop()
        cov.save()
        cov.report()
        
        # Write the updated seed and failure queues to file
        with open("seed.json", "w") as f:
            json.dump(self.seedQ, f)
        with open("failure.json", "w") as f:
            json.dump(self.failureQ, f)
    def mutate_input(self, input_data):
        print(f"Input data: {input_data}")
        mutations = ("bitflip", "byteflip", "arith inc/dec", "interesting values", "random bytes", "delete bytes", "insert bytes", "overwrite bytes", "cross over")
        mutation_chose = random.choice(mutations)
        mutated_data = {}
        for key, value in input_data.items():
            if key in ("name", "info", "price"):
                mutated_data[key] = self.apply_mutation(value, mutation_chose, key)
        print(f"Mutated data: {mutated_data}")
        return mutated_data

    def apply_mutation(self, data, mutation, key):
        if not isinstance(data, str):
            data = str(data)
        if data == "" or data is None:
            data = self.random_string(key)
        mutated_input = bytearray()
        mutated_input.extend(data.encode("ascii"))
        match mutation:
            case "bitflip":
                n = random.choice((1, 2, 4))
                for i in range(0, len(mutated_input)*8):
                    byte_index = i // 8
                    bit_index = i % 8
                    for _ in range(n):
                        if i < len(mutated_input)*8:
                            mutated_input[byte_index] ^= (1 << bit_index)
            case "byteflip":
                n = random.choice((1, 2, 4))
                for i in range(len(mutated_input)):
                    for j in range(n):
                        if (i+j) < len(mutated_input):
                            mutated_input[i+j] ^= 0xFF
            case "arith inc/dec":
                n = random.choice((1, 2, 4))
                operator = random.choice((1, -1))
                for i in range(len(mutated_input)):
                    for j in range(n):
                        if (i+j) < len(mutated_input):
                            mutated_input[i+j] = (mutated_input[i+j] + operator) % 256
            case "interesting values":
                interesting_values = (0x5c, 0x00, 0xFF, 0x7F, 0x80, 0x01, 0x7E, 0x7D, 0x7C, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D, 0x0E, 0x0F)
                n = random.choice((1, 2, 4))
                for i in range(len(mutated_input)):
                    for j in range(n):
                        if (i+j) < len(mutated_input):
                            mutated_input[i+j] = random.choice(interesting_values)
            case "random bytes":
                byte_index = random.randint(0, len(mutated_input) - 1)
                mutated_input[byte_index] = random.randint(0, 255)
            case "delete bytes":
                size = random.randint(1, 4)
                start = random.randint(0, len(mutated_input))
                del mutated_input[start:start+size]
            case "insert bytes":
                size = random.randint(1, 4)
                start = random.randint(0, len(mutated_input))
                mutated_input[start:start] = bytearray(random.choices(range(256), k=size))
            case "overwrite bytes":
                size = random.randint(1, 4)
                start = random.randint(0, len(mutated_input))
                mutated_input[start:start+size] = bytearray(random.choices(range(256), k=size))
            case "cross over":
                data2 = random.choice(self.seedQ)
                other_data = bytearray()
                # other_data.extend(data2[key].encode("ascii"))
                other_data.extend(str(data2[key]).encode("ascii"))

                if len(other_data) < len(mutated_input):
                    splice_loc = random.randint(0, len(other_data))
                else:
                    splice_loc = random.randint(0, len(mutated_input))
                mutated_input[splice_loc:] = other_data[splice_loc:]
        mutated_input = unicodedata.normalize("NFKD", bytes(mutated_input).decode("ascii", errors="ignore"))
        if mutated_input == "" or mutated_input is None:
            mutated_input = self.random_string(key)
        return mutated_input

    def random_string(self, key):
        if key == "name":
            data = ''.join(random.choice(string.printable) for i in range(128))
        elif key == "info":
            data = ''.join(random.choice(string.printable) for i in range(1500))
        elif key == "price":
            data = str(random.randint(0, 1000))
        return data

    def choose_next(self):
        if self.seedQ:
            return random.choice(self.seedQ)
        raise Exception("Seed queue is empty!")
    
    def assign_energy(self, seed):
        return 5
    
    def reveals_bug(self, seed, output):
        if output.status_code == 200:
            print("\033[92mRequest successful!\033[0m")
            print("Request: ", seed)
            print("-" * 60)
            return False
        else:
            print(f"\033[91mRequest failed: Status code {output.status_code}\033[0m")
            print("Seed: ", seed)
            print("Response: ", output.text)
            print("-" * 60)
            return True

    def is_interesting(self):
        cov.stop()
        cov.save()
        if self.coverage_before is None:
            self.coverage_before = 0
            return True

        coverage_after = cov.json_report(pretty_print=True)
        if coverage_after > self.coverage_before:
            self.testCheckCov.append(f"Coverage increased from {self.coverage_before} to {coverage_after}")
            self.coverage_before = coverage_after
            return True
        return False
    
    def signal_handler(self, sig, frame):
        print("Exiting...")
        exit(0)

    def print_interesting_vs_time(self, list_data, stop_event):
        # Print header once
        header = (
            "Timestamp".ljust(25)
            + "No. of interesting".ljust(20)
            + "Recent Interesting Inputs"
        )
        print(header)
        while not stop_event.is_set():
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            count = len(list_data)
            # Show only the last three interesting inputs for brevity
            recent_interesting = list_data[-3:]
            recent_interesting_str = ", ".join(json.dumps(inp) for inp in recent_interesting)
            line = timestamp.ljust(25) + str(count).ljust(20) + recent_interesting_str
            print(line)
            time.sleep(1)

    def print_interesting_vs_testcases(self):
        # Print current testcase count and number of interesting cases
        print(f"Testcases: {self.testcases}, Interesting: {len(self.interesting)}")

    def write_interesting_to_excel(self, interesting_list, filename):
        """Append the interesting inputs to an Excel file if it exists, or create a new one."""
        
        # Check if the file exists
        if os.path.exists(filename):
            wb = load_workbook(filename)
            # Check if the sheet "Interesting Inputs" exists, else use active sheet
            if "Interesting Inputs" in wb.sheetnames:
                ws = wb["Interesting Inputs"]
            else:
                ws = wb.active
                ws.title = "Interesting Inputs"
        else:
            wb = Workbook()
            ws = wb.active
            ws.title = "Interesting Inputs"
            # Write header row if creating new file
            ws.append(["Name", "Info", "Price"])
        
        # Append interesting inputs
        for inp in interesting_list:
            name = inp.get("name", "")
            info = inp.get("info", "")
            price = inp.get("price", "")
            ws.append([name, info, price])
        
        wb.save(filename)
        print(f"Written {len(interesting_list)} interesting inputs to {filename}")
