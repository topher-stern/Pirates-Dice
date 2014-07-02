# Christopher Stern
# Computer Science ISP - Liar's Dice

from socket import *
import random
import time

def checkBid(f,q,n,oF,oQ): # function checks to find that the users entry is a valid entry
    while 1 == 1: # try to integer the input, if it can't the input is invalid
        try:
            f = int(f)
            break
        except:
            f = int(raw_input("Please enter a valid die face. (1-6)"))
            break
    while f < 1 or f > 6: # check that the input is a valid die face between 1 and 6
        f = int(raw_input("Please enter a valid die face. (1-6)"))
    while 2 == 2: # try to make the quantity an integer
        try:
            q = int(q)
            break
        except:
            q = int(raw_input("Please enter an integer number of dice less than or equal to the number of dice in play."))
            break
    if q > n:
        while q > n : # check that the quantity is less than the number of dice on the board
            print "There are " + str(n) + " dice on the table."
            q = int(raw_input("Please enter a number of dice less than or equal to the number of dice in play."))
    if f < oF or q < oQ:
        while f < oF or q < oQ: # ensure the bid is greater than the old bid
            print "Remember, either the face or quantity of dice with that face must increase on each bid."
            print "The previous bid was " + str(oQ) + " " + str(oF) + "s."
            print "Please bid again."
            f = int(raw_input("Please enter a face number (1-6): "))
            q = int(raw_input("Please enter a quantity of that face (integer value): "))
            print
            
    return str(f),str(q)

print "Liar's Dice Client" # title the page and describe the game to new users
print "---------------"
print
print "Liar's Dice generally has players sit in a circle.  All players roll their"
print "5 dice and conceal them. Each player can look at his/her dice but cannot"
print "see their opponents'. The player designated to go first claims any number"
print "of a face of their choice that they believe is the total numebr of dice with"
print "that face on the entire table. These claims continue around the table until"
print "someone believe the another has bid too high. At this point all the dice are"
print "revealed. If the bid was too high, the player who bid loses the round, but"
print "if the bid was too low or right on, the player who called a bluff loses."
print "Whoever loses the round, either the bidder or the challenger, loses a die"
print "and when one of the players has no die, the game is over. Whoever won the"
print "most rounds wins the game."
print
IP = raw_input("Enter the IP address of the Liar's Dice Server: ") # ask for the IP of the server
PORT = 23456 
ADS = (IP, PORT)
tcpsocket = socket(AF_INET, SOCK_STREAM)
tcpsocket.connect(ADS) # connect to pathway of the server

data = tcpsocket.recv(1024) # receive the number of players in the game
numPlayers = int(data)
print "There are " + str(numPlayers) + " players in this game."
print
data = tcpsocket.recv(1024)
playerNum = int(data) # receive the player number the user is playing as
print "You are player number: " + str(playerNum)
print
for x in range(numPlayers-playerNum+1): # wait for other players to join to the server
    data = tcpsocket.recv(1024)
    print data

