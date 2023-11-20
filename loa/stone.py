import array
import random
import math

settings = {
    '77': {
        'amount': 14,
        'except': [(8, 6), (6, 8)]
    },
    '97': {
        'amount': 16,
        'except': [(8, 8)]
    },
    '97_1st': {
        'amount': 16,
        'except': [(8, 8), (7, 9), (8, 9), (10, 6)]
    },
    '97_2nd': {
        'amount': 16,
        'except': [(8, 8), (9, 7), (9, 8), (6, 10)]
    }
}

stone_conf = {
    'rare': {'chance': 6 },
    'epic': {'chance': 8 },
    'legendary': {'chance': 9, 'pheon': 5 },
    'relic': {'chance': 10, 'pheon': 9, 'siling': 1680 }
}

success_probs = [0.25, 0.35, 0.45, 0.55, 0.65, 0.75]

class simulator:
    def __init__(self, target, rating):
        self.setting = settings[target]
        self.stone_conf = stone_conf[rating]
        self.init()

    def is_success(self, state):
        success_amount = state[0]['success'] + state[1]['success']
        if success_amount < self.setting['amount']:
            return False
        
        if (state[0]['success'], state[1]['success']) in self.setting['except']:
            return False
        
        chance = self.stone_conf['chance']
        chance_3rd = chance - (state[2]['success'] + state[2]['failed'])
        if state[2]['success'] + chance_3rd > 4:
            return False
        
        return True

    def is_failed(self, state):
        if state[2]['success'] > 4:
            return True
        
        best_1st = self.stone_conf['chance'] - state[0]['failed']
        best_2nd = self.stone_conf['chance'] - state[1]['failed']

        if best_1st + best_2nd < self.setting['amount']:
            return True

        if (best_1st, best_2nd) in self.setting['except']:
            return True

        return False

    def result(self, state):
        if self.is_success(state):
            return True

        if self.is_failed(state):
            return False
        
        return None

    def index(self, prob_index, state):
        column = self.stone_conf['chance'] + 1
        dim1 = state[0]['success'] * column + state[0]['failed']
        dim2 = dim1 * column + state[1]['success']
        dim3 = dim2 * column + state[1]['failed']
        dim4 = dim3 * column + state[2]['success']
        dim5 = dim4 * column + state[2]['failed']
        return dim5 * len(success_probs) + prob_index

    def calculate_1(self, prob_index, state):
        chance = self.stone_conf['chance']
        chance_1st = chance - (state[0]['success'] + state[0]['failed'])
        if chance_1st == 0:
            return 0.0
        
        success = success_probs[prob_index] * self.cache[self.index(max(prob_index-1, 0), [
            {
                'success': min(state[0]['success'] + 1, chance),
                'failed': state[0]['failed']
            },
            state[1],
            state[2]
        ])]

        fail = (1.0 - success_probs[prob_index]) * self.cache[self.index(min(prob_index+1, len(success_probs)-1), [
            {
                'success': state[0]['success'],
                'failed': min(state[0]['failed'] + 1, chance)
            },
            state[1],
            state[2]
        ])]

        return success + fail

    def calculate_2(self, prob_index, state):
        chance = self.stone_conf['chance']
        chance_2nd = chance - (state[1]['success'] + state[1]['failed'])
        if chance_2nd == 0:
            return 0.0
        
        success = success_probs[prob_index] * self.cache[self.index(max(prob_index-1, 0), [
            state[0],
            {
                'success': min(state[1]['success'] + 1, chance),
                'failed': state[1]['failed']
            },
            state[2]
        ])]

        fail = (1.0 - success_probs[prob_index]) * self.cache[self.index(min(prob_index+1, len(success_probs)-1), [
            state[0],
            {
                'success': state[1]['success'],
                'failed': min(state[1]['failed'] + 1, chance)
            },
            state[2],
        ])]

        return success + fail

    def calculate_3(self, prob_index, state):
        chance = self.stone_conf['chance']
        chance_3rd = chance - (state[2]['success'] + state[2]['failed'])
        if chance_3rd == 0:
            return 0.0
        
        success = success_probs[prob_index] * self.cache[self.index(max(prob_index-1, 0), [
            state[0],
            state[1],
            {
                'success': min(state[2]['success'] + 1, chance),
                'failed': state[2]['failed']
            }
        ])]

        fail = (1.0 - success_probs[prob_index]) * self.cache[self.index(min(prob_index+1, len(success_probs)-1), [
            state[0],
            state[1],
            {
                'success': state[2]['success'],
                'failed': min(state[2]['failed'] + 1, chance)
            }
        ])]

        return success + fail

    def calculate(self, prob_index, state):
        yield self.calculate_1(prob_index, state)
        yield self.calculate_2(prob_index, state)
        yield self.calculate_3(prob_index, state)

    def stone_case_generator(self):
        chance = self.stone_conf['chance']
        return (([ {'success': success_1st, 'failed': failed_1st},{'success': success_2nd, 'failed': failed_2nd},{'success': success_3rd, 'failed': failed_3rd} ], prob_index)
        for success_1st in range(chance, -1, -1) 
        for failed_1st in range(chance - success_1st, -1, -1) 
        for success_2nd in range(chance, -1, -1) 
        for failed_2nd in range(chance - success_2nd, -1, -1) 
        for success_3rd in range(chance, -1, -1) 
        for failed_3rd in range(chance - success_3rd, -1, -1) 
        for prob_index in range(len(success_probs)))

    def init(self):
        size = (self.stone_conf['chance'] + 1) ** 6 * len(success_probs)
        self.cache = array.array('f', [0.0]*size)

        for state, prob_index in self.stone_case_generator():
            if self.is_success(state):
                prob = 1.0
            elif self.is_failed(state):
                prob = 0.0
            else:
                prob = max(self.calculate(prob_index, state))

            self.cache[self.index(prob_index, state)] = prob

    def simulate(self):
        current_percent_index = len(success_probs) - 1
        state = [{ 'success': 0, 'failed': 0 }, { 'success': 0, 'failed': 0 }, { 'success': 0, 'failed': 0 }]

        while True:
            current_probs = [column for column in self.calculate(current_percent_index, state)]
            final_prob = max(*current_probs)
            selection = random.choice([i for i, column in enumerate(current_probs) if column == final_prob])
            success = random.randrange(100) < math.ceil(success_probs[current_percent_index] * 100)
            next_percent_index = max(0, current_percent_index - 1) if success else min(len(success_probs)-1, current_percent_index + 1)
            state[selection] = {
                'success': state[selection]['success'] + 1 if success else state[selection]['success'],
                'failed': state[selection]['failed'] + 1 if not success else state[selection]['failed']
            }

            history = {
                'current prob': success_probs[current_percent_index],
                'selection': selection,
                'final prob': final_prob,
                'result': [column for column in state]
            }

            result = self.result(state)
            yield result, history
            if result is not None:
                break
            
            current_percent_index = next_percent_index

if __name__ == '__main__':
    ist = simulator('97_1st', 'relic')