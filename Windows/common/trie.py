from queue import Queue


class Trie:

    def __init__(self):
        self.key = ''
        self.value = None
        self.children = [None] * 26
        self.isEnd = False

    def insert(self, key: str, value):
        key = key.lower()

        node = self
        for c in key:
            i = ord(c) - 97
            if not 0 <= i < 26:
                return

            if not node.children[i]:
                node.children[i] = Trie()

            node = node.children[i]

        node.isEnd = True
        node.key = key
        node.value = value

    def get(self, key, default=None):
        node = self.searchPrefix(key)
        if not (node and node.isEnd):
            return default

        return node.value

    def searchPrefix(self, prefix):
        prefix = prefix.lower()
        node = self
        for c in prefix:
            i = ord(c) - 97
            if not (0 <= i < 26 and node.children[i]):
                return None

            node = node.children[i]

        return node

    def items(self, prefix):
        node = self.searchPrefix(prefix)
        if not node:
            return []

        q = Queue()
        result = []
        q.put(node)

        while not q.empty():
            node = q.get()
            if node.isEnd:
                result.append((node.key, node.value))

            for c in node.children:
                if c:
                    q.put(c)

        return result
