import copy
import random

BLOCK_STATE_DESTROY     = 0x00000000
BLOCK_STATE_SPIRIT      = 0x00001000
BLOCK_STATE_ALIVE       = BLOCK_STATE_SPIRIT | 0x00000000
BLOCK_STATE_REPLACE     = BLOCK_STATE_SPIRIT | 0x00000001
BLOCK_STATE_BLESS       = BLOCK_STATE_SPIRIT | 0x00000002
BLOCK_STATE_ADDITION    = BLOCK_STATE_SPIRIT | 0x00000004
BLOCK_STATE_MISTERY     = BLOCK_STATE_SPIRIT | 0x00000008
BLOCK_STATE_EXTENTION   = BLOCK_STATE_SPIRIT | 0x00000010
BLOCK_STATE_REPLICATION = BLOCK_STATE_SPIRIT | 0x00000020
BLOCK_STATE_DISTORTION  = 0x00002000

SPIRIT_NORMAL = 0
SPIRIT_EXTEND = 1
SPIRIT_LEGEND = 2

BLOCK_WIDTH = 6
BLOCK_HEIGHT = 6
BLOCK_SIZE = (BLOCK_HEIGHT, BLOCK_WIDTH)
BLOCKS = [BLOCK_STATE_ALIVE] * BLOCK_WIDTH * BLOCK_HEIGHT

