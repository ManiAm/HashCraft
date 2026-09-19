import enum


class NodeState(enum.Enum):
    EMPTY = 0
    OCCUPIED = 1
    DELETED = 2


class Node:

    def __init__(self, key=None, value=None, state=NodeState.EMPTY):
        self.key = key
        self.value = value
        self.state = state


class LinearProbeHashTable:

    def __init__(self, size):
        self.size = size
        self.table = [Node() for _ in range(size)]

    def lookup(self, key):
        idx = self._hash(key)
        start = idx

        while self.table[idx].state != NodeState.EMPTY:
            n = self.table[idx]
            if n.state == NodeState.OCCUPIED and n.key == key:
                return idx

            idx = (idx + 1) % self.size
            if idx == start:
                break

        return -1

    def insert(self, key, value):
        idx = self._hash(key)
        start = idx
        first_tombstone = None

        while self.table[idx].state != NodeState.EMPTY:
            n = self.table[idx]

            if n.state == NodeState.OCCUPIED and n.key == key:
                n.value = value
                return

            if n.state == NodeState.DELETED and first_tombstone is None:
                first_tombstone = idx

            idx = (idx + 1) % self.size
            if idx == start:
                raise Exception("table is full")

        target = first_tombstone if first_tombstone is not None else idx
        self.table[target] = Node(key, value, NodeState.OCCUPIED)

    def delete(self, key):
        idx = self.lookup(key)
        if idx == -1:
            return False

        self.table[idx].key = None
        self.table[idx].value = None
        self.table[idx].state = NodeState.DELETED
        return True

    def _hash(self, key):
        return key % self.size


ht = LinearProbeHashTable(10)

ht.insert(8, "value_8")     # stored at index 8
ht.insert(18, "value_18")   # collides → stored at index 9
ht.insert(28, "value_28")   # collides → stored at index 0
ht.insert(38, "value_38")   # collides → stored at index 1

ht.delete(18)               # index 9 marked DELETED

idx = ht.lookup(28)         # probes 8 → 9 (DELETED, skip) → 0 (found)
print(idx)                   # 0
