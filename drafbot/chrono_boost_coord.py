import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *

# the point of this class is to supply the variables used for passing of the planned buildigns
# Planned Gateway, Planned cybercore shall be used as variables for tensorflow.
class ChronoBoostCoord():
    intWarpgateBoostCnt = 0

    async def boostWarpgate(self,draf_bot):
            objNexus = draf_bot.units(NEXUS).ready.random
            if draf_bot.units(CYBERNETICSCORE).ready.exists:
                ccore = draf_bot.units(CYBERNETICSCORE).ready.first
                if self.intWarpgateBoostCnt != 4:
                    if not ccore.has_buff(BuffId.CHRONOBOOSTENERGYCOST):
                        abilities = await draf_bot.get_available_abilities(objNexus)
                        if AbilityId.EFFECT_CHRONOBOOSTENERGYCOST in abilities:
                            await draf_bot.do(objNexus(AbilityId.EFFECT_CHRONOBOOSTENERGYCOST, ccore))
                            self.intWarpgateBoostCnt = self.intWarpgateBoostCnt + 1

    