import cv2
import numpy as np
from random import choice

# Controls the speed of the tetris pieces
# 控制方塊落下的速度
SPEED = 1 

# Make a board
# 建立遊戲視窗
board = np.uint8(np.zeros([20, 10, 3]))

# Initialize some variables
# 變數初始化
quit = False
place = False
drop = False
switch = False
held_piece = ""
flag = 0
score = 0

# All the tetris pieces
# 所有種類的俄羅斯方塊
next_piece = choice(["O", "I", "S", "Z", "L", "J", "T"])

def get_info(piece):
    if piece == "I":
        coords = np.array([[0, 3], [0, 4], [0, 5], [0, 6]])
        color = [255, 155, 15]
    elif piece == "T":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 4]])
        color = [138, 41, 175]
    elif piece == "L":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 5]])
        color = [2, 91, 227]
    elif piece == "J":
        coords = np.array([[1, 3], [1, 4], [1, 5], [0, 3]])
        color = [198, 65, 33]
    elif piece == "S":
        coords = np.array([[1, 5], [1, 4], [0, 3], [0, 4]])
        color = [55, 15, 215]
    elif piece == "Z":
        coords = np.array([[1, 3], [1, 4], [0, 4], [0, 5]])
        color = [1, 177, 89]
    else:
        coords = np.array([[0, 4], [0, 5], [1, 4], [1, 5]])
        color = [2, 159, 227]

    return coords, color


def display(board, coords, color, next_info, held_info, score, SPEED):
    # Generates the display
    # 顯示遊戲畫面?

    border = np.uint8(127 - np.zeros([20, 1, 3]))
    border_ = np.uint8(127 - np.zeros([1, 34, 3]))

    dummy = board.copy()
    dummy[coords[:,0], coords[:,1]] = color

    right = np.uint8(np.zeros([20, 10, 3]))
    right[next_info[0][:,0] + 2, next_info[0][:,1]] = next_info[1]
    left = np.uint8(np.zeros([20, 10, 3]))
    left[held_info[0][:,0] + 2, held_info[0][:,1]] = held_info[1]

    dummy = np.concatenate((border, left, border, dummy, border, right, border), 1)
    dummy = np.concatenate((border_, dummy, border_), 0)
    dummy = dummy.repeat(20, 0).repeat(20, 1)
    dummy = cv2.putText(dummy, str(score), (520, 200), cv2.FONT_HERSHEY_DUPLEX, 1, [0, 0, 255], 2)

    # Instructions for the player
    # 顯示遊戲介紹
    dummy = cv2.putText(dummy, "A - move left", (45, 200), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "D - move right", (45, 225), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "S - move down", (45, 250), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "W - hard drop", (45, 275), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "J - rotate left", (45, 300), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "L - rotate right", (45, 325), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])
    dummy = cv2.putText(dummy, "I - hold", (45, 350), cv2.FONT_HERSHEY_DUPLEX, 0.6, [0, 0, 255])

    cv2.imshow("Tetris", dummy)
    key = cv2.waitKey(int(1000/SPEED))

    return key

