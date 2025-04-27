class Seed:
    def __init__(self, data, path, covered_lines):
        self.data = data
        self.path = path
        self.covered_lines = covered_lines
        self.s = 0 # times chosen
        self.f = 1 
    def __repr__(self):
        return f"<Seeds={self.s} f={self.f} path={self.path} data = {self.data}>"