SUCCESS             = 0  # 성공 인덱스
FAILED              = 1  # 실패 인덱스
FIRST_LINE          = 0  # 첫번째 라인 인덱스
SECOND_LINE         = 1  # 두번째 라인 인덱스
THIRD_LINE          = 2  # 세번째 라인 인덱스
MAX_LINE            = 3
MAX_PROB            = 0.75
MIN_PROB            = 0.25
DIFF_PROB           = 0.10

def next_prob(current_prob, success):
    if success:
        return max(MIN_PROB, current_prob - DIFF_PROB)

    else:
        return min(MAX_PROB, current_prob + DIFF_PROB)

def next_state(current_state, success):
    if success:
        return (current_state[SUCCESS]+1, current_state[FAILED])
    else:
        return (current_state[SUCCESS], current_state[FAILED]+1)

def expect_value(stone_conf, state_line):
    return stone_conf['chance'] - state_line[FAILED]

def is_base_success(stone_conf, state, min_success):
    no_debuff = (expect_value(stone_conf, state[THIRD_LINE]) <= 4)
    activated = (state[FIRST_LINE][SUCCESS] + state[SECOND_LINE][SUCCESS] >= min_success)

    return no_debuff and activated

def is_success_97(stone_conf, state):
    if not is_base_success(stone_conf, state, 16):
        return False

    validated = not (state[FIRST_LINE][SUCCESS] <= 8 and state[SECOND_LINE][SUCCESS] <= 8)
    if not validated:
        return False

    return True

def is_success_77(stone_conf, state):
    if not is_base_success(stone_conf, state, 14):
        return False

    validated = not ((state[FIRST_LINE][SUCCESS] <= 6 and state[SECOND_LINE][SUCCESS] <= 8) or (state[SECOND_LINE][SUCCESS] <= 6 and state[FIRST_LINE][SUCCESS] <= 8))
    if not validated:
        return False

    return True

def is_base_failed(stone_conf, state, amount_success):
    active_debuff = (state[THIRD_LINE][SUCCESS] >= 5)
    if active_debuff:
        return True
    
    best_success = expect_value(stone_conf, state[FIRST_LINE]) + expect_value(stone_conf, state[SECOND_LINE])
    if best_success < amount_success:
        return True
    
    return False

def is_failed_97(stone_conf, state):
    if is_base_failed(stone_conf, state, 16):
        return True

    if expect_value(stone_conf, state[FIRST_LINE]) <= 8 and expect_value(stone_conf, state[SECOND_LINE]) <= 8:
        return True

    return False

def is_failed_77(stone_conf, state):
    if is_base_failed(stone_conf, state, 14):
        return True

    if expect_value(stone_conf, state[FIRST_LINE]) <= 6 and expect_value(stone_conf, state[SECOND_LINE]) <= 8:
        return True
    
    if expect_value(stone_conf, state[FIRST_LINE]) <= 8 and expect_value(stone_conf, state[SECOND_LINE]) <= 6:
        return True
    
    return False

def is_success_99(stone_conf, state):
    if not is_base_success(stone_conf, state, 18):
        return False

    return True


def is_failed_99(stone_conf, state):
    if is_base_failed(stone_conf, state, 18):
        return True

    if expect_value(stone_conf, state[FIRST_LINE]) <= 10 and expect_value(stone_conf, state[SECOND_LINE]) <= 8:
        return True

    if expect_value(stone_conf, state[FIRST_LINE]) <= 8 and expect_value(stone_conf, state[SECOND_LINE]) <= 10:
        return True

    return False

callback_conf = {
    '97': {
        'success': is_success_97,
        'failed': is_failed_97
    },
    '77': {
        'success': is_success_77,
        'failed': is_failed_77
    },
    '99': {
        'success': is_success_99,
        'failed': is_failed_99
    }
}
rating_conf = {
    'rare': {'chance': 6 },
    'epic': {'chance': 8 },
    'legendary': {'chance': 9, 'pheon': 5 },
    'relic': {'chance': 10, 'pheon': 9 }
}