from hashlib import sha256

LEAF = b"\x00"
NODE = b"\x01"
KEYSIZE = 32
DEPTH = KEYSIZE * 8

RIGHT = 1
PLACEHOLDER = bytes(32)
DEFAULTVALUE = b""


def create_leaf(path, leaf_data):
    value = b"".join([LEAF, path, leaf_data])
    hash = digest(value)
    return (hash, value)


def parse_leaf(data):
    return (data[1:33], data[33:])


def is_leaf(data):
    return data[0] == 0


def create_node(left, right):
    value = b"".join([NODE, left, right])
    hash = digest(value)
    return (hash, value)


def parse_node(data):
    return (data[1:33], data[33:])


def digest(data):
    # we have to create a new instance has hashlib doesn't
    # have a 'reset' for updates
    hasher = sha256()
    hasher.update(data)
    return hasher.digest()


def get_bit(index, data):
    if data[index >> 3] & 1 << (7 - index % 8) > 0:
        return 1
    else:
        return 0


def count_set_bits(data):
    count = 0
    for i in range(0, len(data) * 8):
        if get_bit(i, data) == 1:
            count += 1
    return count


def count_common_prefix(a, b):
    count = 0
    for i in range(0, len(a) * 8):
        if get_bit(i, a) == get_bit(i, b):
            count += 1
        else:
            return count
    return count


# lil helper
def show_bits(value):
    x = [bin(byte) for byte in value]
    return "{}".format(x)


def big_test(tree, size):
    import secrets

    for i in range(size):
        k = secrets.token_bytes(10)
        v = bytes("hello{}".format(i), "utf-8")
        tree.update(k, v)
