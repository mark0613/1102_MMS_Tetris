from tools import *

import cv2
import numpy as np
import random
import time
import math

class Tetris:
    def __init__(self):
        self.WINDOW_NAME = "Tetris"
        self.RATIO = 20
        self.ARROW = [
            [(170,90), (170,140), (220,115)],
            [(170,170), (170,220), (220,195)],
            [(170,250), (170,300), (220,275)],
            [(170,330), (170,380), (220,355)],
        ]
        self.COLOR = {
            "black" : [0, 0, 0],
            "white" : [255, 255, 255],
            "blue" : [255, 148, 41],
            "blue-light" : [255, 190, 183],
            "red" : [0, 0, 255],
            "yellow" : [5, 209, 255],
            "green" : [119, 202, 2],
            "purple" : [255, 0, 136],
            "pink" : [189, 122, 255],
        }
        self.COMMANDS = {
            "rotate" : [ord("w"), ord("W")],
            "up" : [ord("w"), ord("W")],
            "hard drop" : [32],
            "confirm" : [32],
            "left" : [ord("a"), ord("A")],
            "right" : [ord("d"), ord("D")],
            "down" : [ord("s"), ord("S")],
            "hold" : [ord("q"), ord("Q")],
            "quit" : [27],
            "back" : [ord("b"), ord("B")],
        }
        self.MENU_OPTIONS = [
            "start",
            "options",
            "ranking",
            "rule",
        ]
        self.TIME_OPTIONS = [
            "level",
            "mode"
        ]
        self.BOARD = np.uint8(np.zeros([20, 10, 3]))
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

    def showMenu(self):
        homePage = cv2.imread("home.png")
        pt = [np.array(self.ARROW[0])]
        cv2.drawContours(homePage, pt, 0, self.COLOR["red"], -1)
        cv2.imshow(self.WINDOW_NAME, homePage)
        key = cv2.waitKey()
        optionValue = 0
        while True:
            if self.areMatched(key, "up") or self.areMatched(key, "down"):
                if self.areMatched(key, "up"):
                    optionValue -= 1
                elif self.areMatched(key, "down"):
                    optionValue += 1

                pt = [np.array(self.ARROW[optionValue%4])]
                homePage[90:380, 170:220] = [0, 0, 0]
                cv2.drawContours(homePage, pt, 0, self.COLOR["red"], -1)
                cv2.imshow(self.WINDOW_NAME, homePage)
                key = cv2.waitKey()

            if self.areMatched(key, "confirm"):
                return self.MENU_OPTIONS[optionValue]

            if self.areMatched(key, "quit"):
                return "quit"

    def showModeOptions(self):
        optionModePage = cv2.imread("option-mode.png")
        pt = [np.array(self.ARROW[1])]
        cv2.drawContours(optionModePage, pt, 0, self.COLOR["red"], -1)
        cv2.imshow(self.WINDOW_NAME, optionModePage)
        key = cv2.waitKey()
        optionValue = 0
        while True:
            if self.areMatched(key, "up") or self.areMatched(key, "down"):
                if self.areMatched(key, "up"):
                    optionValue -= 1
                elif self.areMatched(key, "down"):
                    optionValue += 1

                pt = [np.array(self.ARROW[optionValue%2+1])]
                optionModePage[90:380, 170:220] = [0, 0, 0]
                cv2.drawContours(optionModePage, pt, 0, self.COLOR["red"], -1)
                cv2.imshow(self.WINDOW_NAME, optionModePage)
                key = cv2.waitKey()

            if self.areMatched(key, "confirm"):
                return
            if self.areMatched(key, "quit"):
                return "quit"

    def showLevelOptions(self):
        optionLevelPage = cv2.imread("option-level.png")
        pt = [np.array(self.ARROW[0])]
        cv2.drawContours(optionLevelPage, pt, 0, self.COLOR["red"], -1)
        cv2.imshow(self.WINDOW_NAME, optionLevelPage)
        key = cv2.waitKey()
        optionValue = 0
        while True:
            if self.areMatched(key, "up") or self.areMatched(key, "down"):
                if self.areMatched(key, "up"):
                    optionValue -= 1
                elif self.areMatched(key, "down"):
                    optionValue += 1

                pt = [np.array(self.ARROW[optionValue%4])]
                optionLevelPage[90:380, 170:220] = [0, 0, 0]
                cv2.drawContours(optionLevelPage, pt, 0, self.COLOR["red"], -1)
                cv2.imshow(self.WINDOW_NAME, optionLevelPage)
                key = cv2.waitKey()

            if self.areMatched(key, "confirm"):
                return
            if self.areMatched(key, "quit"):
                return "quit"

    def showOption(self):    
        optionPage = cv2.imread("option.png")
        pt = [np.array(self.ARROW[1])]
        cv2.drawContours(optionPage, pt, 0, self.COLOR["red"], -1)
        cv2.imshow(self.WINDOW_NAME, optionPage)
        key = cv2.waitKey()
        optionValue = 0
        while True:
            if self.areMatched(key, "up") or self.areMatched(key, "down"):
                if self.areMatched(key, "up"):
                    optionValue -= 1
                elif self.areMatched(key, "down"):
                    optionValue += 1

                pt = [np.array(self.ARROW[optionValue%2+1])]
                optionPage[90:380, 170:220] = [0, 0, 0]
                cv2.drawContours(optionPage, pt, 0, self.COLOR["red"], -1)
                cv2.imshow(self.WINDOW_NAME, optionPage)
                key = cv2.waitKey()

            if self.areMatched(key, "confirm"):
                if self.TIME_OPTIONS[optionValue] == "level":
                    self.showLevelOptions()
                elif self.TIME_OPTIONS[optionValue] == "mode":
                    self.showModeOptions()
            if self.areMatched(key, "quit"):
                return "quit"

    def showRankingRecord(self):
        rankingRecord = self.loadRecord()
        page = 0
        perPage = 10
        while True:
            rankingPage = cv2.imread("rank-begin.png")
            record = rankingRecord[(page-1)*perPage : (page-1)*perPage+perPage]

            if page == 0:
                coords_y = 170
                rankingPage = cv2.imread("rank-begin-p1.png")
                for idx, r in enumerate(rankingRecord[:3]):
                    cv2.putText(rankingPage, f"{idx + 1}", (320, coords_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1.5, self.COLOR["yellow"])
                    cv2.putText(rankingPage, f":", (370, coords_y), cv2.FONT_HERSHEY_TRIPLEX, 1.5, self.COLOR["yellow"])
                    cv2.putText(rankingPage, f"{r['score']}", (410, coords_y), cv2.FONT_HERSHEY_DUPLEX, 1.5, self.COLOR["red"])
                    coords_y += 80
            else:
                coords_y = 110
                for idx, r in enumerate(record):
                    cv2.putText(rankingPage, f"{idx + (page-1)*perPage + 1}", (180, coords_y), cv2.FONT_HERSHEY_TRIPLEX, 0.7, self.COLOR["white"])
                    cv2.putText(rankingPage, f":", (220, coords_y), cv2.FONT_HERSHEY_TRIPLEX, 0.7, self.COLOR["white"])
                    cv2.putText(rankingPage, f"{r['score']}", (240, coords_y), cv2.FONT_HERSHEY_TRIPLEX, 0.7, self.COLOR["red"])
                    cv2.putText(rankingPage, f"{r['time']}", (320, coords_y-2), cv2.FONT_HERSHEY_SIMPLEX, 0.5, self.COLOR["blue-light"])
                    coords_y += 30

            cv2.imshow(self.WINDOW_NAME, rankingPage)
            key = cv2.waitKey()
            if self.areMatched(key, "back"):
                return
            if self.areMatched(key, "left"):
                page = max(page-1, 0)
            if self.areMatched(key, "right"):
                page = min(page+1, math.ceil(len(rankingRecord)/perPage))

    def showRule(self):
        rulePage = cv2.imread("rule.png")
        cv2.imshow(self.WINDOW_NAME, rulePage)
        while True:
            key = cv2.waitKey()
            if self.areMatched(key, "back"):
                return

    def startGame(self):
        while True:
            option = self.showMenu()
            if option == "start":
                return "play"
            elif option == "options":
                self.showOption()
            elif option == "ranking":
                self.showRankingRecord()
            elif option == "rule":
                self.showRule()
            else:
                return "quit"

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
        rankingRecord = self.loadRecord()
        newRecord = {
            "time" : timestamp,
            "score" : self.score,
        }
        rankingRecord.append(newRecord)
        rankingRecord.sort(key=lambda r: r["score"], reverse=True)
        self.saveRecord(rankingRecord)
        for idx, record in enumerate(rankingRecord):
            if record["time"] == timestamp:
                rank = idx+1
        
        if rank == 1:
            idx = 1
            records = rankingRecord[0:3]
        elif rank == len(rankingRecord):
            idx = rank - 2
            records = rankingRecord[-3:]
        else:
            idx = rank - 1
            records = rankingRecord[rank-1:rank+2]

        rankingPage = cv2.imread("rank-end.png")
        coords_y = 170
        for record in records:
            color = self.COLOR["red"] if idx==rank else self.COLOR["white"]
            cv2.putText(rankingPage, f"{idx}", (320, coords_y), cv2.FONT_HERSHEY_SCRIPT_COMPLEX, 1.5, color)
            cv2.putText(rankingPage, f":", (370, coords_y), cv2.FONT_HERSHEY_TRIPLEX, 1.5, color)
            cv2.putText(rankingPage, f"{record['score']}", (410, coords_y), cv2.FONT_HERSHEY_DUPLEX, 1.5, color)
            coords_y += 80
            idx += 1
        cv2.imshow(self.WINDOW_NAME, rankingPage)

        while True:
            key = cv2.waitKey()
            if self.areMatched(key, "back"):
                return "play again"
            if self.areMatched(key, "quit"):
                return "quit"

    def play(self):
        option = self.startGame()
        if option == "quit":
            return
        self.playGame()
        self.endGame()

if __name__ == "__main__":
    Tetris().play()