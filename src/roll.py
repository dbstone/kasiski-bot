# built-in
import re
import sqlite3

# third-party
from discord.ext import commands
import dice

VALID_ROLL_OPERATORS = '+-'

class Roll(commands.Cog):
    def __init__(self):
        self.db = sqlite3.connect('roll.db')
        
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS stats
                (userID int NOT NULL PRIMARY KEY, numRolls int)'''
        )
        
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS macros
                (userID int NOT NULL, alias text NOT NULL, roll text NOT NULL)'''
        )
        
        self.db.execute(
            '''CREATE TABLE IF NOT EXISTS attacks
                (userID int NOT NULL, 
                 alias text NOT NULL, 
                 hitMod int NOT NULL, 
                 dmgDie int NOT NULL, 
                 numDmgDice int NOT NULL,
                 dmgMod int NOT NULL)'''
        )

    def stats_ensure_user_exists(self, userID):
        try:
            with self.db:
                if not self.db.execute('select exists(select * from stats where userID=?)', (userID,)).fetchone()[0]:
                    self.db.execute('insert into stats(userID, numRolls) values(?, 0)', (userID,)) 
        except Exception as e:
            print(e)

    def stats_increment_num_rolls(self, userID):
        try:
            self.stats_ensure_user_exists(userID)
            with self.db:
                self.db.execute('update stats set numRolls=numRolls+1 where userID=?', (userID,))
        except Exception as e:
            print(e)

    def stats_get_num_rolls(self, userID):
        numRolls = 0
        self.stats_ensure_user_exists(userID)
        try:
            numRolls = self.db.execute('select numRolls from stats where userID=?', (userID,)).fetchone()[0]
        except Exception as e:
            print(e)
        return numRolls

    def create_macro(self, userID, alias, roll):
        try:
            with self.db:
                if self.db.execute('select exists(select * from macros where userID=? and alias=?)', (userID, alias)).fetchone()[0]:
                    self.db.execute('update macros set roll=? where userID=? and alias=?', (roll, userID, alias))
                else:
                    self.db.execute('insert into macros(userID, alias, roll) values(?, ?, ?)', (userID, alias, roll)) 
        except Exception as e:
            print(e)

    def get_macro(self, userID, alias):
        try:
            roll = self.db.execute('select roll from macros where userID=? and alias=?', (userID, alias)).fetchone()
            if roll:
                return roll[0]
            else:
                return None
        except Exception as e:
            print(e)
    
    def create_attack_macro(self, userID, alias, hit_mod, dmg_die, num_dmg_dice, dmg_mod):
        try:
            with self.db:
                if self.db.execute('select exists(select * from attacks where userID=? and alias=?)', (userID, alias)).fetchone()[0]:
                    self.db.execute(
                        'update attacks set hitMod=?, dmgDie=?, numDmgDice=?, dmgMod=? where userID=? and alias=?', 
                        (hit_mod, dmg_die, num_dmg_dice, dmg_mod)
                    )
                else:
                    self.db.execute(
                        'insert into attacks(userID, alias, hitMod, dmgDie, numDmgDice, dmgMod) values(?, ?, ?, ?, ?, ?)', 
                        (userID, alias, hit_mod, dmg_die, num_dmg_dice, dmg_mod)
                    ) 
        except Exception as e:
            print(e)
    
    def get_attack_macro(self, userID, alias):
        try:
            return self.db.execute('select roll from macros where userID=? and alias=?', (userID, alias)).fetchone()
        except Exception as e:
            print(e)

    async def handle_attack_macro(self, ctx, hit_mod, dmg_die, num_dmg_dice, dmg_mod):
        try:
            hit = dice.roll('d20')

            critical = hit == 20
            
            hit_result = f'`{hit} + {hit_mod} Total: {hit+hit_mod}`'
            
            if critical:
                num_dmg_dice *= 2

            dmg_roll = f'{num_dmg_dice}d{dmg_die}'
            if dmg_mod < 0:
                dmg_roll += '-'
            else:
                dmg_roll += '+'
            dmg_roll += str(dmg_mod)

            dmg_result = self.handle_roll(dmg_roll)

            return f'Hit: {hit_result} Damage: {dmg_result}'

        except dice.DiceBaseException as e:
            return f'Error: {e}'

    async def handle_roll(self, roll):
        try:
            roll = roll.replace(' ', '') # Trim whitespace
        
            # collect operators
            operators = ''
            for c in roll:
                if c in VALID_ROLL_OPERATORS:
                    operators += c
            
            elements = re.split('\+|\-', roll) # collect operands

            evaluated_elements = []
            for element in elements:
                if element.isnumeric():
                    evaluated_elements.append([int(element)])
                elif re.match('^\d*d?\d+$', element):
                    result = [int(i) for i in dice.roll(element)]
                    evaluated_elements.append(result)
                else:
                    return '`Malformed input`'
            
            total = 0
            for i, element in enumerate(evaluated_elements):
                if i == 0 or operators[i-1] == '+':
                    total += sum(element)
                elif operators[i-1] == '-':
                    total -= sum(element)
            
            if len(evaluated_elements[0]) > 100:
                out_str = '[...]'
            else:
                out_str = str(evaluated_elements[0])

            for i, element in enumerate(evaluated_elements[1:]):
                out_str += ' ' + operators[i]
                if len(element) > 100:
                    out_str += ' [...]'
                else:
                    out_str += ' ' + str(element)

            out_str = f'{out_str} Total: {total}'
            return f'`{out_str}`'
        except dice.DiceBaseException as e:
            return f'Error: `{e}`'

    @commands.command(aliases=['r'], help='Rolls dice', usage='[dice expression] | <macro>')
    async def roll(self, ctx, *, arg):
        result = None

        # handle macros
        macro = self.get_macro(ctx.author.id, arg)
        if macro:
            arg = macro
        else:
            attack_macro = self.get_attack_macro(ctx.author.id, arg)
            if attack_macro:
                result = self.handle_attack_macro(ctx, *attack_macro)

        if not result:
            result = handle_roll(arg)

        self.stats_increment_num_rolls(ctx.author.id)
        await ctx.send(result)

    @commands.command(help='Displays your personal dice-rolling stats')
    async def stats(self, ctx):
        num_rolls = self.stats_get_num_rolls(ctx.author.id)
        await ctx.send(f'You have rolled {num_rolls} times')

    @commands.command(help='Creates a personal roll macro', usage='<alias> <roll>')
    async def rollmacro(self, ctx, alias, roll):
        self.create_macro(ctx.author.id, alias, roll)
        await ctx.send(f'Roll macro set. Usage: `.roll {alias}`')
    
    @commands.command(help='Creates a personal roll macro for a D&D 5e attack', usage='<alias> <hit modifier> <damage roll>')
    async def attackmacro(self, ctx, alias, hit_mod, damage_roll):
        await ctx.send(f'Roll macro set. Usage: `.roll {alias}`')
