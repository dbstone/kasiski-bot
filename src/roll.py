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

    @commands.command(aliases=['r'], help='Rolls dice', usage='[dice expression]')
    async def roll(self, ctx, *, arg):
        try:
            arg = arg.replace(' ', '') # Trim whitespace
        
            # collect operators
            operators = ''
            for c in arg:
                if c in VALID_ROLL_OPERATORS:
                    operators += c
            
            elements = re.split('\+|\-', arg) # collect operands

            evaluated_elements = []
            for element in elements:
                if element.isnumeric():
                    evaluated_elements.append([int(element)])
                elif re.match('^\d*d?\d+$', element):
                    result = [int(i) for i in dice.roll(element)]
                    evaluated_elements.append(result)
                else:
                    await ctx.send('`Malformed input`')
                    return
            
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
            await ctx.send(f'`{out_str}`')
        except dice.DiceBaseException as e:
            await ctx.send(f'Error: {e}')
        
        self.stats_increment_num_rolls(ctx.author.id)

    @commands.command(help='Displays your personal dice-rolling stats')
    async def stats(self, ctx):
        num_rolls = self.stats_get_num_rolls(ctx.author.id)
        await ctx.send(f'You have rolled {num_rolls} times')

