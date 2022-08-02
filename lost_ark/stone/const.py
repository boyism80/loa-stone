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

def expect_value(stone_conf, success, failed):
    return success + (stone_conf['chance'] - (success + failed))

def is_success_97(stone_conf, state):
    no_debuff = (expect_value(stone_conf, *state[THIRD_LINE]) <= 4)
    activated = (state[FIRST_LINE][SUCCESS] + state[SECOND_LINE][SUCCESS] >= 16)
    validated = not (state[FIRST_LINE][SUCCESS] <= 8 and state[SECOND_LINE][SUCCESS] <= 8)
    return no_debuff and activated and validated

def is_success_77(stone_conf, state):
    no_debuff = (expect_value(stone_conf, *state[THIRD_LINE]) <= 4)
    activated = (state[FIRST_LINE][SUCCESS] + state[SECOND_LINE][SUCCESS] >= 14)
    validated = not ((state[FIRST_LINE][SUCCESS] <= 6 and state[SECOND_LINE][SUCCESS] <= 8) or (state[SECOND_LINE][SUCCESS] <= 6 and state[FIRST_LINE][SUCCESS] <= 8))
    return no_debuff and activated and validated

def is_failed_97(stone_conf, state):
    active_debuff = (state[THIRD_LINE][SUCCESS] >= 5)
    if active_debuff:
        return True

    failed_count = (state[FIRST_LINE][FAILED] + state[SECOND_LINE][FAILED])
    if failed_count > (stone_conf['chance'] - 8) * 2:
        return True

    if expect_value(stone_conf, *state[FIRST_LINE]) <= 8 and expect_value(stone_conf, *state[SECOND_LINE]) <= 8:
        return True
    
    return False

def is_failed_77(stone_conf, state):
    active_debuff = (state[THIRD_LINE][SUCCESS] >= 5)
    if active_debuff:
        return True

    failed_count = (state[FIRST_LINE][FAILED] + state[SECOND_LINE][FAILED])
    if failed_count > (stone_conf['chance'] - 7) * 2:
        return True

    if expect_value(stone_conf, *state[FIRST_LINE]) <= 6 and expect_value(stone_conf, *state[SECOND_LINE]) <= 8:
        return True
    
    if expect_value(stone_conf, *state[FIRST_LINE]) <= 8 and expect_value(stone_conf, *state[SECOND_LINE]) <= 6:
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
    }
}
rating_conf = {
    'rare': {'chance': 6 },
    'epic': {'chance': 8 },
    'legendary': {'chance': 9 },
    'relic': {'chance': 10 }
}