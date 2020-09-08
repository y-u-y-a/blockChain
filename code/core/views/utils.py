import hashlib, collections

# target：convert block to hash

# (to use even if random order)
def sorted_dict_by_key(unsorted_dict):
    return collections.OrderedDict(
        sorted(unsorted_dict.items(), key=lambda d:d[0]))

# generate hash with sha256
print(hashlib.sha256('test'.encode()).hexdigest())




# for display
def pprint(chains):
    for i, chain in enumerate(chains):
        print(f"{'='*25} Chain {i} {'='*25}")
        # display key and value
        for k, v in chain.items():
            if k == 'transactions':
                print(k)
                for d in v:
                    print(f"{'-'*40}")
                    for kk, vv in d.items():
                        print(f'{kk:30}{vv}')
            else:
                # k:15は幅揃え
                print(f'{k:15}{v}')

    print(f"{'*'*25}")
