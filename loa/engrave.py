import copy


goal = {
    'A': 15,
    'B': 15,
    'C': 15,
    'D': 15,
    'E': 15,
    # 'F': 10
}

based = {
    'A': 12,
    'B': 12,
    'C': 9,
    'F': 7
}

MAX_VAL = 6
ACC_TYPE = {
    'neck': 0,
    'ear1': 1,
    'ear2': 2,
    'ring1': 3,
    'ring4': 4
}

def a2i(k, v):
    return (ord(k) - ord('A')) * (MAX_VAL - 2) + (v - 3)

def index(k, v, acc, opt):
    return a2i(k, v) + ((a2i('F', MAX_VAL)+1)*(((4-acc)*2)+opt))

def subtract(data1, data2):
    result = copy.deepcopy(data1)
    for k, v in data2.items():
        if k in result:
            result[k] = max(0, result[k]- v)
            if not result[k]:
                del result[k]

    return result

def merge(*args):
    result = {}
    for data in args:
        for k, v in data.items():
            result[k] = min(15, result[k] + v if k in result else v)
    return result

def visit2tuple(*visit):
    return tuple([''.join([f'{k}{v}' for k, v in x.items()]) for x in visit])

def dict2tuple(val):
    return ''.join(f'{k}{v}' for k, v in val.items())

def search():
    visit_ear = set()
    visit_ring = set()
    visits = [set(), set(), set(), set(), set()]
    queue = [[based]]
    while queue:
        current = queue.pop(0)
        subs = subtract(goal, merge(*current))
        required_point = sum(subs.values())
        maximum_point = 9*(6-len(current))
        if required_point > maximum_point:
            continue
        
        acc_count = len(current) - 1
        if acc_count == 3:
            prev = dict2tuple(merge(*current[:2]))
            opt1 = dict2tuple(current[2])
            opt2 = dict2tuple(current[3])
            if (prev, opt2, opt1) in visit_ear:
                continue

            visit_ear.add((prev, opt1, opt2))
        elif acc_count == 5:
            prev = dict2tuple(merge(*current[:4]))
            opt1 = dict2tuple(current[4])
            opt2 = dict2tuple(current[5])
            if (prev, opt2, opt1) in visit_ring:
                continue

            visit_ring.add((prev, opt1, opt2))

            yield current[1:]
            continue

        keys = list(subs.keys())
        for k1 in keys:
            for k2 in (k for k in keys if k is not k1):
                for i in [0, 3, 4, 5, 6]:
                    opt1 = dict2tuple({k1:3})
                    opt2 = dict2tuple({k2:i})
                    if (opt2, opt1) in visits[acc_count]:
                        continue

                    visits[acc_count].add((opt1, opt2))
                    queue.append([*current, {k1:3, k2:i}])

if __name__ == '__main__':
    result = list(search())
    for x in result:
        print(x)

    print(len(result))