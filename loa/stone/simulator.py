import math
import pickle
import os
import random
import loa.stone.const
from loa.stone.const import FIRST_LINE, SECOND_LINE, THIRD_LINE, SUCCESS, FAILED, MAX_LINE

class simulator:
    def __init__(self, target, rating):
        self.__callback_conf = loa.stone.const.callback_conf[target]
        self.__stone_conf = loa.stone.const.rating_conf[rating]
        self.__file_name = f"cache_{target}_{rating}"
        self.__cache = {}

        if os.path.exists(self.__file_name):
            with open(self.__file_name, 'rb') as f:
                self.__cache = pickle.load(f)

    def __del__(self):
        with open(self.__file_name, 'wb') as f:
            pickle.dump(self.__cache, f)

    def is_success(self, state):
        return self.__callback_conf['success'](self.__stone_conf, state)

    def is_failed(self, state):
        return self.__callback_conf['failed'](self.__stone_conf, state)

    def fn(self, prob, selection, state):
        """ 주어진 상황에서 선택했을 때 최종적으로 목표에 달성할 수 있는 확률을 구함
        :param prob: 현재 확률 (1.0 = 100%)
        :param selection: 선택지 (loa.stone.const.FIRST, loa.stone.const.SECOND, loa.stone.const.THIRD)
        :param state: [(첫째줄성공횟수, 첫째줄실패횟수), (둘째줄성공횟수, 둘째줄실패횟수), (셋째줄성공횟수, 셋째줄실패횟수)]
        :return: 주어진 상황에서의 최종목표 달성 확률
        """
        must_failed = (selection == THIRD_LINE)
        step = sum(success+failed for success, failed in state)
        key = f"{step}_{round(prob*100)}_{selection}/{'_'.join(f'{success}_{failed}' for success, failed in state)}"
        if key in self.__cache:
            return self.__cache[key]

        if self.__callback_conf['success'](self.__stone_conf, state):
            self.__cache[key] = 1
            return self.__cache[key]

        if self.__callback_conf['failed'](self.__stone_conf, state):
            self.__cache[key] = 0
            return self.__cache[key]
        
        if (sum(state[selection]) >= self.__stone_conf['chance']):
            self.__cache[key] = 0
            return self.__cache[key]
        
        next_states = [
            [loa.stone.const.next_state(x, True) if i == selection else x for i, x in enumerate(state)],
            [loa.stone.const.next_state(x, False) if i == selection else x for i, x in enumerate(state)]
        ]
        
        heuristic_prob = prob if not must_failed else 1.0 - prob
        next_state = (next_states[FAILED] if must_failed else next_states[SUCCESS], next_states[FAILED] if not must_failed else next_states[SUCCESS])

        basic_prob = heuristic_prob * max(self.fn(loa.stone.const.next_prob(prob, not must_failed), i, next_state[SUCCESS]) for i in range(MAX_LINE))
        additional_prob = (1.0 - heuristic_prob) * max(self.fn(loa.stone.const.next_prob(prob, must_failed), i, next_state[FAILED]) for i in range(MAX_LINE))

        self.__cache[key] = basic_prob + additional_prob
        return self.__cache[key]

    def simulate(self, callback=None):
        """ 어빌리티스톤을 세공함
        :param callback: 한번 눌렀을 때 호출될 콜백함수
        :return: (목표달성여부, 최종결과)
        """
        current_prob = loa.stone.const.MAX_PROB
        state = [(0, 0), (0, 0), (0, 0)]

        while True:
            probs = []
            for selection in range(MAX_LINE):
                probs.append(self.fn(current_prob, selection, state))

            final_prob = max(*probs)
            selection = random.choice([i for i, x in enumerate(probs) if x == final_prob])
            success = random.randrange(100) < math.ceil(current_prob * 100)
            next_prob = loa.stone.const.next_prob(current_prob, success)
            state[selection] = loa.stone.const.next_state(state[selection], success)

            history = {
                'current prob': current_prob,
                'selection': selection,
                'final prob': final_prob,
                'result': [x for x in state]
            }

            if self.is_success(state):
                yield True, history
                break

            elif self.is_failed(state):
                yield False, history
                break

            else:
                yield None, history
            
            current_prob = next_prob