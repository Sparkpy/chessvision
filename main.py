from PIL import Image
from math import floor
import numpy as np
import cv2 as cv
import table
import morse
import chess
import chess.engine
import requests
# import serial

# s = serial.Serial('COM5', 9600, timeout=1)

corners = []

board = chess.Board()
engine = chess.engine.SimpleEngine.popen_uci("./stockfish.exe")

assist = chess.BLACK

# Given the corner coordinates of the startBoard, crop the image to 512x512 and transform

def cropBoardImage(board, corners):
    newCorners = np.float32([[0,0],[512,0],[0,512],[512,512]]) # Assign Resolution of output
    warpMap = cv.getPerspectiveTransform(np.asarray(corners).astype(np.float32), newCorners) # 2D Transformation of image
    return cv.warpPerspective(board, warpMap,(1280,720))[0:512, 0:512] # Crop image

def drawGrid(img, color=(255,255,255), thickness=2):
    for i in range(0, 513, 64):
        img = cv.line(img, (i, 0), (i, 512), color, thickness)
        img = cv.line(img, (0, i), (512, i), color, thickness)
    return img

def getTile(img, tile=1):
    x = (tile%8) if tile%8!=0 else 8
    y = floor((tile/8)-0.01)+1
    return img[(y*64)-64:y*64, (x*64)-64:x*64]

def boardDifference(ob, nb, beta=5):
    return cv.absdiff(cv.GaussianBlur(ob,(beta, beta), 0), cv.GaussianBlur(nb,(beta, beta), 0))

def makeMove(img):
    averages = []
    first = 0
    second = 0
    third = 0
    for x in range(0, 64):
        tile = getTile(img, x+1)
        averages.append(np.average(tile)) #if everything breaks add .astype(int)
        if averages[x] > averages[first]:
            first = x

    for x in range(0, 64):
        if averages[x] < averages[first] and averages[x] > averages[second]:
            second = x

    for x in range(0, 64):
        if averages[x] < averages[first] and averages[x] < averages[second] and averages[x] > averages[third]:
            third = x
    
    print(averages)
    # Please don't ask, I'm sorry in advance
    # If the averages of the tiles in castle positions are the top 3 then castle // im too tired for this shit

    try:
        try:
            move = board.find_move(table.lookup(second+1), table.lookup(first+1))
        except ValueError:
            move = board.find_move(table.lookup(first+1), table.lookup(second+1))
    except:
        # Breaks if no move has been found.
        return False

    board.push(move)

def on_click(event,x,y,flags,param):  
    if(event == cv.EVENT_LBUTTONDOWN):  
        corners.append([x,y])
        cv.circle(newBoard,(x,y),5,(255,255, 255),-1)

url = "http://192.168.0.103:8080/shot.jpg"

img = Image.open(requests.get(url, stream = True).raw)
img.save('./tmp/board.jpg')

newBoard = cv.imread('./tmp/board.jpg')

cv.namedWindow('Corners')  
cv.setMouseCallback('Corners',on_click)

while(len(corners) < 4):
    cv.imshow('Corners', newBoard)
    cv.waitKey(20)
cv.destroyAllWindows()

#re-read the board to get rid of white dots
newBoard = cv.imread('./tmp/board.jpg')
newBoard = cropBoardImage(newBoard, corners)
newBoard = cv.cvtColor(newBoard, cv.COLOR_BGR2GRAY)

cv.imshow("Starting Board", newBoard)
print("Press any key when first move is made.")
cv.waitKey(0)

turn = 0
while not board.is_game_over():
    turn+=1
    cv.destroyAllWindows()
    oldBoard = newBoard

    img = Image.open(requests.get(url, stream = True).raw)
    img.save('./tmp/board.jpg')

    newBoard = cv.imread('./tmp/board.jpg')
    newBoard = cropBoardImage(newBoard, corners)
    newBoard = cv.cvtColor(newBoard, cv.COLOR_BGR2GRAY)
    
    ret, difference = cv.threshold(boardDifference(oldBoard, newBoard, 3), 35, 255, cv.THRESH_BINARY)

    cv.imshow("Difference", drawGrid(difference))
    cv.imshow("Current Board", newBoard)
    cv.imwrite("last.jpg", difference)
    makeMove(difference)
    print("Turn "+str(turn))
    print(board)
    print("")
    if board.turn == assist:
        bestMove = engine.play(board, chess.engine.Limit(time=2))
        print(bestMove.move)
        # s.write(morse.toMorse(str(bestMove.move)+"\n").encode())
    cv.waitKey(0)
    

if board.is_game_over():
    print("Checkmate nerd")
