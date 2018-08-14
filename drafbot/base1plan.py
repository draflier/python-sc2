import sc2
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *

# the point of this class is to supply the variables used for passing of the planned buildigns
# Planned Gateway, Planned cybercore shall be used as variables for tensorflow.
class BasePlan():
    intPlannedGateway = 1
    intPlannedCyberCore = 1
    intPlannedStarport = 1
    IsCompleteFlg = False
    


    async def buildStructures(self,draf_bot):
        if draf_bot.units(PYLON).ready.exists:
            #print("self.GatewayCnt ==> " + str(self.GatewayCnt))
            #print("self.intPlannedGateway ==> " + str(self.intPlannedGateway))
            #print("draf_bot.units(GATEWAY).amount ==> " + str(draf_bot.units(GATEWAY).amount))
            #print("draf_bot.units(CYBERNETICSCORE).amount ==> " + str(draf_bot.units(CYBERNETICSCORE).amount))
            pylon = draf_bot.units(PYLON).ready.random
            _intGatewaycnt = draf_bot.units(GATEWAY).amount + draf_bot.units(WARPGATE).amount
            if _intGatewaycnt < self.intPlannedGateway:
                #print("hehehe")                        
                if draf_bot.can_afford(GATEWAY) and not draf_bot.already_pending(GATEWAY):
                    await draf_bot.build(GATEWAY, near=pylon)
                    draf_bot.on_end_test()


            if draf_bot.units(CYBERNETICSCORE).amount < self.intPlannedCyberCore:
                if draf_bot.can_afford(CYBERNETICSCORE) and not draf_bot.already_pending(CYBERNETICSCORE):
                    await draf_bot.build(CYBERNETICSCORE, near=pylon)                    
            
            if draf_bot.units(CYBERNETICSCORE).amount > 0:
                if draf_bot.units(STARGATE).amount < self.intPlannedStarport:
                    if draf_bot.can_afford(STARGATE) and not draf_bot.already_pending(STARGATE):
                        await draf_bot.build(STARGATE, near=pylon)
                        

            if draf_bot.units(GATEWAY).amount >= self.intPlannedGateway \
                and draf_bot.units(CYBERNETICSCORE).amount >= self.intPlannedCyberCore \
                and draf_bot.units(STARGATE).amount >= self.intPlannedStarport:
                self.IsCompleteFlg = True
            
            await self.researchWarpGate(draf_bot)

    async def researchWarpGate(self,draf_bot):
            if draf_bot.units(CYBERNETICSCORE).ready.exists and draf_bot.can_afford(RESEARCH_WARPGATE) and not draf_bot.warpgate_started:
                ccore = draf_bot.units(CYBERNETICSCORE).ready.first
                await draf_bot.do(ccore(RESEARCH_WARPGATE))
                draf_bot.warpgate_started = True

            for gateway in draf_bot.units(GATEWAY).ready:
                abilities = await draf_bot.get_available_abilities(gateway)
                if AbilityId.MORPH_WARPGATE in abilities and draf_bot.can_afford(AbilityId.MORPH_WARPGATE):
                    await draf_bot.do(gateway(MORPH_WARPGATE))




    