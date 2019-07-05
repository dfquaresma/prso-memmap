table = {}

for i in range(1024):
    table[i] = (0,0)

def address_to_bin(v_address):
    binary = bin(v_address)
    binary = binary.replace('0b', '').strip()

    max_mem_size = 32

    if (len(binary) < max_mem_size):
        offset = max_mem_size - len(binary)
        binary = '0' * offset + binary
    return binary

def map(v_address):
    page_fault = 0

    binary = address_to_bin(v_address)

    msb = binary[0]
    lsb = binary[]
    page = binary[1:11]
