import time
from datetime import datetime
from multiprocessing import Pool
import logging
import logging.handlers
import rsa.prime

filename = "c:\\temp\\rsaLogs\\rsa"


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
    return logger


def get_starting_coditions(key):
    mod = key % 10
    if mod == 1:
        return [(9, 9), (3, 7), (1, 1)]
    if mod == 3:
        return [(7, 9), (1, 3)]
    if mod == 7:
        return [(3, 9), (1, 7)]
    if mod == 9:
        return [(7, 7), (3, 3), (1, 9)]


def get_factors_pair(x):
    nums = []
    for i in range(1, x + 1):
        if x % i == 0:
            other_divisor = x//i
            nums.append((min(i, other_divisor), max(i, other_divisor)))
    return nums


def get_factors(key):
    for f in get_starting_coditions(key):
        print(f"Testing seed: {f}")
        logging.info(f"Testing seed: {f}")
        start = time.time()
        res = get_factors_rec(key, f, 10)
        end = time.time()
        print(f"Time for {f}: {end-start}")
        logging.info(f"Time for {f}: {end-start}")
        if res is not None:
            return res


def process_chunk(args):
    key, sub_factor, depth = args
    start = time.time()
    res = get_factors_rec(key, sub_factor, 10)
    end = time.time()
    print(f"Time for {sub_factor}: {end - start}")
    return res


def get_factors_mp(key, cores):
    args_list = [(key, i, 2) for i in get_starting_coditions(key)]
    with Pool(cores) as pool:
        for i in pool.imap_unordered(process_chunk, args_list, chunksize=1):
            if i is not None:
                print("terminate")
                pool.terminate()
                return i


def get_factors_rec(key, sub_factor, depth):

    pkey = sub_factor[0] * sub_factor[1]

    if pkey.bit_length() >= key.bit_length():
        if sub_factor[0] == key or sub_factor[1] == key:
            return None
        if pkey == key:
            return sub_factor
        return None
    depth10 = depth*10
    key_mod_depth10 = key % depth10
    routes = []
    for i in range(0, 10):
        p = sub_factor[0] + i * depth
        q = sub_factor[1]
        pq = p*q
        if pq > key:
            break
        for j in range(0, 10):
            q = sub_factor[1] + j * depth
            pq = p * q

            if pq % depth10 == key_mod_depth10:
                routes.append((p, q))
    if len(routes) < 8:
        return None
    srt = sorted(routes, key=lambda x: max(x[0], x[1]) - min(x[0], x[1]))

    for r in srt:
        res = get_factors_rec(key, r, depth10)
        if res is not None:
            return res
    return None


# Press the green button in the gutter to run the script.
if __name__ == '__main__':
    dateTag = datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
    logging.basicConfig(filename=f"{filename}_%s.log" % dateTag, level=logging.DEBUG)
    rsa_complexity = 22
    p1 = rsa.prime.getprime(rsa_complexity)
    p2 = rsa.prime.getprime(rsa_complexity)

    logging.info(f"p1:{p1}")
    logging.info(f"p1:{p2}")
    print(f"p1:{p1}")
    print(f"p2:{p2}")
    key = p1 * p2
    print(f"key: {key}")
    logging.info(f"key: {key}")

    start = time.time()
    factors = get_factors(key)
    print(factors)
    logging.info(factors)
    end = time.time()
    logging.info(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")
    print(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")
