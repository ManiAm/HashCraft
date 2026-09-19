class ChainedHashTableList:

    def __init__(self, size=10):
        self.size = size
        self.table = [[] for _ in range(size)]

    def lookup(self, key):
        idx = self._hash(key)
        for k, v in self.table[idx]:
            if k == key:
                return v
        return None

    def insert(self, key, value):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                self.table[idx][i] = (key, value)
                return
        self.table[idx].append((key, value))

    def delete(self, key):
        idx = self._hash(key)
        for i, (k, v) in enumerate(self.table[idx]):
            if k == key:
                del self.table[idx][i]
                return True
        return False

    def _hash(self, key):
        return hash(key) % self.size


ht = ChainedHashTableList()

ht.insert("apple", 5)
ht.insert("banana", 7)

print(ht.lookup("apple"))   # 5

ht.delete("apple")
print(ht.lookup("apple"))   # None
