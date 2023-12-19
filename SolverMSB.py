from datetime import datetime
import logging
import math
from multiprocessing.pool import Pool
import time
from multiprocessing import Pool

import pprofile
import rsa

def get_first_n_digits( num, n):
    return int(str(num)[0:n])


def get_digits_in_num( num):
    return len(str(num))


def get_msb( key):
    return int(str(key)[0])


def get_most_significant_two_digits( key):
    return int(str(key)[0:1])
    return msb
# assumptions:
# * p and q differ by at most 2**(n-1)  (floor log10 delta)
# * At most one addition carry can be applied to the msb
def get_starting_coditions( key):
    numDigits = get_digits_in_num(key)
    numDigits_half = math.ceil(numDigits/2)-1
    target = get_msb(key)
    target1 = target -1
    if target1 == 0:
        target1 = 9
    starting_conditions = []
    for i in range(0, 100):
        for j in range(0, 100):
            try:
                pkey = i*j
                msb = get_msb(pkey)
                if msb == target:
                    i1 =i*10**(numDigits_half-1)
                    j1 = j*10**(numDigits_half-1)
                    if get_digits_in_num(i1*j1) == numDigits:
                        starting_conditions.append((i1, j1))
                if msb == target1:
                    i1 = i*10**numDigits_half
                    j1 = j*10**numDigits_half
                    if get_digits_in_num(i1*j1) == numDigits-1:
                        starting_conditions.append((i1, j1))
            except:
                pass
    return list(reversed(starting_conditions))
def can_key_be_reached( key, shard, depth):
    max = "9"*(depth)
    try:
        maxi = int(max)
        p = shard[0] + maxi
        q = shard[1] + maxi
        pq = p *q
        if pq < key:
            return False
    except:
        pass
    return True
def get_key_shard( key):
    numd = get_digits_in_num(key)
    msb = get_msb(key)
    return key + msb*10**numd
def get_factors( key):
    starting_conditions = get_starting_coditions(key)
    numDigits = get_digits_in_num(key)
    numDigits_half = math.ceil(numDigits/2)-1
    for c in starting_conditions:
        res = get_factors_rec(key, get_key_shard(key), c, numDigits_half-1)
        #print(res)
        if res is not None:
            return res
def get_vals_meeting_squeeze_constraint( key, shard, depth):
    #print("enter squeeze")
    retVals = []
    #print(shard)
    for i in range(0, 10):
        for j in range(0, 10):
            i1 = i * (10 ** (depth-1))
            j1 = j * (10 ** (depth-1))
            p = (shard[0] + i1)
            q = (shard[1] + j1)
            pq = p*q
            #print(f"Testing {p} * {q} = {pq}")
            if pq <= key and can_key_be_reached(key, (p, q), depth-1):
                shrd = (max(p,q), min(p, q))
                retVals.append(shrd)
    return retVals



def get_factors_start( key):
    numDigits = get_digits_in_num(key)
    numDigits_half = math.ceil(numDigits/2)
    starting_conditions = []
    for i in range(1,10):
        for j in range(0, 10):
            i1 = i * 10**numDigits_half
            j1 = j * 10**numDigits_half
            starting_conditions.append((i1,j1))
    starting_conditions = get_starting_coditions(key)
    starting_conditions = map(lambda x: (max(x[0],x[1]), min(x[0], x[1])) , starting_conditions)
    starting_conditions = filter(lambda x: x[0]*x[1] < key, starting_conditions)
    starting_conditions = list(filter(lambda x: can_key_be_reached(key, x, numDigits_half-1), starting_conditions))
    starting_conditions = list(sorted(set(starting_conditions)))
    print(f"Starting conditions len: {len(starting_conditions)}: {starting_conditions}")
    for s in starting_conditions:
        res = get_factors_rec(key, s, numDigits_half-2)
        if res is not None:
            return res
    return None

def get_factors_start_mp( key, cores=2):
    numDigits = get_digits_in_num(key)
    numDigits_half = numDigits//2 -1
    if numDigits %2 == 1:
        print("odd num of digits in key")
        numDigits_half = numDigits_half+1
    starting_conditions = []
    for i in range(1,100):
        for j in range(0, 100):
            i1 = i * 10**(numDigits_half-1)
            j1 = j * 10**(numDigits_half-1)
            starting_conditions.append((i1,j1))
    #starting_conditions = get_starting_coditions(key)
    starting_conditions = list(map(lambda x: (max(x[0],x[1]), min(x[0], x[1])) , starting_conditions))
    starting_conditions = list(filter(lambda x: x[0]*x[1] < key, starting_conditions))
    starting_conditions = list(filter(lambda x: can_key_be_reached(key, x, numDigits_half-1), starting_conditions))
    starting_conditions = list(sorted(set(starting_conditions)))
    print(f"Starting conditions len: {len(starting_conditions)}: {starting_conditions}")
    args_list = [(key, i, numDigits_half-1) for i in starting_conditions]
    with Pool(cores) as pool:
        for i in pool.imap_unordered(get_factors_start_mp_helper, args_list, chunksize=1):
            if i is not None:
                print("terminate")
                pool.terminate()
                return i

