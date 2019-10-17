import sys, math, random
sys.setrecursionlimit(5000)

""" Usage:
        Generate keys - python rsa.py -g <bits>
        Encrypt text  - python rsa.py -e <text to encrypt> <encryption key> <n>
        Decrypt text  - python rsa.py -d <text to decrypt> <decryption key> <n>
"""

def gcd(a, b):
    while b != 0:
        a, b = b, a % b
    return a

def coprime(a, b):
    return gcd(a, b) == 1

def is_prime(n, k=128):        #https://medium.com/@prudywsh/how-to-generate-big-prime-numbers-miller-rabin-49e6e6af32fb
    """ Test if a number is prime
        Args:
            n -- int -- the number to test
            k -- int -- the number of tests to do
        return True if n is prime
    """
    # Test if n is not even.
    # But care, 2 is prime !
    if n == 2 or n == 3:
        return True
    if n <= 1 or n % 2 == 0:
        return False
    # find r and s
    s = 0
    r = n - 1
    while r & 1 == 0:
        s += 1
        r //= 2
    # do k tests
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = pow(a, r, n)
        if x != 1 and x != n - 1:
            j = 1
            while j < s and x != n - 1:
                x = pow(x, 2, n)
                if x == 1:
                    return False
                j += 1
            if x != n - 1:
                return False
    return True

def generate_prime_candidate(length):
    """ Generate an odd integer randomly
        Args:
            length -- int -- the length of the number to generate, in bits
        return a integer
    """
    # generate random bits
    p = random.getrandbits(length)
    # apply a mask to set MSB and LSB to 1
    p |= (1 << length - 1) | 1
    return p

def generate_prime_number(length=1024):
    """ Generate a prime
        Args:
            length -- int -- length of the prime to generate, in          bits
        return a prime
    """
    p = 4
    # keep generating while the primality test fail
    while not is_prime(p, 128):
        p = generate_prime_candidate(length)
    return p

def powermod(a,b,m):
    if b == 0:
        return 1
    if b == 1:
        return a % m
    if b % 2 == 1:
        return (powermod(a,b-1,m) * a) % m
    else:
        return powermod((a*a) % m,b//2,m) % m

def generate(nbits):
    n = 0
    while (len(bin(n))-2) != nbits:
        pqbits = nbits//2
        p = generate_prime_number(pqbits)
        q = generate_prime_number(pqbits)
        n = p * q
    phin = (p-1)*(q-1)
    while True:
        e = random.randint(2, phin-1)
        if coprime(e,n):
            if coprime(e,phin):
                break
    #Calculating D using modular inverses
    qs = [0, 0]
    rs = [phin, e]
    xs = [0, 1]
    i = 2
    while rs[-1] != 1:
        qs.append(rs[i-2] // rs[i-1])
        rs.append(rs[i-2] - (qs[i] * rs[i-1]))
        xs.append(xs[i-2] - (qs[i] * xs[i-1]))
        i += 1
    d = xs[-1]
    while d < 0:
        d += phin
    return [e, d, n]

def crypt(numlist, key, n):
    encryptednumlist = []
    for num in numlist:
        encryptednumlist.append(powermod(num,key,n))
    return encryptednumlist

if '-g' in sys.argv:
    edest = 'print'
    ddest = 'print'
    ndest = 'print'
    [e, d, n] = generate(int(sys.argv[2]))
    for arg in sys.argv[3:]:
        if arg[0:2] == '-e':
            edest = arg[3:]
            continue
        if arg[0:2] == '-d':
            ddest = arg[3:]
            continue
        if arg[0:2] == '-n':
            ndest = arg[3:]
            continue
    if edest == 'print':
        print('Encryption Key --------------------')
        print(str(e))
    else:
        efile = open(edest+'.txt', 'w')
        efile.write(str(e))
        efile.close()
    if ddest == 'print':
        print('Decryption Key --------------------')
        print(str(d))
    else:
        dfile = open(ddest+'.txt', 'w')
        dfile.write(str(d))
        dfile.close()
    if ndest == 'print':
        print('N ---------------------------------')
        print(str(n))
    else:
        nfile = open(ndest+'.txt', 'w')
        nfile.write(str(n))
        nfile.close()
    print('Key generated Successfully!')
    sys.exit()
if '-e' in sys.argv:
    output = 'print'
    if len(sys.argv) > 5:
        output = sys.argv[5]
    if sys.argv[2][0:2] == '-f':
        tfile = open(sys.argv[2][3:]+'.txt', 'r')
        text = tfile.read()
        tfile.close()
    else:
        text = sys.argv[2]
    if sys.argv[3][0:2] == '-f':
        efile = open(sys.argv[3][3:]+'.txt', 'r')
        e = int(efile.read())
        efile.close()
    else:
        e = int(sys.argv[3])
    if sys.argv[4][0:2] == '-f':
        nfile = open(sys.argv[4][3:]+'.txt', 'r')
        n = int(nfile.read())
        nfile.close()
    else:
        n = int(sys.argv[4])
    numlist = []
    encryptednumlist = []
    encryptedtext = ''
    for char in text:
        numlist.append(ord(char))
    encryptednumlist = crypt(numlist, e, n)
    for num in encryptednumlist:
        encryptedtext = encryptedtext + str(num) + '.'
    encryptedtext = encryptedtext[:-1]
    if output == 'print':
        print('Encrypted Text --------------------')
        print(encryptedtext)
    else:
        outputfile = open(output+'.txt', 'w')
        outputfile.write(encryptedtext)
        outputfile.close()
    print('Text Encrypted Successfully!')
    sys.exit()
if '-d' in sys.argv:
    output = 'print'
    if len(sys.argv) > 5:
        output = sys.argv[5]
    if sys.argv[2][0:2] == '-f':
        tfile = open(sys.argv[2][3:]+'.txt', 'r')
        text = tfile.read()
        tfile.close()
    else:
        text = sys.argv[2]
    if sys.argv[3][0:2] == '-f':
        dfile = open(sys.argv[3][3:]+'.txt', 'r')
        d = int(dfile.read())
        dfile.close()
    else:
        d = int(sys.argv[3])
    if sys.argv[4][0:2] == '-f':
        nfile = open(sys.argv[4][3:]+'.txt', 'r')
        n = int(nfile.read())
        nfile.close()
    else:
        n = int(sys.argv[4])
    numlist = text.split('.')
    for i, num in enumerate(numlist):
        numlist[i] = int(num)
    decryptednumlist = []
    decryptedtext = ''
    decryptednumlist = crypt(numlist, d, n)
    for num in decryptednumlist:
        decryptedtext = decryptedtext + chr(num)
    if output == 'print':
        print('Decrypted Text --------------------')
        print(decryptedtext)
    else:
        outputfile = open(output+'.txt', 'w')
        outputfile.write(decryptedtext)
        outputfile.close()
    print('Text Decrypted Successfully!')
    sys.exit()
