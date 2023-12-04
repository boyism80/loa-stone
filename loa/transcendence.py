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
    def __init__(self, blocks, spirit1, spirit2, reversed_spirits):
        self.__blocks = blocks
        self.__spirit1 = spirit1
        self.__spirit2 = spirit2
        self.__reversed_spirits = reversed_spirits
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

    def on_destroy_block(self, blocks, block_flags):
        if (block_flags & BLOCK_STATE_DISTORTION) == BLOCK_STATE_DISTORTION:
            for n in random.sample(list(self.alives(blocks)), 3):
                blocks[n] = BLOCK_STATE_ALIVE
        
        if self.is_finish(blocks):
            return
        
        # TODO: special block effect

    def alives(self, blocks):
        for i in range(len(blocks)):
            if blocks[i] == BLOCK_STATE_ALIVE:
                yield i

    def destroyed(self, blocks):
        for i in range(len(blocks)):
            if blocks[i] == BLOCK_STATE_DESTROY:
                yield i

    def is_finish(self, blocks):
        for i in range(len(blocks)):
            if (blocks[i] & BLOCK_STATE_SPIRIT) == BLOCK_STATE_SPIRIT:
                return False
        
        return True

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

    def simulate(self, p):
        blocks = copy.deepcopy(self.__blocks)
        spirit_name = self.__spirit1
        for n, prob, spirit_type in self.__spirit_maps[spirit_name](blocks, p):
            if n is None:
                continue

            if random.random() > prob:
                continue

            block_flags = 0x00000000
            if blocks[n] == BLOCK_STATE_DISTORTION:
                if spirit_type != SPIRIT_LEGEND and spirit_name not in ('cleans', 'cleans_ex', 'cleans_lgd', 'world_wood'):
                    block_flags = block_flags | BLOCK_STATE_DISTORTION
            blocks[n] = BLOCK_STATE_DESTROY

        self.on_destroy_block(blocks, block_flags)
        return blocks

if __name__ == '__main__':
    ist = simulator(BLOCKS, 'world_tree', 'fountain', ('lightning', 'lightning_strike', 'hell_fire'))
    print(ist.simulate((2, 2)))