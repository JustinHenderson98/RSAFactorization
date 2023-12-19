import time
from multiprocessing import Pool
from decimal import *
import math

class SolverLSB:
    
    def __init__(self, logger):
        self.logging = logger

    def get_digit(number, n):
        return number // 10 ** n % 10


    def get_msb(self, key):
        before_div = (10 ** math.floor(math.log10(key)))
        msb = math.floor(key / before_div)
        return msb

    def get_starting_coditions(self, key):
        mod = key%10
        if mod == 1:
            return [ (9,9), (3, 7), (1, 1)]
        if mod == 3:
            return [(7, 9), (1, 3)]
        if mod == 7:
            return [(3, 9), (1, 7)]
        if mod == 9:
            return [(7, 7), (3, 3), (1, 9)]

    def get_factors_pair(self, x):
        nums = []
        for i in range(1, x + 1):
            if x % i == 0:
                otherDivisor = x//i
                nums.append((min(i, otherDivisor), max(i, otherDivisor)))
        return nums

    def get_factors(self, key):
        global counter

        for f in self.get_starting_coditions(key):
            counter = 0
            print(f"Testing seed: {f}")
            self.logging.info(f"Testing seed: {f}")
            start = time.time()
            res = self.get_factors_rec(key, f, 10, set())
            end = time.time()
            print(f"Time for {f}: {end-start}; calls: {counter}")
            self.logging.info(f"Time for {f}: {end-start}; calls: {counter}")

            if res is not None:
                return res

    def process_chunk(self, args):
        key, sub_factor, depth = args
        bag = set()

        start = time.time()
        res = self.get_factors_rec(key, sub_factor, 10, set())
        #res = get_factors_iterative(key, sub_factor, 10, set())
        end = time.time()
        print(f"Time for {sub_factor}: {end - start}; calls: {counter}")
        return res

    def get_factors_mp(self, key, cores):

        args_list = [(key, i, 2) for i in self.get_starting_coditions(key)]

        #with Pool(cores) as pool:
        #   results = pool.map(process_chunk, args_list)
        with Pool(cores) as pool:
            for i in pool.imap_unordered(self.process_chunk, args_list, chunksize=1):
                if i is not None:
                    print("terminate")
                    pool.terminate()
                    return i


    def get_factors_rec(self, key, sub_factor, depth, bag):
        key_sqrt = key % 10**depth*2
        key_sqrt = Decimal(key_sqrt).sqrt()

        self.logging.debug(f"sub_factor: {sub_factor}; depth: {depth}")
        pkey = sub_factor[0] * sub_factor[1]
        #if (pkey, depth) in bag:
            #self.logging.debug(f"Bag contains: {(pkey, depth)}")
            #return None
        if pkey.bit_length() >= key.bit_length():
            if sub_factor[0] == key or sub_factor[1] == key:
                return None
            if pkey == key:
                return sub_factor
            return None
        depth10 = depth*10
        keyModDepth = key % depth10

        if sub_factor[0] > sub_factor[1]:
            sub_factor = (sub_factor[1], sub_factor[0])

        for i in range(0, 10):
            p = sub_factor[0] + i * depth
            q = sub_factor[1]
            pq = p * q
            if pq > key:
                self.logging.debug(f"Breaking outer. pq greater than key. pq: {pq}; keyMod:{keyModDepth}")
                break
            for j in range(0, 10):
                q = sub_factor[1] + j * depth

                #test
                m = min(p,q)
                if m > key_sqrt:
                    print(f"Exceeded sqrt {key_sqrt}. p: {p}; q: {q}")

                pq = p * q

                if pq > key:
                    self.logging.debug(f"Breaking. pq greater than key. pq: {pq}; keyMod:{keyModDepth}")
                    break
                if pq % depth10 == keyModDepth:
                    pqmsb = self.get_msb(pq)

                    keyDigit = self.get_digit(math.log10(p) + math.log10(q)-1)
                    if(pqmsb == keyDigit):
                        print("IS this valid?")

                    self.logging.debug(f"pq success:{pq}; keyMod:{keyModDepth}")
                    res = self.get_factors_rec(key, (p, q), depth10, bag)
                    if res is not None:
                        return res
                self.logging.debug(f"pq failure:{pq}; keyMod:{keyModDepth}")
        #bag.add((pkey, depth))
        return None


    def get_factors_iterative(self, key, sub_factor, depth, bag):
        stack = [(key, sub_factor, depth)]

        while stack:
            key, sub_factor, depth = stack.pop()
            self.logging.debug(f"sub_factor: {sub_factor}; depth: {depth}")

            pkey = sub_factor[0] * sub_factor[1]
            if (pkey, depth) in bag:
                continue

            if pkey.bit_length() >= key.bit_length():
                if sub_factor[0] == key or sub_factor[1] == key:
                    continue
                if pkey == key:
                    return sub_factor
                continue

            depth10 = depth * 10
            keyModDepth = key % depth10
            if sub_factor[0] > sub_factor[1]:
                sub_factor = (sub_factor[1], sub_factor[0])
            for i in range(0, 10):
                p = sub_factor[0] + i * depth
                q = sub_factor[1]
                pq = p * q

                if pq > key:
                    self.logging.debug(f"Breaking outer. pq greater than key. pq: {pq}; keyMod:{keyModDepth}")
                    break

                for j in range(0, 10):
                    q = sub_factor[1] + j * depth
                    pq = p * q

                    if pq > key:
                        self.logging.debug(f"Breaking. pq greater than key. pq: {pq}; keyMod:{keyModDepth}")
                        break

                    if pq % depth10 == keyModDepth:
                        self.logging.debug(f"pq success:{pq}; keyMod:{keyModDepth}")
                        stack.append((key, (p, q), depth10))
                        break  # Break inner loop

                    self.logging.debug(f"pq failure:{pq}; keyMod:{keyModDepth}")

            bag.add((pkey, depth))

        return None