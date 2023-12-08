import math
import random


class RandomPrimeGenerator:

    def __init__(self):
        pass

    def generate_random_prime(self, min=int(1E20), max=int(1E50)):
        p = random.randint(min, max)
        while not self.is_prime(p):
            p = random.randint(min, max)
        return p

    def generate_random_primes(self):
        return self.generate_random_prime(), self.generate_random_prime()

    def is_prime(self, p):
        # use rabin miller
        if p <= 2:
            return True
        bound = int(math.sqrt(p)) + 1
        for i in range(2, bound):
            if p % i == 0:
                return False
        return True


class Rsa_private_key:
    def __init__(self, p, q):
        self.n = p * q
        self._totient = (p - 1) * (q-1)
        self.e = self._calculateE(self._totient)
        self.d = self._calculateD(self._totient, self.e)

    def _calculateE(self, totient):
        for i in range(2, totient):
            if math.gcd(i, totient) == 1:
                return i
        raise Exception("No E in range Exists")

    def gcdExtended(self, a, b):
        # Base Case
        if a == 0:
            return b, 0, 1

        gcd, x1, y1 = self.gcdExtended(b % a, a)

        # Update x and y using results of recursive
        # call
        x = y1 - (b//a) * x1
        y = x1

        return gcd, x, y

    def _calculateD(self, totient, e):
        gcd, x, y = self.gcdExtended(e, totient)
        d = x + totient if x < 0 else x
        return d


class Rsa_public_key:
    def __init__(self, e, N):
        self.e = e
        self.n = N


class RsaClient:
    def __init__(self, p, q):
        self._private_key = Rsa_private_key(p, q)
        self.public_key = Rsa_public_key(
            self._private_key.e, self._private_key.n)

    def encrypt(self, msg: int, public_key: Rsa_public_key):
        return pow(msg, public_key.e, public_key.n)

    def decrypt(self, cipher: int):
        return pow(cipher, self._private_key.d, self._private_key.n)
