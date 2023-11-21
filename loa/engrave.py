MIN_ENGRAVE_LEVEL = 3
MAX_ENGRAVE_LEVEL = 6
ACTIVE_ENGRAVE_LEVEL = 5
LIMIT_ENGRAVE_LEVEL = ACTIVE_ENGRAVE_LEVEL * 3
MAX_ACC_COUNT = 5

import copy

GOAL = {
    'A': 15,
    'B': 15,
    'C': 15,
    'D': 15,
    'E': 15,
    'F': 10
}

BASE = {
    'A': 12,
    'B': 12,
    'C': 9,
    'F': 7
}

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
    computed = set()
    visit = set()
    engrave_range = [0, *range(MIN_ENGRAVE_LEVEL, MAX_ENGRAVE_LEVEL+1)]

    queue = [[based]]
    while queue:
        current = queue.pop(0)
        if hash(current[1:]) in visit:
            continue

        subs = subtract(goal, merge(*current))
        computed_key = hash(subs)
        if computed_key in computed:
            continue

        required_point = sum(subs.values())
        if required_point == 0:
            visit.add(hash(current[1:]))
            yield current[1:]
            continue

        maximum_point = (MAX_ENGRAVE_LEVEL+MIN_ENGRAVE_LEVEL)*((MAX_ACC_COUNT+1)-len(current))
        if required_point > maximum_point:
            continue

        chance = (MAX_ACC_COUNT+1) - len(current)
        if not possible(subs, chance):
            continue

        computed.add(computed_key)
        keys = list(subs.keys())
        if len(keys) > 1:
            for k1, k2 in ((k1, k2) for k2 in keys for k1 in keys if k2 is not k1):
                for i in engrave_range:
                    opts = {k1:MIN_ENGRAVE_LEVEL, k2:i}
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
    for comb in combination(GOAL, BASE):
        pool.append(comb)
        print(comb)

    limits = search_pool(pool)
    if not limits:
        print('impossible')
        exit(0)
    
    print('search api')
    for k, v in limits.items():
        print(v)