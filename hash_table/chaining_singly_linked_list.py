from llist import sllist as LinkedList


class ChainedHashTableSLL:

    def __init__(self, size=10):
        self.size = size
        self.table = [LinkedList() for _ in range(size)]

    def lookup(self, key):
        idx = self._hash(key)
        for node in self.table[idx].iternodes():
            k, v = node.value
            if k == key:
                return v
        return None

    def insert(self, key, value):
        idx = self._hash(key)
        for node in self.table[idx].iternodes():
            k, v = node.value
            if k == key:
                node.value = (key, value)
                return
        self.table[idx].appendleft((key, value))

    def delete(self, key):
        idx = self._hash(key)
        for node in self.table[idx].iternodes():
            k, _ = node.value
            if k == key:
                self.table[idx].remove(node)
                return True
        return False

    def _hash(self, key):
        return hash(key) % self.size


ht = ChainedHashTableSLL()

ht.insert(8, "value_8")
ht.insert(12, "value_12")
ht.insert(22, "value_22")

print(ht.lookup(12))    # value_12

ht.delete(12)
print(ht.lookup(12))    # None
