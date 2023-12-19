import math
import time
from datetime import datetime
from multiprocessing import Pool
import logging
import logging.handlers
import rsa.prime
import pprofile
import SolverLSB
import SolverMSB

filename = "c:\\temp\\rsaLogs\\rsa"
counter = 0


mult_table = {
    0: [(4, 0), (6, 5), (0, 0), (5, 4), (7, 0), (2, 0), (8, 0), (3, 0), (5, 0), (6, 0), (1, 0), (8, 5), (5, 2)],
    1: [(1, 1), (7, 3)],
    2: [(6, 2), (8, 4), (2, 1), (4, 3), (7, 6)],
    3: [(3, 1)],
    4: [(8, 8), (6, 4), (8, 3), (7, 2), (2, 2), (4, 1)],
    5: [(5, 3), (7, 5), (5, 5), (5, 1)],
    6: [(4, 4), (8, 7), (6, 1), (6, 6), (8, 2), (3, 2)],
    7: [(7, 1)],
    8: [(7, 4), (8, 1), (4, 2), (8, 6), (6, 3)],
    9: [(3, 3), (7, 7)]
}

def get_msb(key):
    return int(str(key)[0])


def get_lsb(key):
    return int(str(key)[-1])

def get_digit(number, n):
    return number // 10**n % 10

def log_setup():
    # Create a logger
    logger = logging.getLogger(__name__)
    # Set the log level
    logger.setLevel(logging.INFO)
    # Create a rotating file handler
    handler = logging.handlers.RotatingFileHandler(filename, backupCount=5)
    # Set the formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # Add the handler to the logger
    logger.addHandler(handler)
    return  logger

def get_starting_coditions( key):
    mod = key%10
    if mod == 1:
        return [ (9,9), (3, 7), (1, 1)]
    if mod == 3:
        return [(7, 9), (1, 3)]
    if mod == 7:
        return [(3, 9), (1, 7)]
    if mod == 9:
        return [(7, 7), (3, 3), (1, 9)]
def get_factors_pair( x):
    nums = []
    for i in range(1, x + 1):
        if x % i == 0:
            otherDivisor = x//i
            nums.append((min(i, otherDivisor), max(i, otherDivisor)))
    return nums
def get_factors( key):
    global counter
    for f in get_starting_coditions(key):
        counter = 0
        print(f"Testing seed: {f}")
        logging.info(f"Testing seed: {f}")
        start = time.time()
        res = get_factors_rec_table(key, f, 10, {})
        end = time.time()
        print(f"Time for {f}: {end-start}; calls: {counter}")
        logging.info(f"Time for {f}: {end-start}; calls: {counter}")
        if res is not None:
            return res

def process_chunk( args):
    key, sub_factor, depth = args
    bag = {}
    start = time.time()
    res = get_factors_rec_table(key, sub_factor, 10, {})
    #res = get_factors_iterative(key, sub_factor, 10, {})
    end = time.time()
    print(f"Time for {sub_factor}: {end - start}; calls: {counter}")
    return res


def get_factors_mp( key, cores):
    args_list = [(key, i, 2) for i in get_starting_coditions(key)]
    #with Pool(cores) as pool:
    #   results = pool.map(process_chunk, args_list)
    with Pool(cores) as pool:
        for i in pool.imap_unordered(process_chunk, args_list, chunksize=1):
            if i is not None:
                print("terminate")
                pool.terminate()
                return i

# do a table lookup for potential digit. lookupkey is key-lsb at pow10

