#-*- coding:utf-8 -*-

import copy
import datetime
import requests
import json
import time

token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJSUzI1NiIsIng1dCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyIsImtpZCI6IktYMk40TkRDSTJ5NTA5NWpjTWk5TllqY2lyZyJ9.eyJpc3MiOiJodHRwczovL2x1ZHkuZ2FtZS5vbnN0b3ZlLmNvbSIsImF1ZCI6Imh0dHBzOi8vbHVkeS5nYW1lLm9uc3RvdmUuY29tL3Jlc291cmNlcyIsImNsaWVudF9pZCI6IjEwMDAwMDAwMDAwMDA1NDUifQ.dnipWNKCIi7KEunsyXwNiyYNXh4xaNjAWwWXCEuMt1y9Z0yQXSLlE3T7pecajCjJsF_TpgSaX0eoZk7Atyk_iuAIhGkDfH0ygaVWQ37RnhabgoS3jJodc-WWTDHo9nuLVgD7dKVA0SUeu9zMBaj2Ery9a_uwdxJHUeWTSwBkCAzWIixvSOdEQhg_zoUHQNY_q5Wl8O2WvS06CkWTTaPBes5PVEq95SVpQGMx5z0-LFtUVXhRueIkUPjiUyAI44IQrqzE6mR2HIAAllV8qTQNZgkL2yT_6mGvs4ah05ucvHOa5c0oz0Lu3Bv8KXrS2vcCEZOtnKr5UiXZ7l3BHbtBgA'

MIN_ENGRAVE_LEVEL = 3
MAX_ENGRAVE_LEVEL = 6
ACTIVE_ENGRAVE_LEVEL = 5
LIMIT_ENGRAVE_LEVEL = ACTIVE_ENGRAVE_LEVEL * 3
MAX_ACC_COUNT = 5
ENGRAVE_LEVEL_RANGE = [0, *range(MIN_ENGRAVE_LEVEL, MAX_ENGRAVE_LEVEL+1)]

ENGRAVE_MAP = { '각성': 255, '갈증': 286, '강령술': 243, '강화 무기': 129, '강화 방패': 242, '결투의 대가': 288, '고독한 기사': 225, '공격력 감소': 800, '공격속도 감소': 802, '광기': 125, '광전사의 비기': 188, '구슬동자': 134, '굳은 의지': 123, '그믐의 경계': 312, '극의: 체술': 190, '급소 타격': 142, '기습의 대가': 249, '긴급구조': 302, '넘치는 교감': 199, '달의 소리': 287, '달인의 저력': 238, '돌격대장': 254, '두 번째 동료': 258, '마나 효율 증가': 168, '마나의 흐름': 251, '만개': 306, '만월의 집행자': 311, '멈출 수 없는 충동': 281, '바리케이드': 253, '방어력 감소': 801, '버스트': 279, '번개의 분노': 246, '부러진 뼈': 245, '분노의 망치': 196, '분쇄의 주먹': 236, '불굴': 235, '사냥의 시간': 290, '상급 소환사': 198, '선수필승': 244, '세맥타통': 256, '속전속결': 300, '슈퍼 차지': 121, '승부사': 248, '시선 집중': 298, '실드 관통': 237, '심판자': 282, '아드레날린': 299, '아르데타인의 기술': 284, '안정된 상태': 111, '약자 무시': 107, '에테르 포식자': 110, '여신의 가호': 239, '역천지체': 257, '예리한 둔기': 141, '오의 강화': 127, '오의난무': 292, '완벽한 억제': 280, '원한': 118, '위기 모면': 140, '이동속도 감소': 803, '이슬비': 308, '일격필살': 291, '잔재된 기운': 278, '저주받은 인형': 247, '전문의': 301, '전투 태세': 224, '절실한 구원': 195, '절정': 276, '절제': 277, '점화': 293, '정기 흡수': 109, '정밀 단도': 303, '죽음의 습격': 259, '중갑 착용': 240, '중력 수련': 197, '진실된 용맹': 194, '진화의 유산': 285, '질량 증가': 295, '질풍노도': 307, '처단자': 310, '초심': 189, '최대 마나 증가': 167, '추진력': 296, '축복의 오라': 283, '충격 단련': 191, '타격의 대가': 297, '탈출의 명수': 202, '포격 강화': 193, '포식자': 309, '폭발물 전문가': 241, '피스메이커': 289, '핸드거너': 192, '화력 강화': 130, '환류': 294, '황제의 칙령': 201, '황후의 은총': 200, '회귀': 305 }
PENALTY_MAP = { '공격력 감소': 800, '공격속도 감소': 802, '방어력 감소': 801, '이동속도 감소': 803 }
STAT_MAP = { '치명': 15, '특화': 16, '제압': 17, '신속': 18, '인내': 19, '숙련': 20 }
CATEGORY_MAP = { '목걸이': 200010, '귀걸이': 200020, '반지': 200030 }

