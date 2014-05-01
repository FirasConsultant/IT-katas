from random import randrange
import operator

#### Miller-Rabin primality test ####

def miller_rabin(n, k):
    'Apply Miller-Rabin test to `n`, `k` times.'
    if n < 2:
        return False
    d = n-1
    s = 0
    while (d & 1 == 0):
        d >>= 1
        s += 1
    composite = False
    while not composite and k > 0:
        a = randrange(2, n-1)
        a = pow(a,d,n)
        if a != 1 and a != n-1:
            for i in range(s):
                a = pow(a,2,n)
                if a == 1:
                    composite = True
                    break
                elif a == n-1:
                    break
            else:
                composite = True
        k -= 1
    return composite

def miller_rabin_witness(n, a):
    'Test whether `a` is a Miller-Rabin compositeness witness for `n`.'
    if n < 2 or a % n == 0:
        return False
    d = n-1
    s = 0
    while (d & 1 == 0):
        d >>= 1
        s += 1
    composite = False
    a = pow(a,d,n)
    if a != 1 and a != n-1:
        for i in range(s):
            a = pow(a,2,n)
            if a == 1:
                composite = True
                break
            elif a == n-1:
                break
        else:
            composite = True
    return composite

def next_probable_prime(n):
    'Return the smallest integer >= n passing 20 Miller-Rabin tests.'
    if n & 1 == 0:
        n += 1
    while miller_rabin(n, 1):
        n += 2
    if not miller_rabin(n, 20):
        return n
    else:
        return next_probable_prime(n+1)


#### p-1 factorization ####
def rand_smooth_prime(random, n=100, k=2):
    '''
    Return random prime such that p-1 is n-smooth.
    
    Looks for primes of the form n!/a_1 a_2 ... a_k + 1 with random
    a_i.
    '''
    fact = reduce(operator.mul, xrange(1,n))
    p = 4
    while miller_rabin(p, 20):
        cofact = reduce(operator.mul, random.sample(xrange(1,n), k))
        p = fact/cofact + 1

    return p