if __name__ == "__main__":
    while not quit:
        # Check if user wants to swap held and current pieces
        # 先確認玩家有要對方塊交換(做動作)
        if switch:
           # swap held_piece and current_piece
           # 切換方塊
            held_piece, current_piece = current_piece, held_piece
            switch = False
        else:
            # Generates the next piece and updates the current piece
            # 生成下一個方塊 並 更新現在的方塊
            current_piece = next_piece
            next_piece = choice(["I", "T", "L", "J", "Z", "S", "O"])
        
        if flag > 0:
            flag -= 1
        
        # Determines the color and position of the current, next, and held pieces
        # 決定現在的方塊、下一個方塊的位置及顏色
        if held_piece == "":
            held_info = np.array([[0, 0]]), [0, 0, 0]
        else:
           held_info = get_info(held_piece)
        
        next_info = get_info(next_piece)

        coords, color = get_info(current_piece)
        if current_piece == "I":
            top_left = [-2, 3]
            
        if not np.all(board[coords[:,0], coords[:,1]] == 0):
            break
            
        while True:
            # Shows the board and gets the key press
            # 顯示畫面 及 取得按鍵
            key = display(board, coords, color, next_info, held_info, score, SPEED)
            # Create a copy of the position
            # 複製位置
            dummy = coords.copy()
        
            if key == ord("a"):
                # Moves the piece left if it isn't against the left wall
                # 若方塊還沒貼左壁，則將方塊左移
                if np.min(coords[:,1]) > 0:
                    coords[:,1] -= 1
                if current_piece == "I":
                    top_left[1] -= 1
                    
            elif key == ord("d"):
                # Moves the piece right if it isn't against the right wall
                # 若方塊還沒貼右壁，則將方塊右移
                if np.max(coords[:,1]) < 9:
                    coords[:,1] += 1
                    if current_piece == "I":
                        top_left[1] += 1
                        
            elif key == ord("j") or key == ord("l"):
                # Rotation mechanism
                # 旋轉機制
                # arr is the array of nearby points which get rotated and pov is the indexes of the blocks within arr
                # arr 是選轉的座標點? pov 是索引 
                if current_piece != "I" and current_piece != "O":
                    if coords[1,1] > 0 and coords[1,1] < 9:
                        arr = coords[1] - 1 + np.array([[[x, y] for y in range(3)] for x in range(3)])
                        pov = coords - coords[1] + 1
                    
                elif current_piece == "I":
                    # The straight piece has a 4x4 array, so it needs seperate code
                    # 直條的方塊有4x4陣列 所以需要分開??
                    arr = top_left + np.array([[[x, y] for y in range(4)] for x in range(4)])
                    pov = np.array([np.where(np.logical_and(arr[:,:,0] == pos[0], arr[:,:,1] == pos[1])) for pos in coords])
                    pov = np.array([k[0] for k in np.swapaxes(pov, 1, 2)])
            
                # Rotates the array and repositions the piece to where it is now
                # 選轉陣列 並 重定位
                if current_piece != "O":
                    if key == ord("j"):
                        arr = np.rot90(arr, -1)
                    else:
                        arr = np.rot90(arr)
                    coords = arr[pov[:,0], pov[:,1]]
            
            elif key == ord("w"):
                # Hard drop set to true
                # 將 方塊直接落下 設成true
                drop = True
            elif key == ord("i"):
                # Goes out of the loop and tells the program to switch held and current pieces
                # 跳出迴圈 並 切換當前的方塊
                if flag == 0:
                    if held_piece == "":
                        held_piece = current_piece
                    else:
                        switch = True
                    flag = 2
                    break
            elif key == 8 or key == 27:
                quit = True
                break
                
            # Checks if the piece is overlapping with other pieces or if it's outside the board, and if so, changes the position to the position before anything happened
            # 檢查方塊 "是否重疊" 或者 "超出格子"，若是，則在發生任何事情之前先改變位置
            if np.max(coords[:,0]) < 20 and np.min(coords[:,0]) >= 0:
                if not (current_piece == "I" and (np.max(coords[:,1]) >= 10 or np.min(coords[:,1]) < 0)):
                    if not np.all(board[coords[:,0], coords[:,1]] == 0):
                        coords = dummy.copy()
                else:
                    coords = dummy.copy()
            else:
                coords = dummy.copy()
                
            if drop:
                # Every iteration of the loop moves the piece down by 1 and if the piece is resting on the ground or another piece, then it stops and places it
                # 每個迴圈都會將方塊下降一格，直到 "到底 或者 "碰到其他方塊"，則放置
                while not place:
                    if np.max(coords[:,0]) != 19:
                        # Checks if the piece is resting on something
                        # 確認方塊靠在某東西上，放置
                        for pos in coords:
                            if not np.array_equal(board[pos[0] + 1, pos[1]], [0, 0, 0]):
                                place = True
                                break
                    else:
                        # If the position of the piece is at the ground level, then it places
                        # 若方塊落到地面，放置
                        place = True
                    
                    if place:
                        break
                    
                    # Keeps going down and checking when the piece needs to be placed
                    # 繼續下降直到方塊需要被放置
                    coords[:,0] += 1
                    score += 1
                    if current_piece == "I":
                        top_left[0] += 1
                        
                drop = False
            
            else:
                # Checks if the piece needs to be placed
                # 確認方塊是否需要被放置
                if np.max(coords[:,0]) != 19:
                    for pos in coords:
                        if not np.array_equal(board[pos[0] + 1, pos[1]], [0, 0, 0]):
                            place = True
                            break
                else:
                    place = True
                
            if place:
                # Places the piece where it is on the board
                # 放置方塊
                for pos in coords:
                    board[tuple(pos)] = color
                    
                # Resets place to False
                # 將判斷是否為需要放置的變數改回false
                place = False
                break

            # Moves down by 1
            # 下降一格

            coords[:,0] += 1
            if key == ord("s"):
                score += 1
            if current_piece == "I":
                top_left[0] += 1
        
        # Clears lines and also counts how many lines have been cleared and updates the score
        # 清除滿格的那列 並 更新分數
                
        lines = 0
                
        for line in range(20):
            if np.all([np.any(pos != 0) for pos in board[line]]):
                lines += 1
                board[1:line+1] = board[:line]
                        
        if lines == 1:
            score += 40
        elif lines == 2:
            score += 100
        elif lines == 3:
            score += 300
        elif lines == 4:
            score += 1200