class simulator:
    def __init__(self, blocks, spirits, reversed_spirits, summon_chance, change_chance):
        self.__blocks = blocks
        self.__spirits = copy.deepcopy(spirits) if spirits else [self.random_spirit(), self.random_spirit()]
        self.__active_spirit = None
        self.__inactive_spirit = None
        self.__reserved_spirits = reversed_spirits if reversed_spirits else (self.random_spirit(), self.random_spirit(), self.random_spirit())
        self.__summon_chance = summon_chance
        self.__change_chance = change_chance
        self.__spirit_maps = {
            'lightning_strike': self.lightning_strike,
            'lightning_strike_ex': self.lightning_strike_ex,
            'lightning_strike_lgd': self.lightning_strike_lgd,
            'lightning': self.lightning,
            'lightning_ex': self.lightning_ex,
            'lightning_lgd': self.lightning_lgd,
            'hell_fire': self.hell_fire,
            'hell_fire_ex': self.hell_fire_ex,
            'hell_fire_lgd': self.hell_fire_lgd,
            'tidal_wave': self.tidal_wave,
            'tidal_wave_ex': self.tidal_wave_ex,
            'tidal_wave_lgd': self.tidal_wave_lgd,
            'earthquake': self.earthquake,
            'earthquake_ex': self.earthquake_ex,
            'earthquake_lgd': self.earthquake_lgd,
            'explosion': self.explosion,
            'explosion_ex': self.explosion_ex,
            'explosion_lgd': self.explosion_lgd,
            'cleans': self.cleans,
            'cleans_ex': self.cleans_ex,
            'cleans_lgd': self.cleans_lgd,
            'world_tree': self.world_tree,
            'shock_wave': self.shock_wave,
            'shock_wave_ex': self.shock_wave_ex,
            'shock_wave_lgd': self.shock_wave_lgd,
            'storm': self.storm,
            'storm_ex': self.storm_ex,
            'storm_lgd': self.storm_lgd,
            'mesocyclone': self.mesocyclone,
            'mesocyclone_ex': self.mesocyclone_ex,
            'mesocyclone_lgd': self.mesocyclone_lgd,
            'fountain': self.fountain
        }
        self.__spirit_effects = {
            BLOCK_STATE_REPLACE: self.BLOCK_STATE_REPLACE_callback,
            BLOCK_STATE_BLESS: self.BLOCK_STATE_BLESS_callback,
            BLOCK_STATE_ADDITION: self.BLOCK_STATE_ADDITION_callback,
            BLOCK_STATE_MISTERY: self.BLOCK_STATE_MISTERY_callback,
            BLOCK_STATE_EXTENTION: self.BLOCK_STATE_EXTENTION_callback,
            BLOCK_STATE_REPLICATION: self.BLOCK_STATE_REPLICATION_callback
        }
        self.__queue = []

    def index(self, row, col):
        rows, cols = BLOCK_SIZE
        row = max(0, min(row, rows))
        col = max(0, min(col, cols))

        return (row * cols) + col

    def position(self, i):
        row = i // BLOCK_WIDTH
        col = i % BLOCK_WIDTH
        return row, col

    def left(self, i):
        if i is None:
            return None
        
        row, col = self.position(i)
        col = col - 1
        if col < 0:
            return None
        
        return self.index(row, col)

    def right(self, i):
        if i is None:
            return None
        
        row, col = self.position(i)
        col = col + 1
        if col >= BLOCK_WIDTH:
            return None
        
        return self.index(row, col)

    def up(self, i):
        if i is None:
            return None
        
        row, col = self.position(i)
        row = row - 1
        if row < 0:
            return None
        
        return self.index(row, col)

    def down(self, i):
        if i is None:
            return None
        
        row, col = self.position(i)
        row = row + 1
        if row >= BLOCK_HEIGHT:
            return None
        
        return self.index(row, col)
    
    def choice(self, blocks, flags):
        for n in range(len(blocks)):
            if (blocks[n] & flags) == flags:
                yield n
    
    def BLOCK_STATE_REPLACE_callback(self, blocks):
        shuffle = random.sample(blocks, len(blocks))
        for i in range(len(blocks)):
            blocks[i] = shuffle[i]

    def BLOCK_STATE_BLESS_callback(self, blocks):
        self.__summon_chance = self.__summon_chance + 1

    def BLOCK_STATE_ADDITION_callback(self, blocks):
        self.__change_chance = self.__change_chance + 1

    def BLOCK_STATE_MISTERY_callback(self, blocks):
        if random.random() > 0.8:
            self.__inactive_spirit = 'world_tree'
        else:
            self.__inactive_spirit = 'fountain'

    def root_spirit(self, spirit):
        data = {
            'lightning_strike': ('lightning_strike', SPIRIT_NORMAL),
            'lightning_strike_ex': ('lightning_strike', SPIRIT_EXTEND),
            'lightning_strike_lgd': ('lightning_strike', SPIRIT_LEGEND),
            'lightning': ('lightning', SPIRIT_NORMAL),
            'lightning_ex': ('lightning', SPIRIT_EXTEND),
            'lightning_lgd': ('lightning', SPIRIT_LEGEND),
            'hell_fire': ('hell_fire', SPIRIT_NORMAL),
            'hell_fire_ex': ('hell_fire', SPIRIT_EXTEND),
            'hell_fire_lgd': ('hell_fire', SPIRIT_LEGEND),
            'tidal_wave': ('tidal_wave', SPIRIT_NORMAL),
            'tidal_wave_ex': ('tidal_wave', SPIRIT_EXTEND),
            'tidal_wave_lgd': ('tidal_wave', SPIRIT_LEGEND),
            'earthquake': ('earthquake', SPIRIT_NORMAL),
            'earthquake_ex': ('earthquake', SPIRIT_EXTEND),
            'earthquake_lgd': ('earthquake', SPIRIT_LEGEND),
            'explosion': ('explosion', SPIRIT_NORMAL),
            'explosion_ex': ('explosion', SPIRIT_EXTEND),
            'explosion_lgd': ('explosion', SPIRIT_LEGEND),
            'cleans': ('cleans', SPIRIT_NORMAL),
            'cleans_ex': ('cleans', SPIRIT_EXTEND),
            'cleans_lgd': ('cleans', SPIRIT_LEGEND),
            'world_tree': ('world_tree', SPIRIT_NORMAL),
            'shock_wave': ('shock_wave', SPIRIT_NORMAL),
            'shock_wave_ex': ('shock_wave', SPIRIT_EXTEND),
            'shock_wave_lgd': ('shock_wave', SPIRIT_LEGEND),
            'storm': ('storm', SPIRIT_NORMAL),
            'storm_ex': ('storm', SPIRIT_EXTEND),
            'storm_lgd': ('storm', SPIRIT_LEGEND),
            'mesocyclone': ('mesocyclone', SPIRIT_NORMAL),
            'mesocyclone_ex': ('mesocyclone', SPIRIT_EXTEND),
            'mesocyclone_lgd': ('mesocyclone', SPIRIT_LEGEND),
            'fountain': ('fountain', SPIRIT_NORMAL)
        }
        return data[spirit]


    def upgrade_spirit(self, spirit):
        ext_map = {
            'lightning_strike': 'lightning_strike_ex',
            'lightning_strike_ex': 'lightning_strike_lgd',
            'lightning': 'lightning_ex',
            'lightning_ex': 'lightning_lgd',
            'hell_fire': 'hell_fire_ex',
            'hell_fire_ex': 'hell_fire_lgd',
            'tidal_wave': 'tidal_wave_ex',
            'tidal_wave_ex': 'tidal_wave_lgd',
            'earthquake': 'earthquake_ex',
            'earthquake_ex': 'earthquake_lgd',
            'explosion': 'explosion_ex',
            'explosion_ex': 'explosion_lgd',
            'cleans': 'cleans_ex',
            'cleans_ex': 'cleans_lgd',
            'shock_wave': 'shock_wave_ex',
            'shock_wave_ex': 'shock_wave_lgd',
            'storm': 'storm_ex',
            'storm_ex': 'storm_lgd',
            'mesocyclone': 'mesocyclone_ex',
            'mesocyclone_ex': 'mesocyclone_lgd'
        }
        
        if spirit in ext_map:
            return ext_map[spirit]
        else:
            return spirit

    def BLOCK_STATE_EXTENTION_callback(self, blocks):
        self.__inactive_spirit = self.upgrade_spirit(self.__inactive_spirit)
        
    def BLOCK_STATE_REPLICATION_callback(self, blocks):
        self.__inactive_spirit = self.__active_spirit

    def random_spirit(self):
        return random.choice(['lightning_strike', 'lightning', 'hell_fire', 'tidal_wave', 'earthquake', 'explosion', 'cleans', 'shock_wave', 'storm', 'mesocyclone'])
    
    def spirit_change(self, spirit, free=False):
        i = 0 if spirit is self.__spirits[0] else 1
        while True:
            self.__spirits[i] = self.__reserved_spirits[0]
            self.__reserved_spirits = [*self.__reserved_spirits[1:], self.random_spirit()]

            spirit1, level1 = self.root_spirit(self.__spirits[0])
            spirit2, level2 = self.root_spirit(self.__spirits[1])
            if spirit1 == spirit2:
                if level1 >= level2:
                    self.__spirits[0] = self.upgrade_spirit(self.__spirits[0])
                else:
                    self.__spirits[0] = self.upgrade_spirit(self.__spirits[1])
                i = 1
            else:
                break
        if not free:
            self.__change_chance = self.__change_chance - 1
    
    def on_destroy_block(self, blocks, block_flags):
        # TODO: 임의의 위치에 생성되는거 빈 칸에 생성되는건지 확인
        if (block_flags & BLOCK_STATE_DISTORTION) == BLOCK_STATE_DISTORTION:
            for n in random.sample(list(self.destroyed(blocks)), 3):
                blocks[n] = BLOCK_STATE_ALIVE
        
        for k, v in self.__spirit_effects.items():
            if (block_flags & k) == k:
                v(blocks)
                break

        self.spirit_change(self.__active_spirit, True)

        for n in self.specials(blocks):
            blocks[n] = BLOCK_STATE_ALIVE
        
        alive_blocks = list(self.alives(blocks))
        if alive_blocks:
            random_block = random.choice(alive_blocks)
            blocks[random_block] = random.choice(list(self.__spirit_effects.keys()))

    def alives(self, blocks):
        return self.choice(blocks, BLOCK_STATE_ALIVE)

    def destroyed(self, blocks):
        for i in range(len(blocks)):
            if blocks[i] == BLOCK_STATE_DESTROY:
                yield i
    
    def specials(self, blocks):
        for n in self.alives(blocks):
            if blocks[n] > BLOCK_STATE_ALIVE:
                yield n

    def is_finish(self, blocks):
        return not any(n for n in self.alives(blocks))

    def __lightning_strike(self, blocks, p, callback):
        i = self.index(*p)
        for n in (self.left(i), self.right(i), self.up(i), self.down(i)):
            yield callback(n, 0.5)

        yield callback(i, 1.0)

    def lightning_strike(self, blocks, p):
        for x in self.__lightning_strike(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x

    def lightning_strike_ex(self, blocks, p):
        for x in self.__lightning_strike(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x

    def lightning_strike_lgd(self, blocks, p):
        for x in self.__lightning_strike(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __lightning(self, blocks, p, destroy_range, callback):
        i = self.index(*p)
        yield callback(i, 1.0)

        blocks[i] = BLOCK_STATE_DESTROY
        alive_blocks = list(self.alives(blocks))

        destory_count = random.choice(range(destroy_range))
        if destory_count > 0:
            for n in random.sample(alive_blocks, min(destory_count, len(alive_blocks))):
                yield callback(n, 1.0)
        else:
            n = random.choice(list(self.destroyed(blocks)))
            blocks[n] = BLOCK_STATE_ALIVE

    def lightning(self, blocks, p):
        for x in self.__lightning(blocks, p, 3, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x

    def lightning_ex(self, blocks, p):
        for x in self.__lightning(blocks, p, 5, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x

    def lightning_lgd(self, blocks, p):
        for x in self.__lightning(blocks, p, 7, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __hell_fire(self, blocks, p, callback):
        i = self.index(*p)
        for n in (self.up(self.up(i)), self.up(self.left(i)), self.up(i), self.up(self.right(i)), self.left(self.left(i)), self.left(i), self.right(i), self.right(self.right(i)), self.left(self.down(i)), self.down(i), self.right(self.down(i)), self.down(self.down(i))):
            yield callback(n, 0.5)

        yield callback(i, 1.0)
    
    def hell_fire(self, blocks, p):
        for x in self.__hell_fire(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x
    
    def hell_fire_ex(self, blocks, p):
        for x in self.__hell_fire(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x
    
    def hell_fire_lgd(self, blocks, p):
        for x in self.__hell_fire(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __tidal_wave(self, blocks, p, callback):
        count = max(BLOCK_WIDTH, BLOCK_HEIGHT)
        i = self.index(*p)
        l = r = t = d = i
        for i in range(count):
            l = self.left(l)
            r = self.right(r)
            t = self.up(t)
            d = self.down(d)
            prob = 1.0 - ((i+1) * 0.15)
            for n in (l, r, t, d):
                yield callback(n, prob)
        
        yield callback(i, 1.0)
    
    def tidal_wave(self, blocks, p):
        for x in self.__tidal_wave(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x
    
    def tidal_wave_ex(self, blocks, p):
        for x in self.__tidal_wave(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x
    
    def tidal_wave_lgd(self, blocks, p):
        for x in self.__tidal_wave(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __earthquake(self, blocks, p, callback):
        i = self.index(*p)
        l = r = i
        for i in range(BLOCK_WIDTH):
            l = self.left(l)
            r = self.right(r)
            prob = 1.0 - ((i+1) * 0.15)
            
            yield callback(l, prob)
            yield callback(r, prob)
        
        yield callback(i, 1.0)

    def earthquake(self, blocks, p):
        for x in self.__earthquake(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x
    
    def earthquake_ex(self, blocks, p):
        for x in self.__earthquake(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x
    
    def earthquake_lgd(self, blocks, p):
        for x in self.__earthquake(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __explosion(self, blocks, p, callback):
        count = max(BLOCK_WIDTH, BLOCK_HEIGHT)
        i = self.index(*p)
        lt = rt = ld = rd = i
        for i in range(count):
            lt = self.left(self.up(lt))
            rt = self.right(self.up(rt))
            ld = self.left(self.down(ld))
            rd = self.right(self.down(rd))
            prob = 1.0 - ((i+i)*0.15)

            for n in (lt, rt, ld, rd):
                yield callback(n, prob)

        yield callback(i, 1.0)
    
    def explosion(self, blocks, p):
        for x in self.__explosion(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x
    
    def explosion_ex(self, blocks, p):
        for x in self.__explosion(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x

    def explosion_lgd(self, blocks, p):
        for x in self.__explosion(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __cleans(self, blocks, p, callback):
        i = self.index(*p)
        for n in (self.left(i), self.right(i)):
            yield callback(n, 0.5)

        yield callback(i, 1.0)
    
    def cleans(self, blocks, p):
        for x in self.__cleans(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x
    
    def cleans_ex(self, blocks, p):
        for x in self.__cleans(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x
    
    def cleans_lgd(self, blocks, p):
        for x in self.__cleans(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x
        
        i = self.index(*p)
        yield (self.up(i), 1.0, SPIRIT_LEGEND)
        yield (self.down(i), 1.0, SPIRIT_LEGEND)

    def world_tree(self, blocks, p):
        i = self.index(*p)
        for n in (i, self.up(i), self.left(i), self.right(i), self.down(i), self.up(self.up(i)), self.left(self.left(i)), self.right(self.right(i)), self.down(self.down(i))):
            yield (n, 1.0, SPIRIT_LEGEND)

    def __shock_wave(self, blocks, p, callback):
        i = self.index(*p)
        for n in (self.left(self.up(i)), self.up(i), self.right(self.up(i)), self.left(i), self.right(i), self.left(self.down(i)), self.down(i), self.right(self.down(i))):
            yield callback(n, 0.75)

        yield callback(i, 1.0)
    
    def shock_wave(self, blocks, p):
        for x in self.__shock_wave(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x

    def shock_wave_ex(self, blocks, p):
        for x in self.__shock_wave(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x
    
    def shock_wave_lgd(self, blocks, p):
        for x in self.__shock_wave(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __storm(self, blocks, p, callback):
        i = self.index(*p)
        u = d = i
        for i in range(BLOCK_HEIGHT):
            u = self.up(u)
            d = self.down(d)
            prob = 1.0 - ((i+i)*0.15)
            yield callback(u, prob)
            yield callback(d, prob)
        
        yield callback(i, 1.0)
    
    def storm(self, blocks, p):
        for x in self.__storm(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x
    
    def storm_ex(self, blocks, p):
        for x in self.__storm(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x

    def storm_lgd(self, blocks, p):
        for x in self.__storm(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def __mesocyclone(self, blocks, p, callback):
        i = self.index(*p)
        for n in (self.left(self.up(i)), self.right(self.up(i)), self.left(self.down(i)), self.right(self.down(i))):
            yield callback(n, 0.5)

        yield callback(i, 1.0)
    
    def mesocyclone(self, blocks, p):
        for x in self.__mesocyclone(blocks, p, lambda n, prob: (n, prob, SPIRIT_NORMAL)):
            yield x
    
    def mesocyclone_ex(self, blocks, p):
        for x in self.__mesocyclone(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_EXTEND)):
            yield x
    
    def mesocyclone_lgd(self, blocks, p):
        for x in self.__mesocyclone(blocks, p, lambda n, prob: (n, 1.0, SPIRIT_LEGEND)):
            yield x

    def fountain(self, blocks, p):
        i = self.index(*p)
        yield (i, 1.0, SPIRIT_NORMAL)

    def record(self, blocks):
        self.__queue.append({
            'blocks': copy.deepcopy(blocks),
            'spirits': copy.deepcopy(self.__spirits),
            'reserved_spirits': copy.deepcopy(self.__reserved_spirits),
            'change_chance': self.__change_chance,
            'summon_chance': self.__summon_chance
        })

    def history(self):
        return self.__queue

    def do(self, blocks, p):
        if self.is_finish(blocks):
            return True, blocks
        
        if self.__summon_chance == 0:
            return False, blocks

        blocks = copy.deepcopy(blocks)
        self.__active_spirit, self.__inactive_spirit = random.sample(self.__spirits, len(self.__spirits))
        for n, prob, spirit_type in self.__spirit_maps[self.__active_spirit](blocks, p):
            if n is None:
                continue

            if random.random() > prob:
                continue

            block_flags = 0x00000000
            if blocks[n] == BLOCK_STATE_DISTORTION:
                if spirit_type != SPIRIT_LEGEND and self.__active_spirit not in ('cleans', 'cleans_ex', 'cleans_lgd', 'world_wood'):
                    block_flags = block_flags | BLOCK_STATE_DISTORTION
            else:
                block_flags = block_flags | blocks[n]
            blocks[n] = BLOCK_STATE_DESTROY

        self.on_destroy_block(blocks, block_flags)
        self.__active_spirit = self.__inactive_spirit = None
        self.__summon_chance = self.__summon_chance - 1
        if self.is_finish(blocks):
            return True, blocks
        
        return None, blocks
    
    def simulation(self):
        blocks = self.__blocks
        while True:
            if self.is_finish(blocks):
                return True, blocks
            
            self.record(blocks)
            candidates = list(self.alives(blocks))
            if self.__change_chance > 0:
                candidates = candidates + [*self.__spirits]
            n = random.choice(candidates)
            if n in self.__spirits:
                self.spirit_change(n)
            else:
                success, blocks = self.do(blocks, self.position(n))
                if success is not None:
                    return success, blocks

if __name__ == '__main__':
    count = 0
    while True:
        count = count + 1
        ist = simulator(BLOCKS, None, None, 7, 3)
        success, blocks = ist.simulation()
        if success:
            break
    
    print(count)
    print(ist.history())