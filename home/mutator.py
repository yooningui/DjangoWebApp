from abc import ABC, abstractmethod
import random, string
import copy 

class NumberMutation(ABC):
    @abstractmethod
    def mutate(self, n: int) -> int:
        """Mutate an integer and return the new value."""
    
        pass

class StringMutation(ABC):
    @abstractmethod
    def mutate(self, s: str) -> str:
        """Mutate a string and return the new value."""
        pass

class ByteListMutation(ABC):
    @abstractmethod
    def mutate(self, b: list[int]) -> list[int]:
        """Mutate a byte‐list and return the new list."""
        pass

# —— Number mutations —— #

class AddSubtract(NumberMutation):
    def mutate(self, n: int) -> int:
        delta = random.randint(1, 10)
        return n + random.choice((-delta, delta))

class MulDiv(NumberMutation):
    def mutate(self, n: int) -> int:
        factor = random.choice((0.5, 2))
        return int(n * factor) if factor != 0.5 else int(n / 2)

class FlipBit(NumberMutation):
    def mutate(self, n: int) -> int:
        bit = 1 << random.randint(0, 31)
        return n ^ bit

class LargeConst(NumberMutation):
    def mutate(self, n: int) -> int:
        return (2**32) - 1

class SmallConst(NumberMutation):
    def mutate(self, n: int) -> int:
        return -((2**32) - 1)

# —— String mutations —— #

class DeleteChar(StringMutation):
    def mutate(self, s: str) -> str:
        if not s: return s
        i = random.randrange(len(s))
        return s[:i] + s[i+1:]

class InsertChar(StringMutation):
    ALL = string.digits + string.ascii_letters + string.punctuation
    def mutate(self, s: str) -> str:
        i = random.randrange(len(s)+1)
        c = random.choice(self.ALL)
        return s[:i] + c + s[i:]

class FlipChar(StringMutation):
    def mutate(self, s: str) -> str:
        if not s: return s
        ba = bytearray(s, 'utf-8')
        idx = random.randrange(len(ba))
        bit = 1 << random.randrange(8)
        ba[idx] ^= bit
        return ba.decode('utf-8', errors='ignore')

class ExtremeString(StringMutation):
    ALL = string.digits + string.ascii_letters + string.punctuation
    def mutate(self, s: str) -> str:
        if random.choice((True, False)):
            return ''.join(random.choice(self.ALL) for _ in range(256))
        return ''

# —— Byte-list mutations —— #

class ReplaceByte(ByteListMutation):
    def mutate(self, b: list[int]) -> list[int]:
        if not b: return b
        i = random.randrange(len(b))
        b[i] = random.randint(0, 255)
        return b

class InsertByte(ByteListMutation):
    def mutate(self, b: list[int]) -> list[int]:
        i = random.randrange(len(b)+1)
        b.insert(i, random.randint(0,255))
        return b

class RemoveBytes(ByteListMutation):
    def mutate(self, b: list[int]) -> list[int]:
        if not b: return b
        n = random.randint(1, len(b))
        for _ in range(n):
            if not b: break
            del b[random.randrange(len(b))]
        return b

class FlipBitByte(ByteListMutation):
    def mutate(self, b: list[int]) -> list[int]:
        if not b: return b
        idx = random.randrange(len(b))
        bit = 1 << random.randrange(8)
        b[idx] ^= bit
        return b

class Havoc(ByteListMutation):
    def mutate(self, b: list[int]) -> list[int]:
        b.insert(0, 0xFF)
        return b

class EmptyList(ByteListMutation):
    def mutate(self, b: list[int]) -> list[int]:
        return []

class Mutator:
    def __init__(self):
        self.num_mutators    = [AddSubtract(), MulDiv(), FlipBit(), LargeConst(), SmallConst()]
        self.str_mutators    = [DeleteChar(), InsertChar(), FlipChar(), ExtremeString()]
        self.bylist_mutators = [ReplaceByte(), InsertByte(), RemoveBytes(),
                                FlipBitByte(), Havoc(), EmptyList()]

    def mutate_field(self, field):
        if isinstance(field, int):
            m = random.choice(self.num_mutators)
        elif isinstance(field, str):
            m = random.choice(self.str_mutators)
        elif isinstance(field, list):
            m = random.choice(self.bylist_mutators)
        else:
            return field
        return m.mutate(copy.deepcopy(field))

    def mutate(self, attributes: list) -> list:
        # Choose one attribute at random to mutate
        out = copy.deepcopy(attributes)
        i = random.randrange(len(out))
        out[i] = self.mutate_field(out[i])
        return out
