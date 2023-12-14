import math
import random


class RandomPrimeGenerator:
    def __init__(self):
        pass

    def generate_random_prime(self, min=int(1e20), max=int(1e50)):
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
        self._totient = (p - 1) * (q - 1)
        # self.e = self._calculateE(self._totient)
        gen = self._calculateE(self._totient)
        self.e = next(gen)  # 3
        # self._calculateD(self._totient, self.e)
        # self.d = self._calculateD(self.e, self._totient)
        self.d = self._calculateD(self.e, self._totient)
        print("D: ", self.d)

    def _calculateE(self, totient):
        for i in range(2, totient):
            if math.gcd(i, totient) == 1:
                yield i
        raise Exception("No E in range Exists")

    def _calculateD(self, e, totient):
        gcd, x, y = self.extended_gcd(e, totient)
        return x + totient if x < 0 else x

    def extended_gcd(self, a, b):
        x, old_x = 0, 1
        y, old_y = 1, 0

        while b != 0:
            quotient = a // b
            a, b = b, a - quotient * b
            old_x, x = x, old_x - quotient * x
            old_y, y = y, old_y - quotient * y

        return a, old_x, old_y
        # https://he.wikipedia.org/wiki/RSA#%D7%90%D7%9C%D7%92%D7%95%D7%A8%D7%99%D7%AA%D7%9E%D7%99%D7%9D


class Rsa_public_key:
    def __init__(self, e, N):
        self.e = e
        self.n = N


class RsaClient:
    def __init__(self, p, q):
        self._private_key = Rsa_private_key(p, q)
        self.public_key = Rsa_public_key(self._private_key.e, self._private_key.n)

    def encrypt(self, msg: int, public_key: Rsa_public_key):
        print("Encoding with: ", public_key.e, public_key.n)
        return pow(msg, public_key.e, public_key.n)

    def decrypt(self, cipher: int):
        return pow(cipher, self._private_key.d, self._private_key.n)
