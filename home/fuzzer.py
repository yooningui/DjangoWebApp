from copy import deepcopy
from home.mutator import Mutator
import hashlib
from abc import ABC, abstractmethod
from home.seed import Seed
from typing import List
import time

class AFLFuzzer(ABC):
    def __init__(self):
        seedQ =  [] # type: List[Seed]
        self.seedQ = seedQ 
        self.failureQ = [] 
        self.global_lines: set[int] = set()      # ever-seen lines
        self.global_arcs:  set[tuple[int,int]] = set()  # ever-seen edges
        self.interestingPaths: set[str] = set()  # path hashes
        self.mutator = Mutator()
        self.cov = None

    @abstractmethod
    def init_seedQ(self):
        pass

    @abstractmethod
    def mutate_input(self, seed: Seed) -> Seed:
        pass

    @abstractmethod
    def execute(self, mutant: Seed) -> str:
        """
        Execute the mutant and return the result.
        This function should be implemented in the derived class.
        """
        pass

    def reveals_crash(self, result: str) -> bool:
        """
        Check if the result indicates a crash.
        This function should be implemented in the derived class.
        """
        pass
    def choose_next(self)-> Seed:
        self.seedQ.sort(key=lambda seed: (seed.s, seed.f))
        seed = self.seedQ.pop(0)
        seed.s += 1
        return seed
    
    def assign_energy(self, seed: Seed) -> int:
        MAX, alpha = 64 , 20 
        e = (alpha * (2 ** seed.s)) / seed.f

        return max(1, min(MAX, int(e)))
    
    def is_interesting(self, seed: Seed) -> bool:
        """
        Decide whether the current input discovered *new* coverage.
        Returns True ⇢ keep in seed queue, append to interesting.   False ⇢ discard.
        """

        data = self.cov.get_data()
        print(data.measured_files())

         # ----- line coverage -------------------------------------------------
        lines_this_run: set[int] = set()
        for fname in data.measured_files():
            lines_this_run.update(data.lines(fname))

        arcs_this_run: set[tuple[int, int]] = set()
        if data.has_arcs():
            for fname in data.measured_files():
                arcs_this_run.update(data.arcs(fname) or [])
        
        seed.covered_lines = len(lines_this_run)
        seed.path          = len(arcs_this_run)
        path_sig = hashlib.sha1(
            ",".join(f"{a}:{b}" for a, b in sorted(arcs_this_run)).encode()
        ).hexdigest()

        new_lines = lines_this_run - self.global_lines
        new_arcs  = arcs_this_run  - self.global_arcs

        if new_lines or new_arcs or path_sig not in self.interestingPaths:
            self.global_lines.update(new_lines)
            self.global_arcs.update(new_arcs)
            self.interestingPaths.add(path_sig)
            return True        # <- keep it
        return False           # <- throw it away

    def fuzz(self, timeout:int):
        start = time.monotonic()
        self.init_seedQ()

        while self.seedQ and (time.monotonic() - start) < timeout:

            seed = self.choose_next()
            E = self.assign_energy(seed)
            for _ in range(E):
                mutant = self.mutate_input(seed)
                print("─── AFL trial ───")
                print("Parent seed: ", seed.data)
                print("Mutated seed:", mutant.data)

                result = self.execute(mutant)
                status = getattr(result, "status_code", result)
                print("HTTP status:", status)

                if self.reveals_crash(result):
                    print("💥 Crash detected!")
                    self.failureQ.append(mutant)
                elif self.is_interesting(mutant):
                    print("✨ New coverage discovered, enqueueing mutant")
                    self.seedQ.append(mutant)
                else:
                    print("– No new coverage, discarding mutant")
            print(len(self.seedQ), "seeds left in queue")
            print(len(self.failureQ), "seeds in failure queue")
        return {
            "failures": len(self.failureQ),
            "unique_paths": len(self.interestingPaths),
        }



        


        



    



    






        