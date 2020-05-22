
def chunk_list(ls, n):
    for i in range(0, len(ls), n):
        yield ls[i: i + n]