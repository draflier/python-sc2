import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
import random
#from sc2.data import race_townhalls

# the point of this class is to set all the attack type options for the units to attack.

class OffenseCoord():
    intIsAllAttack = 0    

    def select_target(self,draf_bot):
        if draf_bot.known_enemy_structures.exists:
            return random.choice(draf_bot.known_enemy_structures).position

        return draf_bot.enemy_start_locations[0]

    async def attackWithAll(self,draf_bot):    
        #print("draf_bot.unitsBuilder.objForcesList len ==>" + str(len(draf_bot.unitsBuilder.objForcesList)))    
        for _objUnitTypes in draf_bot.unitsBuilder.objForcesList:
            await draf_bot.do(_objUnitTypes.attack(self.select_target(draf_bot)))
        #for unit in forces.idle:
        #    await self.do(unit.attack(self.select_target()))

    async def defendNexus(self,draf_bot):
        _Target = False
        if len(draf_bot.known_enemy_units.not_structure) > 0:
            _Target = draf_bot.known_enemy_units.closest_to(random.choice(draf_bot.units(NEXUS)))
        if _Target:
            for _objUnitTypes in draf_bot.unitsBuilder.objForcesList:
                await draf_bot.do(_objUnitTypes.attack(_Target))