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
    for _ in range(count):
        if not goal:
            return True
        
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
    
    return not goal

def combination(goal, based):
    dp = set()
    visit = set()

    queue = [[x] for x in based]
    while queue:
        current = queue.pop(0)
        if hash(current) in visit:
            continue

        subs = subtract(goal, merge(*current))
        dp_key = hash([current[0], subs])
        if dp_key in dp:
            continue

        required_point = sum(subs.values())
        if required_point == 0:
            visit.add(hash(current))
            yield current
            continue

        maximum_point = (MAX_ENGRAVE_LEVEL+MIN_ENGRAVE_LEVEL)*((MAX_ACC_COUNT+1)-len(current))
        if required_point > maximum_point:
            visit.add(hash(current))
            continue

        chance = (MAX_ACC_COUNT+1) - len(current)
        if not possible(subs, chance):
            visit.add(hash(current))
            continue

        dp.add(dp_key)
        keys = list(subs.keys())
        if len(keys) > 1:
            for k1, k2 in ((k1, k2) for k1 in keys for k2 in keys if k2 is not k1):
                for opt2_level in ENGRAVE_LEVEL_RANGE:
                    opts = {k1:MIN_ENGRAVE_LEVEL, k2:opt2_level}
                    if opts[k2] == 0:
                        del opts[k2]

                    case = [*current, opts]
                    queue.append(case)
        else:
            opts = {keys[0]:MIN_ENGRAVE_LEVEL}
            case = [*current, opts]
            queue.append(case)

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
    for comb in combination(GOAL, BASE):
        pool.append(comb[1:])
        print(comb)
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