def get_factors_rec( key, sub_factor, depth, dic):

    if depth in dic:
        key_sqrt = dic[depth]
    else:
        sqr = ((depth*10)**2)
        key_sqrt2 = key % sqr
        key_sqrt2 = key_sqrt2 + (sqr/5)
        key_sqrt = math.sqrt(key_sqrt2)
        dic[depth] = key_sqrt+1
    pkey = sub_factor[0] * sub_factor[1]

    if pkey.bit_length() >= key.bit_length():
        if sub_factor[0] == key or sub_factor[1] == key:
            return None
        if pkey == key:
            return sub_factor
        return None
    depth10 = depth*10
    keyModDepth10 = key % depth10
    routes = []
    for i in range(0, 10):
        p = sub_factor[0] + i * depth
        q = sub_factor[1]
        pq = p*q
        if pq > key:
            break
        for j in range(0, 10):
            q = sub_factor[1] + j * depth

            m = min(p,q)
            if m > key_sqrt:
                break
            pq = p * q

            if pq % depth10 == keyModDepth10:
                routes.append((p, q))
    #print(f"subfactor: {sub_factor}; Len of possibilities: {len(srt)}")
    if len(routes) < 8:
        return None
    srt = sorted(routes, key=lambda x: max(x[0], x[1]) - min(x[0], x[1]))

    for r in srt:
        res = get_factors_rec(key, r, depth10, dic)
        if res is not None:
            return res
    return None


def get_factors_rec_table( key, sub_factor, depth, dic):

    pkey = sub_factor[0] * sub_factor[1]

    if pkey.bit_length() >= key.bit_length():
        if sub_factor[0] == 1 or sub_factor[1] == 1:
            return None
        if pkey == key:
            return sub_factor
        return None
    depth10 = depth*10
    depth100 = depth*100
    delta_key = key - pkey
    keyModDepth10 = key % depth10
    delta_keyModDepth10 = delta_key % depth100
    routes1 = mult_table[get_msb(delta_keyModDepth10)]
    routes = []
    for route in routes1:
        p = sub_factor[0] + (route[0] * depth)
        q = sub_factor[1] + (route[1] * depth)
        pq = p*q

        if pq <= key and pq % depth10 == keyModDepth10:
            routes.append((p, q))
    srt = sorted(routes, key=lambda x: max(x[0], x[1]) - min(x[0], x[1]))

    for r in srt:
        res = get_factors_rec_table(key, r, depth10, dic)
        if res is not None:
            return res
    return None


def get_factors_iterative( key, sub_factor, depth, bag):
    stack = [(key, sub_factor, depth)]
    while stack:
        key, sub_factor, depth = stack.pop()
        logging.debug(f"sub_factor: {sub_factor}; depth: {depth}")
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
                logging.debug(f"Breaking outer. pq greater than key. pq: {pq}; keyMod:{keyModDepth}")
                break
            for j in range(0, 10):
                q = sub_factor[1] + j * depth
                pq = p * q
                if pq > key:
                    logging.debug(f"Breaking. pq greater than key. pq: {pq}; keyMod:{keyModDepth}")
                    break
                if pq % depth10 == keyModDepth:
                    logging.debug(f"pq success:{pq}; keyMod:{keyModDepth}")
                    stack.append((key, (p, q), depth10))
                    break  # Break inner loop
                logging.debug(f"pq failure:{pq}; keyMod:{keyModDepth}")
        bag.add((pkey, depth))
    return None


def test_pair(key, pair):
    return get_factors_rec_table(key, pair, 10, {})

# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dateTag = datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
    logging.basicConfig(filename=f"{filename}_%s.log" % dateTag, level=logging.DEBUG)
    rsa_complexity = 22
    p1 = rsa.prime.getprime(rsa_complexity)
    p2 = rsa.prime.getprime(rsa_complexity)
    p1 = 2578529
    p2 = 3276551

    logging.info(f"p1:{p1}")
    logging.info(f"p1:{p2}")
    print(f"p1:{p1}")
    print(f"p2:{p2}")
    key = p1 *p2
    print(f"key: {key}")
    logging.info(f"key: {key}")


    profiler = pprofile.Profile()
    start = time.time()
    #factors = get_factors(key)
    factors = test_pair(key, (9, 1))
    print(factors)
    logging.info(factors)
    end = time.time()
    logging.info(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")
    print(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")
    #with profiler:
    #    start = time.time()
    #    print(get_factors(key))
    #    end = time.time()
    #    logging.info(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")
    #    print(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")
#
    #profiler.dump_stats("c:\\temp\\profiler_stats1.txt")
