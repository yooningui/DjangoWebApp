# import os
# import signal
# import subprocess
# import logging
# from time import sleep
# from home.apps import HomeConfig
# import random
# import json
# from django.test import TestCase, Client , LiveServerTestCase
# import unicodedata
# import string
# import time
# import copy
# import requests
# import coverage
# import threading
# import matplotlib.pyplot as plt

# logging.basicConfig(
#     filename='app.log',  # Logs will be written to app.log in the current directory
#     level=logging.DEBUG,
#     format="%(asctime)s [%(levelname)s] %(message)s",
#     datefmt="%Y-%m-%d %H:%M:%S",
# )
# logger = logging.getLogger(__name__)

# cov = coverage.Coverage(source=['home'])
# cov.start()

# class FuzzingTestCase(TestCase):
#     @classmethod
#     def tearDownClass(cls):
#         cov.stop()
#         cov.save()
#         super(FuzzingTestCase, cls).tearDownClass()

#     def setUp(self):
#         super().setUp()
#         # Capture baseline covered lines
#         data = cov.get_data()
#         self._covered = set(
#             (fn, ln)
#             for fn in data.measured_files()
#             for ln in (data.lines(fn) or [])
#         )

#         self.client = Client()
#         self.url = '/datatb/product/add/'
#         self.seedQ = self._load_seeds('seed.json')

#         self.seedQ.extend([
#             {
#                 "seed": {"name": "((a+)+)+", "info": "((a+)+)+", "price": "0"},
#                 "s": 0,
#                 "f": 1,
#                 "alpha": 1,
#             },
#             {
#                 "seed": {"name": "OOM Test", "info": "A" * 10_000_000, "price": "100"},
#                 "s": 0,
#                 "f": 1,
#                 "alpha": 1,
#             },
#         ])

#     def _load_seeds(self, path):
#         try:
#             raw = json.load(open(path))
#         except Exception:
#             logger.error("Failed to load %s", path)
#             raw = []
#         return [
#             {"seed": s, "s": 0, "f": 1, "alpha": 20}
#             for s in raw
#         ]

#     def test_fuzz_requests(self):
#         start_time = time.time()
#         cumulative_interesting = 0

#         # lists to store (elapsed_time, cumulative_interesting)
#         times = []
#         counts = []

#         timeout = 300
#         end = start_time + timeout

#         while time.time() < end:
#             seed   = self.choose_next()
#             energy = self.assign_energy(seed)

#             for _ in range(energy):
#                 payload    = self._prepare_payload(seed["seed"])
#                 seed["f"] += 1

#                 resp = self.client.post(
#                     self.url,
#                     json.dumps(payload),
#                     content_type="application/json"
#                 )

#                 if self.reveals_bugs(seed, resp):
#                     self._save_crash(payload, resp.status_code, resp.content)

#                 if self._is_interesting():
#                     cumulative_interesting += 1
#                     self._queue_new_seed(payload)

#                     # record timestamp and count
#                     elapsed = time.time() - start_time
#                     times.append(elapsed)
#                     counts.append(cumulative_interesting)

#         # — after fuzzing, plot —
#         plt.figure()
#         plt.plot(times, counts, marker="o", linestyle="-")
#         plt.xlabel("Elapsed Time (seconds)")
#         plt.ylabel("Cumulative Interesting Inputs")
#         plt.title("Fuzzer: Interesting Discoveries Over Time")
#         plt.tight_layout()
#         plt.savefig("interesting_over_time.png")


        
#     def mutate_input(self,input_data):
#         mutations = (
#             "bitflip", "byteflip", "arith inc/dec", "interesting values",
#             "random bytes", "delete bytes", "insert bytes", "overwrite bytes", "cross over"
#         )
#         mutation_chose = random.choice(mutations)
#         mutated_data = {}
#         for key, value in input_data.items():
#             if key in ("name", "info", "price"):
#                 mutated_data[key] = self.apply_mutation(value, mutation_chose, key)
#         return mutated_data

