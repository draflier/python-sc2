import sc2
import random
from sc2 import run_game, maps, Race, Difficulty
from sc2.player import Bot, Computer
from sc2.constants import *
from base1plan import BasePlan
from unitComp import UnitComp
from offense_coord import OffenseCoord
from chrono_boost_coord import ChronoBoostCoord
from intel_coord import IntelCoord
import os

os.environ["SC2PATH"] = 'C:\\sc2\\StarCraft II'

class DrafBot(sc2.BotAI):
    b1Builder = BasePlan()
    unitsBuilder = UnitComp()
    armyCommand = OffenseCoord()
    objChronoBoostCoord = ChronoBoostCoord()
    objIntelCoord = IntelCoord()
    warpgate_started = False
    intSupplyBuffer = 2
    intPlannedBases = 3
    intPlannedAttackSupply = 70
    intPlannedWarpgatePerBase = 3
    


    async def on_step(self,iteration):
        await self.distribute_workers()
        await self.build_workers(iteration)
        await self.build_pylons()
        await self.offensive_force_buildings(iteration)        
        await self.build_assimilator()
        await self.objIntelCoord.intel(self)
        if iteration % 5 == 0: 
            await self.buildUnits()
            await self.chronoBoostBuildings()
            await self.commandArmy()
            await self.objIntelCoord.sendSimpleScout(self)
            await self.expand()

    def on_end(self, game_result):
        print('--- on_end called ---')
        print(game_result)

        #if game_result == Result.Victory:
        self.objIntelCoord.saveTrainData() 

    def on_end_test(self):
        print('--- on_end test called ---')

        #if game_result == Result.Victory:
        self.objIntelCoord.saveTrainData()            

    async def build_workers(self,iteration):
        # nexus = command center
        if iteration % 2 == 0:  
            for nexus in self.units(NEXUS).ready.noqueue:
                if self.units(PROBE).amount < (self.units(NEXUS).amount * 23):
                    if self.can_afford(PROBE):
                        await self.do(nexus.train(PROBE))  
                
    async def build_pylons(self):
        if self.supply_left < self.intSupplyBuffer and not self.already_pending(PYLON):
            nexuses = self.units(NEXUS).ready.random
            if self.can_afford(PYLON):
                await self.build(PYLON, near=nexuses.position.towards(self.game_info.map_center, 5))   

    async def expand(self):
        if self.units(NEXUS).amount < self.intPlannedBases:
            if self.b1Builder.IsCompleteFlg == True and self.can_afford(NEXUS):
                await self.expand_now() 
                   

    async def offensive_force_buildings(self,iteration):
        if iteration % 5 == 0:        
            await self.b1Builder.buildStructures(self)
        if self.units(NEXUS).ready.amount > 1:
            if self.can_afford(GATEWAY) and not self.already_pending(GATEWAY):
                pylon = self.units(PYLON).closest_to(self.enemy_start_locations[0])
                await self.build(GATEWAY, near=pylon.position.towards(self.game_info.map_center, 5))
        
    async def build_assimilator(self):
        for nexus in self.units(NEXUS).ready:
            if self.units(GATEWAY).ready.exists or self.already_pending(GATEWAY):
                vaspenes = self.state.vespene_geyser.closer_than(10.0, nexus)
                for vaspene in vaspenes:
                    if not self.can_afford(ASSIMILATOR):
                        break
                    worker = self.select_build_worker(vaspene.position)
                    if worker is None:
                        break
                    if not self.units(ASSIMILATOR).closer_than(1.0, vaspene).exists:
                        await self.do(worker.build(ASSIMILATOR, vaspene))  

    async def buildUnits(self):  
        await self.unitsBuilder.updateCurrUnitCompRatio(self)
        _intChoice = random.randrange(0,len(self.unitsBuilder.objUnitCntDict))
        print("_intChoice =>" + str(_intChoice))
        if _intChoice == 0:
            if not self.unitsBuilder.IsUnitRatioFull(0):
                await self.unitsBuilder.buildUnit(self,ZEALOT)
            else:
                intChoice = 1
        if _intChoice == 1:
            if not self.unitsBuilder.IsUnitRatioFull(1):
                await self.unitsBuilder.buildUnit(self,STALKER)
            else:
                intChoice = 2
        if _intChoice == 2:
            if not self.unitsBuilder.IsUnitRatioFull(2):
                await self.unitsBuilder.buildUnit(self,SENTRY)
            else:
                intChoice = 3
        if _intChoice == 3:
            if not self.unitsBuilder.IsUnitRatioFull(3):
                await self.unitsBuilder.buildUnit(self,ADEPT)
            else:
                intChoice = 4
        if _intChoice == 4:
            if not self.unitsBuilder.IsUnitRatioFull(3):
                await self.unitsBuilder.buildUnit(self,VOIDRAY)

        self.unitsBuilder.IsUnitsRatioFull()

    async def commandArmy(self):
        if self.supply_cap - self.units(PROBE).amount < self.intPlannedAttackSupply:
            await self.armyCommand.defendNexus(self)
        else:
            await self.armyCommand.attackWithAll(self)


    async def chronoBoostBuildings(self):
        await self.objChronoBoostCoord.boostWarpgate(self)

    


      


run_game(maps.get("Abyssal Reef LE"),[Bot(Race.Protoss, DrafBot()), Computer(Race.Terran, Difficulty.Easy)],realtime=False)
