import os, random, json, string, subprocess, time, asyncio
from typing import Dict, Tuple
from home.fuzzer import AFLFuzzer      # your base class
from home.mutator import Mutator
from home.seed import Seed
import requests
import asyncio

    
class DjangoFuzzer(AFLFuzzer):
    def __init__(self, seed_path=None, cov = None, client = None):
        super().__init__()
        self.mutator = Mutator()
        self.seed_path = seed_path
        self.cov = cov
        self.client = client
        self.init_seedQ()
        
    def init_seedQ(self):
        with open(self.seed_path, "r") as f:
            payload = json.load(f)
        
        seed = Seed(
            data = payload,
            path = "",
            covered_lines= 0,
        )
        seed.f = 1
        seed.s = 0
        self.seedQ.append(seed)

    def mutate_input(self, seed: Seed) -> Seed:
        new_payload = json.loads(json.dumps(seed.data))
        field = random.choice(list(new_payload.keys()))
        value = new_payload[field]
        new_payload[field] = self.mutator.mutate_field(value)

        mutated_seed = Seed(data=new_payload, path="", covered_lines=0)
        mutated_seed.s = 0; mutated_seed.f = 1
        return mutated_seed
    
    def execute(self, seed: Seed) -> str:
         return self.client.post(
            "/datatb/product/add/",
            json.dumps(seed.data),
            content_type="application/json"
        )
    
    def reveals_crash(self, result: str) -> bool:
        return result.status_code != 200
    