#     def apply_mutation(self, data, mutation, key):
#         if not isinstance(data, str):
#             data = str(data)
#         if data == "" or data is None:
#             data = self.random_string(key)
#         mutated_input = bytearray()
#         mutated_input.extend(data.encode("ascii"))
#         match mutation:
#             case "bitflip":
#                 n = random.choice((1, 2, 4))
#                 for i in range(0, len(mutated_input) * 8):
#                     byte_index = i // 8
#                     bit_index = i % 8
#                     for _ in range(n):
#                         if i < len(mutated_input) * 8:
#                             mutated_input[byte_index] ^= (1 << bit_index)
#             case "byteflip":
#                 n = random.choice((1, 2, 4))
#                 for i in range(len(mutated_input)):
#                     for j in range(n):
#                         if (i + j) < len(mutated_input):
#                             mutated_input[i + j] ^= 0xFF
#             case "arith inc/dec":
#                 n = random.choice((1, 2, 4))
#                 operator = random.choice((1, -1))
#                 for i in range(len(mutated_input)):
#                     for j in range(n):
#                         if (i + j) < len(mutated_input):
#                             mutated_input[i + j] = (mutated_input[i + j] + operator) % 256
#             case "interesting values":
#                 interesting_values = (0x5c, 0x00, 0xFF, 0x7F, 0x80, 0x01, 0x7E, 0x7D, 0x7C,
#                                       0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A,
#                                       0x0B, 0x0C, 0x0D, 0x0E, 0x0F)
#                 n = random.choice((1, 2, 4))
#                 for i in range(len(mutated_input)):
#                     for j in range(n):
#                         if (i + j) < len(mutated_input):
#                             mutated_input[i + j] = random.choice(interesting_values)
#             case "random bytes":
#                 byte_index = random.randint(0, len(mutated_input) - 1)
#                 mutated_input[byte_index] = random.randint(0, 255)
#             case "delete bytes":
#                 size = random.randint(1, 4)
#                 start = random.randint(0, len(mutated_input))
#                 del mutated_input[start:start + size]
#             case "insert bytes":
#                 size = random.randint(1, 4)
#                 start = random.randint(0, len(mutated_input))
#                 mutated_input[start:start] = bytearray(random.choices(range(256), k=size))
#             case "overwrite bytes":
#                 size = random.randint(1, 4)
#                 start = random.randint(0, len(mutated_input))
#                 mutated_input[start:start + size] = bytearray(random.choices(range(256), k=size))
#             case "cross over":
#                 if self.seedQ:
#                     data2 = random.choice(self.seedQ)["seed"]
#                     other_data = bytearray()
#                     other_data.extend(str(data2.get(key, "")).encode("ascii"))
#                     if len(other_data) < len(mutated_input):
#                         splice_loc = random.randint(0, len(other_data))
#                     else:
#                         splice_loc = random.randint(0, len(mutated_input))
#                     mutated_input[splice_loc:] = other_data[splice_loc:]
#         try:
#             mutated_str = bytes(mutated_input).decode("ascii", errors="ignore")
#         except Exception as ex:
#             mutated_str = self.random_string(key)
#         mutated_str = unicodedata.normalize("NFKD", mutated_str)
#         if mutated_str == "" or mutated_str is None:
#             mutated_str = self.random_string(key)
#         return mutated_str
    
#     def random_string(self, key):
#         if key == "name":
#             data = ''.join(random.choice(string.printable) for i in range(128))
#         elif key == "info":
#             data = ''.join(random.choice(string.printable) for i in range(1500))
#         elif key == "price":
#             data = str(random.randint(0, 1000))
#         return data

#     def choose_next(self):
#         rec = min(self.seedQ, key=lambda r: (r["s"], r["f"]))
#         rec["s"] += 1
#         return rec

#     def assign_energy(self, seed):
#         MAX = 64
#         e = (seed["alpha"] * (2 ** seed["s"])) / seed["f"]
#         return max(1, min(MAX, int(e)))
    
#     def reveals_bugs(self, seed, output):
#         if output.status_code == 200:
#             return False
#         else:
#             logger.error("Bug revealed!")
#             logger.error("Request failed: Status code %s", output.status_code)
#             logger.error("Seed: %s", seed)
#             return True

#     def _is_interesting(self):
#         data = cov.get_data()
        
#         current = {
#             (fn, ln)
#             for fn in data.measured_files()
#             for ln in (data.lines(fn) or [])
#         }
#         print(f"[coverage] total covered lines this snapshot: {len(current)}")
#         new = current - self._covered
#         print(f"[coverage] new lines this iteration: {len(new)}")
#         if new:
#             self._covered |= new
#             return True
#         return False

#     # ——— crash & seed persistence ——————————————————————————————————————
#     def _save_crash(self, payload, status, body):
#         os.makedirs('crashes', exist_ok=True)
#         fname = f"crashes/{int(time.time())}_{status}.json"
#         with open(fname, 'w') as f:
#             json.dump({'payload': payload, 'status': status, 'body': body.decode(errors='ignore')}, f)

#     def _queue_new_seed(self, payload):
#         os.makedirs('queue', exist_ok=True)
#         idx = len(os.listdir('queue'))
#         with open(f'queue/seed_{idx}.json', 'w') as f:
#             json.dump(payload, f)
#         # also add to in-memory queue
#         self.seedQ.append({"seed": payload, "s": 0, "f": 1, "alpha": 20})

#     # ——— payload shaping —————————————————————————————————————————————
#     def _prepare_payload(self, base):
#         mutated = self.mutate_input(base)
#         # only keep valid keys
#         return {k: mutated[k] for k in ("name", "info", "price") if k in mutated}
    
# class RaceTest(LiveServerTestCase):
#     # disable the transaction wrapper so each request really commits
#     serialized_rollback = True  

#     def test_race_condition(self):
#         url = self.live_server_url + '/datatb/product/add/'

#         def send(i):
#             body = {"name": f"race number {i}", "info": "race", "price": "10"}
#             try:
#                 r = requests.post(url, json=body, timeout=5)
#                 logger.info("Race condition request %s response: %s", i, r.text)
#             except requests.exceptions.RequestException as e:
#                 logger.error("Race condition request %s failed: %s", i, e)
#         threads = [threading.Thread(target=send, args=(i,)) for i in range(20)]
#         for t in threads: t.start()
#         for t in threads: t.join()