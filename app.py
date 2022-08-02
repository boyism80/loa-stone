import lost_ark.stone.simulator

def callback(current_prob, selection, final_prob, state):
    print(f'current prob : {current_prob * 100:.2f}%, next selection : {selection+1}, final success prob : {final_prob * 100:.5f}% : {state}')

if __name__ == '__main__':
    ist = lost_ark.stone.simulator('97', 'relic')

    success, state = ist.simulate(callback)
    print(f'result : {success}, {state}')