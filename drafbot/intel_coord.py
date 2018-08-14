import sc2
from sc2 import run_game, maps, Race, Difficulty, position
from sc2.player import Bot, Computer
from sc2.constants import *
import random
import cv2
import numpy as np
import time
#from sc2.data import race_townhalls

# the point of this class is to set all the attack type options for the units to attack.

class IntelCoord():
    intSimpleScout = 0 
    #intScoutTag = None
    listScoutTags = []
    DrawDict = {
                     NEXUS: [5, (0, 255, 0)],
                     PYLON: [2, (20, 235, 0)],
                     PROBE: [1, (55, 200, 0)],
                     ASSIMILATOR: [2, (55, 200, 0)],
                     GATEWAY: [3, (200, 100, 0)],
                     CYBERNETICSCORE: [3, (150, 150, 0)],
                     STARGATE: [3, (255, 0, 0)],
                     VOIDRAY: [2, (255, 100, 0)],
                    }
    listTrainData = []
    objFlippedCVMap = None
    

    def select_target(self,draf_bot):
        if draf_bot.known_enemy_structures.exists:
            return random.choice(draf_bot.known_enemy_structures).position

        return draf_bot.enemy_start_locations[0]

    async def intel(self,draf_bot):
        game_data = np.zeros((draf_bot.game_info.map_size[1], draf_bot.game_info.map_size[0], 3), np.uint8)
        for unit_type in self.DrawDict:
            for unit in draf_bot.units(unit_type).ready:
                pos = unit.position
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), int(unit.radius) * self.DrawDict[unit_type][0], self.DrawDict[unit_type][1], -1)            

        main_base_names = ["nexus", "commandcenter", "hatchery"]
        for enemy_building in draf_bot.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() not in main_base_names:
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), 5, (200, 50, 212), -1)
        for enemy_building in draf_bot.known_enemy_structures:
            pos = enemy_building.position
            if enemy_building.name.lower() in main_base_names:
                cv2.circle(game_data, (int(pos[0]), int(pos[1])), 15, (0, 0, 255), -1)

        for enemy_unit in draf_bot.known_enemy_units:

            if not enemy_unit.is_structure:
                worker_names = ["probe",
                                "scv",
                                "drone"]
                # if that unit is a PROBE, SCV, or DRONE... it's a worker
                pos = enemy_unit.position
                if enemy_unit.name.lower() in worker_names:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 1, (55, 0, 155), -1)
                else:
                    cv2.circle(game_data, (int(pos[0]), int(pos[1])), 3, (50, 0, 215), -1)
        
        if len(self.listScoutTags) > 0:
            for _intScoutTag in self.listScoutTags:
                if draf_bot.units.find_by_tag(_intScoutTag) is not None:
                    _posScout = draf_bot.units.find_by_tag(_intScoutTag).position
                    #print("tag ==> " + str(self.objScout.tag))
                    #print("posScout ==> " + str(_posScout))
                    cv2.circle(game_data, (int(_posScout[0]), int(_posScout[1])), 1, (255, 255, 255), -1)

        self.objFlippedCVMap = cv2.flip(game_data, 0)        
        resized = cv2.resize(self.objFlippedCVMap, dsize=None, fx=2, fy=2)
        cv2.imshow('Intel', resized)
        cv2.waitKey(1)
        self.appendTrainData([self.objFlippedCVMap])

    def appendTrainData(self,objData):
        self.listTrainData.append(objData)

    def saveTrainData(self):
        np.save("G:\dev2\OPIMDemo\\drafbot\\train_data\\{}.npy".format(str(int(time.time()))), np.array(self.listTrainData))
        #np.savetxt("G:\dev2\OPIMDemo\\drafbot\\train_data\\{}.txt".format(str(int(time.time()))), np.array(self.listTrainData))

    def haveVisibleEnemyOffUnit(self, draf_bot):
        intNumEnemyUnitsStructures = len(draf_bot.known_enemy_units)
        intNumEnemyStructures = len(draf_bot.known_enemy_units)
        if len(draf_bot.known_enemy_units) > 0:
            return draf_bot.known_enemy_units


    def random_location_variance(self, draf_bot, enemy_start_location):
        x = enemy_start_location[0]
        y = enemy_start_location[1]

        x += ((random.randrange(-20, 20))/100) * enemy_start_location[0]
        y += ((random.randrange(-20, 20))/100) * enemy_start_location[1]

        if x < 0:
            x = 0
        if y < 0:
            y = 0
        if x > draf_bot.game_info.map_size[0]:
            x = draf_bot.game_info.map_size[0]
        if y > draf_bot.game_info.map_size[1]:
            y = draf_bot.game_info.map_size[1]

        go_to = position.Point2(position.Pointlike((x,y)))
        return go_to
    
    #This function will send a probe to scout. To resend a probe to scout, use 
    #resendSimpleScout
    async def sendSimpleScout(self,draf_bot):
        if self.intSimpleScout < 1:
            _EnemyLocation = draf_bot.enemy_start_locations[0]
            _objScout = draf_bot.units(PROBE).ready.random
            self.listScoutTags.append(_objScout.tag)
            _scout_dest = self.random_location_variance(draf_bot,_EnemyLocation)
            #print("Scout Destinatino ==>" + str(_scout_dest))
            await draf_bot.do(_objScout.move(_scout_dest))
            self.intSimpleScout = self.intSimpleScout + 1

    async def resendSimpleScout(self):
        self.intSimpleScout = 0

    async def sendScout(self,draf_bot):   
        if draf_bot.units(NEXUS).ready.exists > 1:
            self.sendObserver(draf_bot)
        else:
            self.sendSimpleScout(draf_bot)

    async def sendObserver(self,draf_bot):
        if len(draf_bot.units(OBSERVER)) > 0:
            scout = draf_bot.units(OBSERVER)[0]
            if scout.is_idle:
                enemy_location = draf_bot.enemy_start_locations[0]
                move_to = draf_bot.random_location_variance(enemy_location)
                print(move_to)
                self.listScoutTags.append(_objScout.tag)
                await draf_bot.do(scout.move(move_to))

        else:
            for rf in draf_bot.units(ROBOTICSFACILITY).ready.noqueue:
                if draf_bot.can_afford(OBSERVER) and draf_bot.supply_left > 0:
                    await draf_bot.do(rf.train(OBSERVER))
        
