import copy
import datetime
import json
import api

MAX_ENGRAVE_LEVELS = {'유물': 5, '고대': 6}
MIN_ENGRAVE_LEVEL = 3
ACTIVE_ENGRAVE_LEVEL = 5
LIMIT_ENGRAVE_LEVEL = ACTIVE_ENGRAVE_LEVEL * 3
MAX_ACC_COUNT = 5
ACC_PARTS_MAP = {
    0: '목걸이',
    1: '귀걸이',
    2: '귀걸이',
    3: '반지',
    4: '반지'
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

def hash(val, sort=True):
    if type(val) is list:
        data = [hash(x, sort) for x in val]
        if sort:
            data = sorted(data)
        return ','.join(data)
    elif type(val) is dict:
        data = [f'{k}{v}' for k, v in val.items()]
        if sort:
            data = sorted(data)
        return ''.join(sorted(data))
    elif type(val) is str:
        return val
    else:
        raise Exception()

class combiner:
    def __init__(self):
        self.grade('고대')
        self.__goal = {}
        self.__preset = []
        self.__option = {}
        self.__engrave_combines = []
        self.__wear_combines = []
        self.__builder_list = []
        self.__items = {}
        self.__option = {
            '목걸이': [],
            '귀걸이': [],
            '반지': []
        }
        self.__search_option = {
            'ready_to_buy': True,
            'min_trade_count': 0,
            'allowed_penalty': []
        }

    def __distinct_acc_hash(self, engraves):
        if len(engraves) == MAX_ACC_COUNT:
            return ','.join([hash(engraves[0]), hash(engraves[1:3]), hash(engraves[3:5])])
        elif len(engraves) >= 3:
            return ','.join([hash(engraves[0]), hash(engraves[1:3]), hash(engraves[3:])])
        else:
            return hash(engraves, sort=False)
        
    def __possible(self, goal, count):
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
            goal[max_key] = max(0, goal[max_key] - self.MAX_ENGRAVE_LEVEL)
            if goal[max_key] == 0:
                del goal[max_key]
        
        return not goal
    
    def __calc_engrave_combine(self):
        visit1 = set()
        visit2 = set()
        queue = [(root, []) for root in self.__preset]

        while queue:
            root, accs = queue.pop()
            v_key = hash([root, *accs])
            if v_key in visit2:
                continue

            subs = subtract(self.__goal, merge(root, *accs))
            dp_key = hash([root, subs])
            if dp_key in visit1:
                continue

            if not subs:
                visit2.add(v_key)
                yield (root, accs)
                continue

            chance = MAX_ACC_COUNT+ - len(accs)
            if not self.__possible(subs, chance):
                visit2.add(v_key)
                continue

            visit1.add(dp_key)
            for option in self.__acc_option_combine(subs.keys()):
                queue.append((root, [*accs, option]))

    def __distinct(self, data):
        visit = set()
        for pair in (pair for _, combo in data for pair in combo):
            key = hash(pair)
            if key in visit:
                continue

            visit.add(key)
            yield pair

    def __builders(self):
        accessories = list(self.__distinct(self.__engrave_combines))
        if not accessories:
            raise Exception('impossible')

        for category, options in self.__option.items():
            visit = set()
            for option in options:
                key_e = json.dumps(option, ensure_ascii=False)
                if key_e in visit:
                    continue

                visit.add(key_e)
                for engraves in accessories:
                    builder = api.auction_builder()
                    builder.category(category)
                    builder.quality(option['quality'])
                    builder.grade(self.__grade)
                    for stat in option['stats']:
                        builder.stat(stat)
                    for k, v in engraves.items():
                        builder.engrave(k, v, v)
                    yield builder

    def __distinct_acc_hash(self, engraves):
        if len(engraves) == MAX_ACC_COUNT:
            return ','.join([hash(engraves[0]), hash(engraves[1:3]), hash(engraves[3:5])])
        elif len(engraves) >= 3:
            return ','.join([hash(engraves[0]), hash(engraves[1:3]), hash(engraves[3:])])
        else:
            return hash(engraves, sort=False)

    def __calc_wear_combine(self):
        queue = []
        visit = set()
        for root, case in self.__engrave_combines:
            for engraves in case:
                queue.append((root, [engraves]))
            
            while queue:
                root, current = queue.pop(0)
                key = hash([root, self.__distinct_acc_hash(current)])
                if key in visit:
                    continue

                visit.add(key)
                candidates = [engraves for engraves in case if engraves not in current]
                if not candidates:
                    yield (root, current)
                    continue

                for engraves in candidates:
                    queue.append((root, [*current, engraves]))

    def __matched_items(self, engrave, category):
        category_name = ACC_PARTS_MAP[category]
        slot = 1 if category in (2, 4) else 0
        key_e = hash(engrave)
        if key_e not in self.__items[category_name]:
            return []

        key_s = hash(self.__option[category_name][slot]['stats'])
        if key_s not in self.__items[category_name][key_e]:
            return []
        
        return self.__items[category_name][key_e][key_s]

    def __candidates(self, acc_case, root):
        queue = [[]]
        visit = set()
        result = {}
        while queue:
            current = queue.pop(0)
            candidates = [x for x in acc_case if x not in current]
            if not candidates:
                for category, engrave in enumerate(current):
                    category_name = ACC_PARTS_MAP[category]
                    slot = 1 if category in (2, 4) else 0
                    key_e = hash(engrave)
                    key_s = hash(self.__option[category_name][slot]['stats'])
                    acc_key = f'{category_name}{slot+1}' if category in (1, 2, 3, 4) else category_name
                    result[acc_key] = self.__items[category_name][key_e][key_s]
                continue

            current_key = self.__distinct_acc_hash(current)
            if current_key in visit:
                continue
            visit.add(current_key)

            category = len(current)
            if ACC_PARTS_MAP[category] not in self.__items:
                continue

            for engrave in candidates:
                if not self.__matched_items(engrave, category):
                    continue

                queue.append([*current, engrave])

        if len(result) < MAX_ACC_COUNT:
            return

        if any(not result[x] for x in result):
            return

        for neck, ear1, ear2, ring1, ring2 in ((neck, ear1, ear2, ring1, ring2) 
                                            for neck in result['목걸이'] 
                                            for ear1 in result['귀걸이1'] 
                                            for ear2 in result['귀걸이2'] 
                                            for ring1 in result['반지1'] 
                                            for ring2 in result['반지2']):

            if ear1 is ear2:
                continue

            if ring1 is ring2:
                continue

            complete = (neck, ear1, ear2, ring1, ring2)
            if any(x['trade count'] < self.__search_option['min_trade_count'] for x in complete):
                continue

            if self.__search_option['ready_to_buy'] and any(x['price'] is None for x in complete):
                continue

            penalty = merge(*[x['penalty'] for x in complete], {k:v for k, v in root.items() if k in api.PENALTY_MAP})
            if any(v >= ACTIVE_ENGRAVE_LEVEL for k, v in penalty.items() if k not in self.__search_option['allowed_penalty']):
                continue

            yield complete

    def __acc_option_combine(self, keys):
        result = []
        visit = set()
        if len(keys) > 1:
            for k1, k2 in ((k1, k2) for k1 in keys for k2 in keys if k2 is not k1):
                for opt1 in [0, 3]:
                    for opt2 in (0, *range(MIN_ENGRAVE_LEVEL, self.MAX_ENGRAVE_LEVEL+1)):
                        value = {k1: opt1, k2: opt2}
                        for k in [x for x in value.keys() if value[x] == 0]:
                            del value[k]
                        if not value:
                            continue
                        
                        key = hash(value)
                        if key in visit:
                            continue

                        visit.add(key)
                        result.append(value)
        else:
            for k1 in keys:
                for opt1 in range(MIN_ENGRAVE_LEVEL, self.MAX_ENGRAVE_LEVEL+1):
                    value = {k1: opt1}
                    key = hash(value)
                    if key in visit:
                        continue

                    visit.add(key)
                    result.append(value)
        return result
    
    def goal(self, value=None):
        if not value:
            return self.__goal
        else:
            self.__goal = value
            return self
    
    def preset(self, value=None):
        if not value:
            return self.__preset
        else:
            self.__preset.append(value)
            return self
        
    def option(self, category, value):
        if category not in self.__option:
            self.__option[category] = []

        self.__option[category].append(value)
        return self
    
    def grade(self, value):
        if value not in MAX_ENGRAVE_LEVELS:
            raise Exception(f'{value} : not support value')
        
        self.__grade = value
        self.MAX_ENGRAVE_LEVEL = MAX_ENGRAVE_LEVELS[value]
        self.ENGRAVE_LEVEL_RANGE = [0, *range(MIN_ENGRAVE_LEVEL, self.MAX_ENGRAVE_LEVEL+1)]

    def ready_to_buy(self, enabled):
        self.__search_option['ready_to_buy'] = enabled
        return self
    
    def min_trade_count(self, count):
        self.__search_option['min_trade_count'] = count
        return self
    
    def allow_penalty(self, engrave_name):
        if engrave_name not in self.__search_option['allowed_penalty']:
            self.__search_option['allowed_penalty'].append(engrave_name)
        return self

    def calculate(self):
        self.__engrave_combines = list(self.__calc_engrave_combine())
        self.__wear_combines = list(self.__calc_wear_combine())
        self.__builder_list = list(self.__builders())

        return len(self.__builder_list)

    def search(self, token):
        self.__items = {x:{} for x in api.CATEGORY_MAP}
        for builder in self.__builder_list:
            category = builder.category()
            search_result = []
            for item in builder.search(token):
                search_result.append(item)

                key_e = hash(item['engraves'])
                if key_e not in self.__items[category]:
                    self.__items[category][key_e] = {}

                key_s = hash(list(item['stats'].keys()))
                if key_s not in self.__items[category][key_e]:
                    self.__items[category][key_e][key_s] = []
                
                self.__items[category][key_e][key_s].append(item)
            
            yield search_result

    def candidate(self):
        for root, acc_case in self.__wear_combines:
            for x in ist.__candidates(acc_case, root):
                yield root, x

if __name__ == '__main__':
    ist = combiner()
    ist.goal({
        '원한': 15,
        '슈퍼 차지': 15,
        '분노의 망치': 15,
        '바리케이드': 15,
        '결투의 대가': 15,
        '저주받은 인형': 10
    })
    
    ist.preset({
        '분노의 망치': 12,
        '원한': 12,
        '바리케이드': 9,
        '저주받은 인형': 7,
        '방어력 감소': 1
    })
    ist.preset({
        '분노의 망치': 12,
        '슈퍼 차지': 12,
        '바리케이드': 9,
        '저주받은 인형': 7,
        '방어력 감소': 1
    })
    ist.preset({
        '분노의 망치': 12,
        '결투의 대가': 12,
        '바리케이드': 9,
        '저주받은 인형': 7,
        '방어력 감소': 1
    })

    ist.option('목걸이', {'quality': 100, 'stats': ['치명', '특화']})
    ist.option('귀걸이', {'quality': 100, 'stats': ['특화']})
    ist.option('귀걸이', {'quality': 100, 'stats': ['치명']})
    ist.option('반지', {'quality': 100, 'stats': ['특화']})
    ist.option('반지', {'quality': 100, 'stats': ['치명']})
    ist.ready_to_buy(True)
    ist.min_trade_count(0)
    ist.allow_penalty('방어력 감소')

    token = 'Enter your lost ark api key'
    begin = datetime.datetime.now()
    try:
        count = ist.calculate()
        progress = 0
        for items in ist.search(token):
            progress = progress + 1
            print(f'Request to loa api : {progress}/{count}')

        for root, combination in ist.candidate():
            print(combination)

    except Exception as e:
        print(str(e))

    end = datetime.datetime.now()
    print(end - begin)