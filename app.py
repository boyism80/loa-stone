import loa.stone.simulator

if __name__ == '__main__':
    ist = loa.stone.simulator('97', 'relic')

    count = 0
    while True:
        history_list = []
        for success, history in ist.simulate():
            history_list.append(history)
        
        count = count + 1
        if not success:
            continue
        
        for history in history_list:
            print(f"[{history['current prob'] * 100:6.2f}% | {history['final prob'] * 100:5.2f}%] select {history['selection']+1} => {history['result']}")
        print(f'try count : {count}')
        break