GOAL = {
    '원한': 15,
    '슈퍼 차지': 15,
    '분노의 망치': 15,
    '바리케이드': 15,
    '결투의 대가': 15,
    '저주받은 인형': 10
}

BASE = [
    {
        '분노의 망치': 12,
        '원한': 12,
        '바리케이드': 9,
        '저주받은 인형': 7,
        '방어력 감소': 1
    },
    {
        '분노의 망치': 12,
        '슈퍼 차지': 12,
        '바리케이드': 9,
        '저주받은 인형': 7,
        '방어력 감소': 1
    },
    {
        '분노의 망치': 12,
        '결투의 대가': 12,
        '바리케이드': 9,
        '저주받은 인형': 7,
        '방어력 감소': 1
    }
]

ACC_OPTIONS = {
    '목걸이': [{'quality': 100, 'stats': ['치명', '특화']}],
    '귀걸이': [{'quality': 100, 'stats': ['특화']}, {'quality': 100, 'stats': ['치명']}],
    '반지': [{'quality': 100, 'stats': ['특화']}, {'quality': 100, 'stats': ['치명']}]
}

ACC_PARTS_MAP = {
    0: '목걸이',
    1: '귀걸이',
    2: '귀걸이',
    3: '반지',
    4: '반지'
}

SEARCH_OPTIONS = {
    'ready_to_buy': True,
    'trade_allow_count': 0,
    'allowed_penalty': []
}

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
    cache_key = ''.join(sorted(keys))
    if cache_key in cache_option:
        return cache_option[cache_key]

    cache_option[cache_key] = []
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
                    cache_option[cache_key].append(value)
    else:
        for k1 in keys:
            for opt1 in range(MIN_ENGRAVE_LEVEL, MAX_ENGRAVE_LEVEL+1):
                value = {k1: opt1}
                key = hash(value)
                if key in visit:
                    continue

                visit.add(key)
                cache_option[cache_key].append(value)
    return cache_option[cache_key]

def engrave_combination(goal, based):
    visit1 = set()
    visit2 = set()
    queue = [(root, []) for root in based]

    while queue:
        root, accs = queue.pop()
        v_key = hash([root, *accs])
        if v_key in visit2:
            continue

        subs = subtract(goal, merge(root, *accs))
        dp_key = hash([root, subs])
        if dp_key in visit1:
            continue

        if not subs:
            visit2.add(v_key)
            yield (root, accs)
            continue

        chance = MAX_ACC_COUNT+ - len(accs)
        if not possible(subs, chance):
            visit2.add(v_key)
            continue

        visit1.add(dp_key)
        for option in acc_option_combine(subs.keys()):
            queue.append((root, [*accs, option]))

def distinct(data):
    visit = set()
    for pair in (pair for _, combo in data for pair in combo):
        key = hash(pair)
        if key in visit:
            continue

        visit.add(key)
        yield pair

def search_params(engrave_combination, acc_options):
    accessories = list(distinct(engrave_combination))
    if not accessories:
        raise Exception('impossible')

    for category, options in acc_options.items():
        visit = set()
        for option in options:
            key_e = json.dumps(option, ensure_ascii=False)
            if key_e in visit:
                continue

            visit.add(key_e)
            for engraves in accessories:
                yield category, loa_api_body(category, option, engraves)

def search(search_params):
    for category, params in search_params:
        while True:
            response = requests.post("https://developer-lostark.game.onstove.com/auctions/items", json=params, headers={'Authorization': f'Bearer {token}'})
            data = response.json()
            if data is None:
                time.sleep(1)
            else:
                break

        if not data['Items']:
            yield category, []
            continue

        result = []
        for item in data['Items']:
            engraves = {}
            stats = {}
            penalty = None
            for option in item['Options']:
                if option['Type'] == 'STAT':
                    stats[option['OptionName']] = option['Value']
                elif option['Type'] == 'ABILITY_ENGRAVE':
                    if not option['IsPenalty']:
                        engraves[option['OptionName']] = option['Value']
                    else:
                        penalty = {option['OptionName']: option['Value']}
            
            result.append({
                'name': item['Name'],
                'quality': item['GradeQuality'],
                'price': item['AuctionInfo']['BuyPrice'],
                'trade count': item['AuctionInfo']['TradeAllowCount'],
                'stats': stats,
                'engraves': engraves,
                'penalty': penalty
            })

        yield category, result

