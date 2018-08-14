import sc2
from sc2 import run_game, maps, Race, Difficulty,Result
from sc2.player import Bot, Computer
from sc2.constants import *

# the point of this class is to supply the variables used for passing of the unit composition
# the PlannedVariables are intended to serve as a ratio of the total army composition
# e.g 
#    intPlannedZealots = 1
#    intPlannedStalkers = 2
#    intPlannedVoidRays = 3
#    intDenominator = 
#    Total ratio of the units is    
class UnitComp():
    objUnitRatioDict = dict(intZealotsWeight=2, intStalkersWeight=3, intSentryCnt = 1, intAdept = 1, intVoidrayWeight=2)
    objUnitCntDict = dict(intZealotsCnt=0, intStalkersCnt=0, intSentryCnt = 0, intAdept = 0, intVoidrayCnt=0)
    objForcesList = []
    objWarpableUnitsList = [ZEALOT,STALKER,SENTRY,ADEPT]
    intUnitCompCycle = 1
    IsCompleteFlg = False

    async def buildUnit(self,draf_bot,objUnitType):  
        if objUnitType in self.objWarpableUnitsList:
            if draf_bot.units(WARPGATE).ready.exists:            
                    await self.warpUnit(draf_bot,objUnitType) 
            else:
                await self.trainUnit(draf_bot,objUnitType)  
        else:        
            await self.trainUnit(draf_bot,objUnitType)  

    async def trainUnit(self,draf_bot,objUnitType):
        if objUnitType in self.objWarpableUnitsList:
            for gw in draf_bot.units(GATEWAY).ready.noqueue:
                if draf_bot.can_afford(objUnitType) and draf_bot.supply_left > 0:
                    await draf_bot.do(gw.train(objUnitType))
        
        for objSG in draf_bot.units(STARGATE).ready.noqueue:
            if draf_bot.can_afford(objUnitType) and draf_bot.supply_left > 0:
                await draf_bot.do(objSG.train(objUnitType))

    

    async def updateCurrUnitCompRatio(self,draf_bot):
        self.objForcesList = (draf_bot.units(ZEALOT) | 
                    draf_bot.units(STALKER) | 
                    draf_bot.units(SENTRY) |
                    draf_bot.units(ADEPT) |
                    draf_bot.units(VOIDRAY)) 
        self.objUnitCntDict.update(intZealotsCnt=draf_bot.units(ZEALOT).amount,
                                    intStalkersCnt=draf_bot.units(STALKER).amount, 
                                    intSentryCnt=draf_bot.units(SENTRY).amount, 
                                    intAdeptCnt=draf_bot.units(ADEPT).amount, 
                                    intVoidrayCnt=draf_bot.units(VOIDRAY).amount)
    
    def IsUnitRatioFull(self,intListIdx):
        _objUnitCntList = list(self.objUnitCntDict.values())
        _objUnitRatioList = list(self.objUnitRatioDict.values())
        #print ("objUnitCntList ==> " + str(_objUnitCntList))
        #print ("objUnitRatioList ==> " + str(_objUnitRatioList))
        if _objUnitCntList[intListIdx] < _objUnitRatioList[intListIdx] * self.intUnitCompCycle:
            return False
        else:
            return True

    #TODO comment on this function
    def IsUnitsRatioFull(self):
        _objUnitCntList = list(self.objUnitCntDict.values())
        _objUnitRatioList = list(self.objUnitRatioDict.values())
        #print("self.intUnitCompCycle ==> " + str(self.intUnitCompCycle))
        for i in range(len(_objUnitCntList)):
            if _objUnitRatioList[i] != 0:
                if _objUnitCntList[i] < _objUnitRatioList[i] * self.intUnitCompCycle:
                    return False
                
        if self.intUnitCompCycle < 4:
            self.intUnitCompCycle = self.intUnitCompCycle + 1
        return True
            

    async def warpUnit(self,draf_bot,objUnitType):
        for warpgate in draf_bot.units(WARPGATE).ready:
            abilities = await draf_bot.get_available_abilities(warpgate)
            if AbilityId.WARPGATETRAIN_ZEALOT in abilities:
                proxy = draf_bot.units(PYLON).closest_to(draf_bot.enemy_start_locations[0])
                pos = proxy.position.to2.random_on_distance(4)
                placement = await draf_bot.find_placement(AbilityId.WARPGATETRAIN_STALKER, pos, placement_step=1)
                if placement is None:
                    #return ActionResult.CantFindPlacementLocation
                    print("can't place")
                    return
                await draf_bot.do(warpgate.warp_in(objUnitType, placement))


    
        #for _key,_intValue in objUnitCntDict
        #    if _key == intZealotsCnt:              
    #async def resolveUnitsToBuild(self):

        