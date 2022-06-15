import cv2
import numpy as np
import random


BOARD = np.uint8(np.zeros([20, 10, 3]))
SPEED = 1 
COMMANDS = {
    "rotate" : [ord("w"), ord("W")],
    "hard drop" : [32],
    "left" : [ord("a"), ord("A")],
    "right" : [ord("d"), ord("D")],
    "down" : [ord("s"), ord("S")],
    "hold" : [ord("q"), ord("Q")],
    "quit" : [27]
}
ALL_PIECES = ["O", "I", "S", "Z", "L", "J", "T"]
isGaming = True
isPlaced = False
isHardDrop = False
switch = False
heldPieceCode = ""
flag = 0
score = 0
nextPieceCode = random.choice(ALL_PIECES)

def areMatched(key, command):
    return key in COMMANDS[command]

def getPieceInfo(pieceCode):
    if pieceCode == "I":
        coords = np.array([[0, 3], [0, 4], [0, 5], [0, 6]])
        color = [255, 155, 15]
    elif pieceCode == "T":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 4]])
        color = [138, 41, 175]
    elif pieceCode == "L":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 5]])
        color = [2, 91, 227]
    elif pieceCode == "J":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 3]])
        color = [198, 65, 33]
    elif pieceCode == "S":
        coords = np.array([[1, 5], [1, 4], [0, 3], [0, 4]])
        color = [55, 15, 215]
    elif pieceCode == "Z":
        coords = np.array([[1, 3], [1, 4], [0, 4], [0, 5]])
        color = [1, 177, 89]
    else:
        coords = np.array([[0, 4], [0, 5], [1, 4], [1, 5]])
        color = [2, 159, 227]

    return coords, color


def display(BOARD, coords, color, nextPiece, heldPiece, score, SPEED):
    # main
    border = np.uint8(127 - np.zeros([20, 1, 3]))
    border_ = np.uint8(127 - np.zeros([1, 34, 3]))

    dummy = BOARD.copy()
    dummy[coords[:,0], coords[:,1]] = color

    right = np.uint8(np.zeros([20, 10, 3]))
    right[nextPiece[0][:,0] + 2, nextPiece[0][:,1]] = nextPiece[1]
    left = np.uint8(np.zeros([20, 10, 3]))
    left[heldPiece[0][:,0] + 2, heldPiece[0][:,1]] = heldPiece[1]

    dummy = np.concatenate((border, left, border, dummy, border, right, border), 1)
    dummy = np.concatenate((border_, dummy, border_), 0)
    dummy = dummy.repeat(20, 0).repeat(20, 1)
    dummy = cv2.putText(dummy, str(score), (520, 200), cv2.FONT_HERSHEY_DUPLEX, 1, [0, 0, 255], 2)

    # side
    dummy = cv2.putText(dummy, "A - move left", (45, 200), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "D - move right", (45, 225), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "S - move down", (45, 250), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "Space - hard drop", (45, 275), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "W - rotate", (45, 300), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "Q - hold", (45, 350), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])

    cv2.imshow("Tetris", dummy)
    return cv2.waitKey(int(1000/SPEED))

def endGame():
    print(score)

if __name__ == "__main__":
    while isGaming:
        if switch: # 交換
            heldPieceCode, currentPieceCode = currentPieceCode, heldPieceCode
            switch = False
        else:
            currentPieceCode = nextPieceCode
            nextPieceCode = random.choice(["I", "T", "L", "J", "Z", "S", "O"])
        
        if flag > 0:
            flag -= 1
        
        # 方塊顏色和位置
        if heldPieceCode == "":
            heldPiece = np.array([[0, 0]]), [0, 0, 0]
        else:
           heldPiece = getPieceInfo(heldPieceCode)
        
        nextPiece = getPieceInfo(nextPieceCode)

        coords, color = getPieceInfo(currentPieceCode)
        if currentPieceCode == "I":
            topLeft = [-2, 3]
            
        if not np.all(BOARD[coords[:,0], coords[:,1]] == 0):
            break
            
        while True:
            key = display(BOARD, coords, color, nextPiece, heldPiece, score, SPEED)
            dummy = coords.copy()

            if areMatched(key, "left"):
                if np.min(coords[:,1]) > 0:
                    coords[:,1] -= 1
                if currentPieceCode == "I":
                    topLeft[1] -= 1
                    
            elif areMatched(key, "right"):
                if np.max(coords[:,1]) < 9:
                    coords[:,1] += 1
                    if currentPieceCode == "I":
                        topLeft[1] += 1

            elif areMatched(key, "rotate"):
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
            
            elif areMatched(key, "hard drop"):
                isHardDrop = True

            elif areMatched(key, "hold"):
                if flag == 0:
                    if heldPieceCode == "":
                        heldPieceCode = currentPieceCode
                    else:
                        switch = True
                    flag = 2
                    break

            elif areMatched(key, "quit"):
                isGaming = False
                break
                
            # 處理方塊重疊或超線
            if np.max(coords[:,0]) < 20 and np.min(coords[:,0]) >= 0:
                if currentPieceCode == "I" and (np.max(coords[:,1]) >= 10 or np.min(coords[:,1]) < 0):
                    coords = dummy.copy()
                else:
                    if np.any(BOARD[coords[:,0], coords[:,1]] != 0):
                        coords = dummy.copy()
            else:
                coords = dummy.copy()
                
            if isHardDrop:
                while not isPlaced:
                    if np.max(coords[:,0]) != 19:  # 放在其他方塊上
                        for pos in coords:
                            if not np.array_equal(BOARD[pos[0] + 1, pos[1]], [0, 0, 0]):
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
                        if not np.array_equal(BOARD[pos[0] + 1, pos[1]], [0, 0, 0]):
                            isPlaced = True
                            break
                else:
                    isPlaced = True
                
            if isPlaced:
                for pos in coords:
                    BOARD[tuple(pos)] = color
                isPlaced = False
                break

            # 下降一格
            coords[:,0] += 1
            if currentPieceCode == "I":
                topLeft[0] += 1
        
        # 消除和得分
        lines = 0
        for line in range(20):
            if np.all([np.any(pos != 0) for pos in BOARD[line]]):
                lines += 1
                BOARD[1:line+1] = BOARD[:line]
        if lines == 1:
            score += 40
        elif lines == 2:
            score += 100
        elif lines == 3:
            score += 300
        elif lines == 4:
            score += 1200
    
    endGame()