def loa_api_body(category, option, engraves):
    etc = []
    for k, v in engraves.items():
        etc.append({
            "FirstOption": 3,
            "SecondOption": ENGRAVE_MAP[k],
            "MinValue": v,
            "MaxValue": v
        })
    
    for v in option['stats']:
        etc.append({
            "FirstOption": 2,
            "SecondOption": STAT_MAP[v],
            "MinValue": None,
            "MaxValue": None
        })

    return {
        "ItemLevelMin": 0,
        "ItemLevelMax": 0,
        "ItemGradeQuality": option['quality'],
        "SkillOptions": [
            {
            "FirstOption": None,
            "SecondOption": None,
            "MinValue": None,
            "MaxValue": None
            }
        ],
        "EtcOptions": etc,
        "Sort": "BUY_PRICE",
        "CategoryCode": CATEGORY_MAP[category],
        "CharacterClass": None,
        "ItemTier": 3,
        "ItemGrade": "고대" if MAX_ENGRAVE_LEVEL == 6 else "유물",
        "ItemName": None,
        "PageNo": 1,
        "SortCondition": "ASC"
    }

def distinct_acc_hash(engraves):
    if len(engraves) == MAX_ACC_COUNT:
        return ','.join([hash(engraves[0]), hash(engraves[1:3]), hash(engraves[3:5])])
    elif len(engraves) >= 3:
        return ','.join([hash(engraves[0]), hash(engraves[1:3]), hash(engraves[3:])])
    else:
        return hash(engraves, sort=False)

def accessory_combination(engrave_combination):
    queue = []
    visit = set()
    for root, case in engrave_combination:
        for engraves in case:
            queue.append((root, [engraves]))
        
        while queue:
            root, current = queue.pop(0)
            key = hash([root, distinct_acc_hash(current)])
            if key in visit:
                continue

            visit.add(key)
            if len(current) == MAX_ACC_COUNT:
                yield (root, current)
                continue

            for engraves in case:
                if engraves in current:
                    continue

                queue.append((root, [*current, engraves]))

def matched_items(items, engrave, category):
    category_name = ACC_PARTS_MAP[category]
    slot = 1 if category in (2, 4) else 0
    key_e = hash(engrave)
    if key_e not in items[category_name]:
        return []

    key_s = hash(ACC_OPTIONS[category_name][slot]['stats'])
    if key_s not in items[category_name][key_e]:
        return []
    
    return items[category_name][key_e][key_s]

def candidates(combination, items, root, options):
    queue = [[]]
    visit = set()
    result = {}
    while queue:
        current = queue.pop(0)
        candidates = [x for x in combination if x not in current]
        if not candidates:
            for category, engrave in enumerate(current):
                category_name = ACC_PARTS_MAP[category]
                slot = 1 if category in (2, 4) else 0
                key_e = hash(engrave)
                key_s = hash(ACC_OPTIONS[category_name][slot]['stats'])
                acc_key = f'{category_name}{slot+1}' if category in (1, 2, 3, 4) else category_name
                result[acc_key] = items[category_name][key_e][key_s]
            continue

        current_key = distinct_acc_hash(current)
        if current_key in visit:
            continue
        visit.add(current_key)

        category = len(current)
        if ACC_PARTS_MAP[category] not in items:
            continue

        for engrave in candidates:
            if not matched_items(items, engrave, category):
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
        if any(x['trade count'] < options['trade_allow_count'] for x in complete):
            continue

        if options['ready_to_buy'] and any(x['price'] is None for x in complete):
            continue

        penalty = merge(*[x['penalty'] for x in complete], {k:v for k, v in root.items() if k in PENALTY_MAP})
        if any(v >= ACTIVE_ENGRAVE_LEVEL for k, v in penalty.items() if k not in options['allowed_penalty']):
            continue

        yield complete
    

if __name__ == '__main__':
    begin = datetime.datetime.now()
    combination_e = list(engrave_combination(GOAL, BASE))
    combination_a = list(accessory_combination(combination_e))
    
    params = list(search_params(combination_e, ACC_OPTIONS))
    progress = 0
    items = {x:{} for x in CATEGORY_MAP}
    for category, search_result in search(params):
        for item in search_result:
            key_e = hash(item['engraves'])
            if key_e not in items[category]:
                items[category][key_e] = {}

            key_s = hash(list(item['stats'].keys()))
            if key_s not in items[category][key_e]:
                items[category][key_e][key_s] = []
            
            items[category][key_e][key_s].append(item)

        progress = progress + 1
        print(f'Request to loa api : {progress}/{len(params)}')

    result = []
    for root, combination in combination_a:
        for x in candidates(combination, items, root, SEARCH_OPTIONS):
            print(x)

    end = datetime.datetime.now()
    elapsed = end - begin
    print(elapsed)