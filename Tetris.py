from tools import *

import cv2
import numpy as np
import random
import time

class Tetris:
    def __init__(self):
        self.WINDOW_NAME = "Tetris"
        self.RATIO = 20
        self.CENTER_POINT_X = 340
        self.CENTER_POINT_Y = 220
        self.COLOR = {
            "black" : [0, 0, 0],
            "white" : [255, 255, 255],
            "blue" : [255, 148, 41],
            "red" : [0, 0, 255],
            "yellow" : [5, 209, 255],
            "green" : [119, 202, 2],
            "purple" : [255, 0, 136],
            "pink" : [189, 122, 255],
        }
        self.BOARD = np.uint8(np.zeros([20, 10, 3]))
        self.COMMANDS = {
            "rotate" : [ord("w"), ord("W")],
            "up" : [ord("w"), ord("W")],
            "hard drop" : [32],
            "space" : [32],
            "left" : [ord("a"), ord("A")],
            "right" : [ord("d"), ord("D")],
            "down" : [ord("s"), ord("S")],
            "hold" : [ord("q"), ord("Q")],
            "quit" : [27],
            "back" : [ord("b"), ord("B")],
        }
        self.ALL_PIECES = ["O", "I", "S", "Z", "L", "J", "T"]

        self.loadConfiguration()

        self.border = np.uint8(127 - np.zeros([20, 1, 3]))
        self.border_ = np.uint8(127 - np.zeros([1, 34, 3]))
        self.score = 0
    
    def loadConfiguration(self):
        config = {
            "speed" : 1,
            "isZen" : False
        }
        result = loadJsonFile("config.json")
        config = result if result else config
        self.speed = config["speed"]
        self.isZen = config["isZen"]
        self.timer = 120
    
    def saveConfiguration(self, data):
        pass
    
    def loadRecord(self):
        record = []
        result = loadJsonFile("record.json")
        record = result if result else record
        return record
    
    def saveRecord(self, record):
        dumpJsonFile(record, "record.json")

    def getRandomPieceCode(self):
        return random.choice(self.ALL_PIECES)

    def getPieceInfo(self, pieceCode):
        if pieceCode == "I":
            coords = np.array([[0, 3], [0, 4], [0, 5], [0, 6]])
            color = self.COLOR["white"]
        elif pieceCode == "T":
            coords = np.array([[1, 3], [1, 4], [1, 5], [0, 4]])
            color = self.COLOR["purple"]
        elif pieceCode == "L":
            coords = np.array([[1, 3], [1, 4], [1, 5], [0, 5]])
            color = self.COLOR["pink"]
        elif pieceCode == "J":
            coords = np.array([[1, 3], [1, 4], [1, 5], [0, 3]])
            color = self.COLOR["blue"]
        elif pieceCode == "S":
            coords = np.array([[1, 5], [1, 4], [0, 3], [0, 4]])
            color = self.COLOR["green"]
        elif pieceCode == "Z":
            coords = np.array([[1, 3], [1, 4], [0, 4], [0, 5]])
            color = self.COLOR["red"]
        else:
            coords = np.array([[0, 4], [0, 5], [1, 4], [1, 5]])
            color = self.COLOR["yellow"]

        return coords, color

    def areMatched(self, key, command):
        return key in self.COMMANDS[command]

    def changeOption(self):
        optionPage = cv2.imread("option-level.png")
        cv2.imshow(self.WINDOW_NAME, optionPage)
        key = cv2.waitKey()
        while(key != self.COMMANDS["back"]):
            key = cv2.waitKey()
        return "back"

    def showRank(self):
        rankPage = cv2.imread("rank-begin.png")
        cv2.imshow(self.WINDOW_NAME, rankPage)
        key = cv2.waitKey()
        while(key != self.COMMANDS["back"]):
            key = cv2.waitKey()
        return "back"

    def showRule(self):
        rulePage = cv2.imread("rule.png")
        cv2.imshow(self.WINDOW_NAME, rulePage)
        key = cv2.waitKey()
        while(key != self.COMMANDS["back"]):
            key = cv2.waitKey()
        return "back"

    def playGame(self):
        def display(coords, color, nextPiece, heldPiece):
            # game
            dummy = self.BOARD.copy()
            dummy[coords[:,0], coords[:,1]] = color

            right = np.uint8(np.zeros([20, 10, 3]))
            right[nextPiece[0][:,0] + 2, nextPiece[0][:,1]] = nextPiece[1]
            left = np.uint8(np.zeros([20, 10, 3]))
            left[heldPiece[0][:,0] + 2, heldPiece[0][:,1]] = heldPiece[1]

            dummy = np.concatenate((self.border, left, self.border, dummy, self.border, right, self.border), 1)
            dummy = np.concatenate((self.border_, dummy, self.border_), 0)
            dummy = dummy.repeat(self.RATIO, 0).repeat(self.RATIO, 1)
            dummy = cv2.putText(dummy, str(self.score), (520, 200), cv2.FONT_HERSHEY_DUPLEX, 1, [0, 0, 255], 2)

            # side
            timerText = "oo" if self.isZen else timer-1
            dummy = cv2.putText(dummy, f"time: {timerText}", (45, 200), cv2.FONT_HERSHEY_DUPLEX, 0.6, self.COLOR["white"])

            cv2.imshow(self.WINDOW_NAME, dummy)
            return cv2.waitKey(int(1000/self.speed))

        def eliminate():
            lines = 0
            for line in range(20):
                if np.all([np.any(pos != 0) for pos in self.BOARD[line]]):
                    lines += 1
                    self.BOARD[1:line+1] = self.BOARD[:line]
            if lines == 0 :
                return

            if lines == 1:
                self.score += 40
            elif lines == 2:
                self.score += 100
            elif lines == 3:
                self.score += 300
            elif lines == 4:
                self.score += 1200

        isGaming = True
        isPlaced = False
        isHardDrop = False
        switch = False
        heldPieceCode = ""
        nextPieceCode = self.getRandomPieceCode()
        timer = self.timer
        startTimeStamp = time.time()

        executingTimeStamp1 = startTimeStamp

        while isGaming:
            executingTimeStamp2 = time.time()
            if not self.isZen:
                if executingTimeStamp2 - startTimeStamp >= self.timer:
                    break
            
            if switch: # 交換
                heldPieceCode, currentPieceCode = currentPieceCode, heldPieceCode
                switch = False
            else:
                currentPieceCode = nextPieceCode
                nextPieceCode = self.getRandomPieceCode()

            if heldPieceCode == "":
                heldPiece = np.array([[0, 0]]), [0, 0, 0]
            else:
                heldPiece = self.getPieceInfo(heldPieceCode)
            nextPiece = self.getPieceInfo(nextPieceCode)
            coords, color = self.getPieceInfo(currentPieceCode)

            if currentPieceCode == "I":
                topLeft = [-2, 3]
                
            if np.any(self.BOARD[coords[:,0], coords[:,1]] != 0):
                break
                
            while True:
                # timer
                executingTimeStamp2 = time.time()
                if not self.isZen:
                    if executingTimeStamp2 - startTimeStamp >= self.timer:
                        break
                if executingTimeStamp2 - executingTimeStamp1 >= 1:
                    timer -= 1
                    executingTimeStamp1 = executingTimeStamp2

                key = display(coords, color, nextPiece, heldPiece)
                dummy = coords.copy()

                if self.areMatched(key, "left"):
                    if np.min(coords[:,1]) > 0:
                        coords[:,1] -= 1
                    if currentPieceCode == "I":
                        topLeft[1] = 0 if topLeft[1]<1 else topLeft[1]-1
                        
                elif self.areMatched(key, "right"):
                    if np.max(coords[:,1]) < 9:
                        coords[:,1] += 1
                        if currentPieceCode == "I":
                            topLeft[1] += 1

                elif self.areMatched(key, "rotate"):
                    if currentPieceCode != "I" and currentPieceCode != "O":
                        if coords[1,1] > 0 and coords[1,1] < 9:
                            arr = coords[1] - 1 + np.array([[[x, y] for y in range(3)] for x in range(3)])
                            pov = coords - coords[1] + 1
                    elif currentPieceCode == "I":
                        arr = topLeft + np.array([[[x, y] for y in range(4)] for x in range(4)])
                        pov = np.array([np.where(np.logical_and(arr[:,:,0] == pos[0], arr[:,:,1] == pos[1])) for pos in coords])
                        pov = np.array([k[0] for k in np.swapaxes(pov, 1, 2)])

                    if currentPieceCode != "O":
                        arr = np.rot90(arr, -1)
                        coords = arr[pov[:,0], pov[:,1]]
                
                elif self.areMatched(key, "hard drop"):
                    isHardDrop = True

                elif self.areMatched(key, "hold"):
                    if heldPieceCode == "":
                        heldPieceCode = currentPieceCode
                    else:
                        switch = True
                    break

                elif self.areMatched(key, "quit"):
                    isGaming = False
                    break
                    
                # 處理方塊重疊或超線
                if np.max(coords[:,0]) < 20 and np.min(coords[:,0]) >= 0:
                    if currentPieceCode == "I" and (np.max(coords[:,1]) >= 10 or np.min(coords[:,1]) < 0):
                        coords = dummy.copy()
                    else:
                        if np.any(self.BOARD[coords[:,0], coords[:,1]] != 0):
                            coords = dummy.copy()
                else:
                    coords = dummy.copy()
                    
                if isHardDrop:
                    while not isPlaced:
                        if np.max(coords[:,0]) != 19:  # 放在其他方塊上
                            for pos in coords:
                                if not np.array_equal(self.BOARD[pos[0] + 1, pos[1]], [0, 0, 0]):
                                    isPlaced = True
                                    break
                        else:  # 放在地上
                            isPlaced = True
                        if isPlaced:
                            break
                        coords[:,0] += 1
                        if currentPieceCode == "I":
                            topLeft[0] += 1  
                    isHardDrop = False
                else:
                    if np.max(coords[:,0]) != 19:  # 確認方塊是否需要被放置
                        for pos in coords:
                            if not np.array_equal(self.BOARD[pos[0] + 1, pos[1]], [0, 0, 0]):
                                isPlaced = True
                                break
                    else:
                        isPlaced = True
                    
                if isPlaced:
                    for pos in coords:
                        self.BOARD[tuple(pos)] = color
                    isPlaced = False
                    break

                # 下降一格
                coords[:,0] += 1
                if currentPieceCode == "I":
                    topLeft[0] += 1
            
            # 消除和得分
            eliminate()

    def endGame(self):
        timestamp = time.strftime("%Y/%m/%d, %H:%M:%S", time.localtime())
        record = self.loadRecord()
        newRecord = {
            "time" : timestamp,
            "score" : self.score,
        }
        record.append(newRecord)
        record.sort(key=lambda r: r["score"], reverse=True)
        self.saveRecord(record)
        for idx, r in enumerate(record):
            if r["time"] == timestamp:
                print(f"Rank: {idx+1}")
    
    def startGame(self):
        homePage = cv2.imread("home.png")
        cv2.imshow(self.WINDOW_NAME, homePage)
        key = cv2.waitKey()
        click = 0
        while(key):
            if (key == self.COMMANDS["up"]):
                click -= 1
                print(click)
            elif (key == self.COMMANDS["down"]):
                click +=1
                print(click)
            elif (key == self.COMMANDS["space"]):
                print("space")
                value = "none"
                if(click %4 == 1):
                    value = self.changeOption()
                    if(value == "back"):
                         self.startGame()
                elif(click %4 == 2):
                    value =  self.showRank()
                    if(value == "back"):
                         self.startGame()
                elif(click %4 == 3):
                    value =  self.showRule()
                    if(value == "back"):
                         self.startGame()
                elif(click %4 == 0):
                     self.playGame()
        key = cv2.waitKey()

    def play(self):
        # self.startGame()
        self.playGame()
        self.endGame()

if __name__ == "__main__":
    Tetris().play()