from hashlib import sha256


def updatehash(*args):
    hashing_text = ""
    h = sha256()
    for arg in args:
        hashing_text += str(arg)
    h.update(hashing_text.encode('utf-8'))
    return h.hexdigest()

class Block():
    data = None
    hash = None
    nonce = 0
    previous_hash = "0" * 64

    def __init__(self, data, number=0):
        self.data = data
        self.number = number

    def hash(self):
        return updatehash(self.previous_hash, self.number, self.data, self.nonce)

    def __str__(self):
        return "Block#: {}\nHash: {}\nPrevious: {}\nData: {}\nNonce: {}\n".format(
            self.number,
            self.hash(),
            self.previous_hash,
            self.data,
            self.nonce
        )

class Blockchain():
    difficulty = 4

    def __init__(self, chain=[]):
        self.chain = chain

    def add(self, block):
        self.chain.append(block)

    def remove(self, block):
        self.chain.remove(block)

    def mine(self, block):
        try:
            block.previous_hash = self.chain[-1].hash() # this raise index error
        except IndexError:
            pass

        while True:
            if block.hash()[:self.difficulty] == "0" * self.difficulty:
                self.add(block)
                break
            else:
                block.nonce += 1
    def isvalid(self):
        for b in range(1, len(self.chain)):
            _previous = self.chain[b].previous_hash
            _current = self.chain[b-1].hash()
            if _previous != _current or _current[:self.difficulty] != "0"*self.difficulty:
                return False
        return True




def main():
    blockchain = Blockchain()
    database = ["hello world", "what's up", "hello", "bye"]

    num = 0
    for data in database:
        num += 1
        blockchain.mine(Block(data, num))

    for block in blockchain.chain:
         print(block)
         #to check the blcokblockchain.chain[2].data = "New Data"
         #blockchain.mine(blockchain.chain[2])
    print(blockchain.isvalid())

main()