def get_factors_start_mp_count_half( key, cores=2):
    numDigits = get_digits_in_num(key)
    numDigits_half = numDigits//2 -1
    if numDigits %2 == 1:
        print("odd num of digits in key")
        numDigits_half = numDigits_half+1
    starting_conditions = []
    for i in range(1,100):
        for j in range(0, 100):
            i1 = i * 10**(numDigits_half-1)
            j1 = j * 10**(numDigits_half-1)
            starting_conditions.append((i1,j1))
    #starting_conditions = get_starting_coditions(key)
    starting_conditions = list(map(lambda x: (max(x[0],x[1]), min(x[0], x[1])) , starting_conditions))
    starting_conditions = list(filter(lambda x: x[0]*x[1] < key, starting_conditions))
    starting_conditions = list(filter(lambda x: can_key_be_reached(key, x, numDigits_half-1), starting_conditions))
    starting_conditions = list(sorted(set(starting_conditions)))
    print(f"Starting conditions len: {len(starting_conditions)}: {starting_conditions}")
    args_list = [(key, i, numDigits_half-1) for i in starting_conditions]
    count = 0
    with Pool(cores) as pool:
        for i in pool.imap_unordered(get_factors_start_mp_helper_count_half, args_list, chunksize=1):
            count += i
            print(f"Count:{count}")
    return count

def get_factors_start_mp_helper_count_half( args):
    key, shard, depthPow = args
    return get_mid_point_Count_rec(key, shard, depthPow)

def get_factors_start_mp_helper( args):
    key, shard, depthPow = args
    return get_factors_rec(key, shard, depthPow)

def brute_force_pow1(key, shard):
    pq = shard[0] * shard[1]
    #print(f"p: {shard[0]}; q:{shard[1]}; pq:{pq}; delta; {key-pq}")
    if key% (shard[0] + 1) == 0:
        p = shard[0] + 1
        q = key / p
        return (p, q)
    if key% (shard[0] + 3) == 0:
        p = shard[0] + 3
        q = key / p
        return (p, q)
    if key% (shard[0] + 7) == 0:
        p = shard[0] + 7
        q = key / p
        return (p, q)
    if key% (shard[0] + 9) == 0:
        p = shard[0] + 9
        q = key / p
        return (p, q)
    return None

def can_key_be_reached( key, shard, depth):
    max = "9"*(depth)
    try:
        maxi = int(max)
        p = shard[0] + maxi
        q = shard[1] + maxi
        pq = p *q
        if pq < key:
            return False
    except:
        pass
    return True

def get_vals_meeting_squeeze_constraint_optimized(key, shard, depth):
    #print("enter squeeze")
    retVals = []
    #print(shard)
    for i in range(0, 10):
        i1 = i * (10 ** (depth - 1))
        p = (shard[0] + i1)

        for j in range(0, 10):
            j1 = j * (10 ** (depth-1))
            q = (shard[1] + j1)
            pq = p*q

            #print(f"Testing {p} * {q} = {pq}")
            if pq > key:
                break
            if can_key_be_reached(key, (p, q), depth-1):
                shrd = (max(p,q), min(p, q))
                retVals.append(shrd)
    return retVals

def get_factors_rec( key, shard, depthPow):
    if depthPow == 1:
        r = brute_force_pow1(key, shard)
        return r
    if depthPow == 1:
        return None
    potentials = get_vals_meeting_squeeze_constraint_optimized(key, shard, depthPow)
    potentials = sorted(set(potentials))
    for p in potentials:
        res = get_factors_rec(key, p, depthPow-1)
        if res is not None:
            return res
    return None

def get_mid_point_Count_rec( key, shard, depthPow):
    #logging.info(f"get_factors_rec shard: {shard}; depth:{depthPow}")
    mid = math.ceil(get_digits_in_num(key)/2)
    mid = mid//2-3
    if depthPow == mid:
        return 1
    potentials = get_vals_meeting_squeeze_constraint_optimized(key, shard, depthPow)
    potentials = list(sorted(set(potentials)))
    sum = 0
    for p in potentials:
        res = get_mid_point_Count_rec(key, p, depthPow-1)
        sum += res
    return sum


# Rec algo design MSB -> lsb
# * Get for p-shard and q-shard at given power of 10 0-100 multiplied together that are less than the key
#   * starting power of 10 is NumberOfDigits(key)/2
# * sort combinations of p and q by highest product
# * Recurse in sorted order
# * If maximum product of unknown digits is less than the key terminate branch

filename = "c:\\temp\\rsaLogs\\rsa"

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

if __name__ == '__main__':
    dateTag = datetime.now().strftime("%Y-%b-%d_%H-%M-%S")
    logging.basicConfig(filename=f"{filename}_%s.log" % dateTag, level=logging.DEBUG)
    rsa_complexity = 45
    p1 = rsa.prime.getprime(rsa_complexity)
    p2 = rsa.prime.getprime(rsa_complexity)
    #p1 = 3490529510847650949147849619903898133417764638493387843990820577
    #p2 = 32769132993266709549961988190834461413177642967992942539798288533

    logging.info(f"p1:{p1}")
    logging.info(f"p1:{p2}")
    print(f"p1:{p1}")
    print(f"p2:{p2}")
    key = p1 * p2
    print(f"key: {key}")
    logging.info(f"key: {key}")


    profiler = pprofile.Profile()
    start = time.time()
    factors = get_factors_start_mp(key, 8)
    #factors = get_factors_start_mp_count_half(key, 8)
    print(factors)
    logging.info(factors)
    end = time.time()
    logging.info(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")
    print(f"Elapsed time: {end - start}; RSA complexity: {key.bit_length()} bits")