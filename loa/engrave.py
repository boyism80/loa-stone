import copy
import datetime

MIN_ENGRAVE_LEVEL = 3
MAX_ENGRAVE_LEVEL = 6
ACTIVE_ENGRAVE_LEVEL = 5
LIMIT_ENGRAVE_LEVEL = ACTIVE_ENGRAVE_LEVEL * 3
MAX_ACC_COUNT = 5
ENGRAVE_LEVEL_RANGE = [0, *range(MIN_ENGRAVE_LEVEL, MAX_ENGRAVE_LEVEL+1)]

GOAL = {
    'A': 15,
    'B': 15,
    'C': 15,
    'D': 15,
    'E': 15,
    'F': 5
}

BASE = [
    {
        'A': 12,
        'B': 12,
        'C': 9,
        'F': 7
    },
    {
        'A': 12,
        'B': 12,
        'D': 9,
        'F': 7
    },
    {
        'A': 12,
        'B': 12,
        'E': 9,
        'F': 7
    }
]

cache_option = {}
cache_possible = {}

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
            result[k] = min(LIMIT_ENGRAVE_LEVEL, result[k] + v if k in result else v)
    return result

def hash(val):
    if type(val) is list:
        return ','.join(sorted([hash(x) for x in val]))
    elif type(val) is dict:
        return ''.join(sorted([f'{k}{v}' for k, v in val.items()]))
    else:
        raise Exception()

def possible(goal, count):
    goal = copy.deepcopy(goal)
    key = f"{hash(goal)}{count}"
    if key in cache_possible:
        return cache_possible[key]
    
    for _ in range(count):
        if not goal:
            cache_possible[key] = True
            return cache_possible[key]
        
        min_key = min(goal, key=goal.get)
        goal[min_key] = max(0, goal[min_key] - MIN_ENGRAVE_LEVEL)
        if goal[min_key] == 0:
            del goal[min_key]

        if not goal:
            return True
        
        max_key = max(goal, key=goal.get)
        goal[max_key] = max(0, goal[max_key] - MAX_ENGRAVE_LEVEL)
        if goal[max_key] == 0:
            del goal[max_key]
    
    cache_possible[key] = not goal
    return cache_possible[key]

def acc_option_combine(keys):
    key = ''.join(sorted(keys))
    if key in cache_option:
        return cache_option[key]

    cache_option[key] = []
    visit = set()
    if len(keys) > 1:
        for k1, k2 in ((k1, k2) for k1 in keys for k2 in keys if k2 is not k1):
            for opt1 in [0, 3]:
                for opt2 in (0, *range(MIN_ENGRAVE_LEVEL, MAX_ENGRAVE_LEVEL+1)):
                    value = {k1: opt1, k2: opt2}
                    for k in [x for x in value.keys() if value[x] == 0]:
                        del value[k]
                    if not value:
                        continue
                    
                    key = hash(value)
                    if key in visit:
                        continue

                    visit.add(key)
                    cache_option[key].append(value)
    else:
        for k1 in keys:
            for opt1 in range(MIN_ENGRAVE_LEVEL, MAX_ENGRAVE_LEVEL+1):
                value = {k1: opt1}
                key = hash(value)
                if key in visit:
                    continue

                visit.add(key)
                cache_option[key].append(value)
    return cache_option[key]

def combination(goal, based):
    visit = set()
    queue = [(root, []) for root in based]

    while queue:
        root, accs = queue.pop(0)
        v_key = hash([root, *accs])
        if v_key in visit:
            continue

        subs = subtract(goal, merge(root, *accs))
        dp_key = hash([root, subs])
        if dp_key in visit:
            continue

        if not subs:
            visit.add(v_key)
            yield (root, accs)
            continue

        chance = MAX_ACC_COUNT+ - len(accs)
        if not possible(subs, chance):
            visit.add(v_key)
            continue

        visit.add(dp_key)
        for option in acc_option_combine(subs.keys()):
            queue.append((root, [*accs, option]))

def search_pool(data):
    result = {}
    for comb in data:
        for pair in comb:
            key = ''.join(sorted(list(pair.keys())))
            if key not in result:
                result[key] = {}

            for k, v in pair.items():
                if k not in result[key]:
                    result[key][k] = {'min': v, 'max': v}
                else:
                    result[key][k]['min'] = min(result[key][k]['min'], v)
                    result[key][k]['max'] = max(result[key][k]['max'], v)

    return result


if __name__ == '__main__':
    pool = []
    begin = datetime.datetime.now()
    for root, current in combination(GOAL, BASE):
        pool.append(current)
        print(hash([root, *current]))
    end = datetime.datetime.now()
    elapsed = end - begin

    limits = search_pool(pool)
    if not limits:
        print('impossible')
        exit(0)
    
    print('search api')
    for k, v in limits.items():
        print(v)
    print(elapsed)