gameover = False
numDice = 5 # players start with five dice
dice = []
while gameover == False: # continue until someone loses all their dice
    face = ""
    quantity = ""
    answer = ""
    dice = []
    for q in range (0,numDice):
        dice.append(random.randint(1,6)) # create a list in which the player's dice are kept (dice can e any random number between 1 and 6)
    line = ""
    for i in range (0, len(dice)): # set up a string to tell the user what dice they have
        if i != len(dice) - 1:
            line += str(dice[i]) + ", "
        else:
            line += str(dice[i])
    roundover = False
    while roundover == False: # conintue until someone challenges a bid
        if numDice > 1:
            print "You have " + str(numDice) + " dice on the table." # tell client how many dice they have
            print "Your dice are: " + line # tell client what his/her dice are
        else:
            print "You have " + str(numDice) + " die on the table." # tell client how many dice they have
            print "Your die is: " + line # tell client what his/her die is
        tcpsocket.send(str(numDice)) # send to server the number of dice client has
        dice = tcpsocket.recv(1024)
        time.sleep(1)
        totalDice = int(tcpsocket.recv(1024)) # receive total dice value from server
        time.sleep(1)
        data = tcpsocket.recv(1024) # receive data from the server
        time.sleep(1)
        if data[-5:] == "turn.": # if data tells the user it is his/her turn
            print data # print the data
            print
            oldFace = int(tcpsocket.recv(1024)) # receieve the last face value to be bid
            time.sleep(1)
            oldQuantity = int(tcpsocket.recv(1024)) # receieve the last quantity to be bid
            print "There are " + str(totalDice) + " dice on the table."
            face = raw_input("What die face would you like to bid? (1-6) ") # ask client what face they would like to bid
            quantity = raw_input("How many dice of that face do you think there are? (integer value) ") # ask client the number of faces they wish to bid
            print
            face, quantity = checkBid(face,quantity,totalDice,oldFace,oldQuantity) # send new and old faces and quantity to function to make sure the bid is valid
            tcpsocket.send(face) # send the valid face to the server
            time.sleep(1)
            tcpsocket.send(quantity) # send the valid quantity to the server
            time.sleep(1)

        elif data[-2:] == "s.": # It is not this cilent's turn, but the data holds the new bid
            print data
        x = 0
        answer = ""
        while x < numPlayers:
            data = tcpsocket.recv(1024) # receive new information from the server 
            time.sleep(1)
            if data[-5:] == " bid?": # server wants to know if client would like to challenge
                if numDice > 1:
                    print "Your dice are: " + line # tell client what his/her dice are
                else:
                    print "Your die is: " + line # tell client what his/her die is
                answer = raw_input(data + " [Y/N]: ") # ask client if they would like to challenge
                tcpsocket.send(answer) # send the answer to the server
                time.sleep(1)
                data = tcpsocket.recv(1024) # receive from user the string telling them they have challenged the bid
            if data[-5:] == " bid.": # if the information tells the client someone challenged the bid
                print data
                print
                tcpsocket.send(line) # send the dice the client has to the server
                time.sleep(1)
                roundover = True # someone challenged so the round is over and new dice will need to be rolled
                data = tcpsocket.recv(1024) # receive who was correct
                print data
                time.sleep(1)
                winner = tcpsocket.recv(1024) # receive who the winner of the round is
                print winner
                time.sleep(1)
                data = tcpsocket.recv(1024) # receive who loses a die
                print data
                time.sleep(1)
                print
                if answer.upper() == "Y" and winner[-2:] != str(playerNum) + ".": # if player challenged and they are not the winner, they lose a die
                    numDice -= 1
                    break
                elif face != "" and winner[-2:] != str(playerNum) + ".": # if player made a bid and they are not the winner they lsoe a die
                    numDice -= 1
                    break
                break
            if data[-5:] == "nged.": # the previous player left the bid unchallenged
                print data
                if data[7] == str(numPlayers): # if the player who did not challenge is the last player to go, break out of the loop
                    break
                data = tcpsocket.recv(1024) # receive whether or not it is the next player's turn or not
                time.sleep(1)
                if data == "Next Turn":
                    break
            x += 1

        tcpsocket.send(str(numDice)) # send the number of dice one has
        time.sleep(1)
        game = tcpsocket.recv(1024) # receive whether or not the game is over
        time.sleep(1)
        if game == "Game Over": # if game is over, then end the round and game
            gameover = True
            roundover = True
        

            
overallWin = tcpsocket.recv(1024) # receive winner of the game
time.sleep(1)
print overallWin # print winner and overall response to specific client
if overallWin[-2] == str(playerNum):
    print "Congratulations. You won this game of Liar's Dice"
    print "You are the master of deception."

else:
    print "Unfortunately you did not win this game of Liar's Dice."
    print "Better luck next time."
print
print "Thank you for playing."
raw_input("Press ENTER to End Game.")
tcpsocket.close()
