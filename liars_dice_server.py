# Christopher Stern
# Computer Science ISP - Liar's Dice

import socket
import random
import time

def numFaces(d,f,q): # function checks the number of faces of that die on the board
    counter = 0
    w = ""
    diceFaces = d.split(", ")
    for t in range (0,len(diceFaces)-1):
        if int(diceFaces[t])== f: # count the number of dice which have the face bid
            counter += 1

    if counter >= q: # if the couter is greater than or equal to the bid, then the bidder wins
        w = "bidder"
    else: # the challenger wins because the bidder was too high
        w = "challenger"
    print "The " + w + " was the winner."
    return w, counter # return the winner and the number of the bid face to the main function

def findWinner(): # function finds the overall winner in the game
    fileIn = open("winners.txt", "r") # read the txt file winners.txt
    countWins = fileIn.readline().rstrip()
    while countWins != "":
        winList.append(int(countWins)) # add each line to a list
        countWins = fileIn.readline().rstrip() # move to next line of text file

    playerCounter = 0
    winnerCount = 0
    overallWinner = ""
    for l in range (1,numPlayers+1): # move through the player numbers
        for item in winList: # loop through the win list
            if item == l: # if the player number equals the value in the text file, add to counter
                playerCounter += 1
        if playerCounter > winnerCount: # if counter is greater than the last highest counter, then we have a new winner
            winnerCount = playerCounter
            overallWinner = str(l)

    return overallWinner # return overall winner to the main function
       
print "Liar's Dice Server"
print
IP = socket.gethostbyname(socket.gethostname())
print "The IP address of the Liar's Dice Server is: " + IP
PORT = 23456
ADS = (IP, PORT)
from socket import *
tcpsoc = socket(AF_INET, SOCK_STREAM) # set up pathway for clients to connect to
tcpsoc.bind(ADS)
tcpsoc.listen(5) # listen for clients

client = []
address = []
numPlayers = int(raw_input("Enter the number of people who wish to play: ")) # ask user to enter the number of players playing the game
for x in range (0,numPlayers): # loop until all players have joined based on users input
    print "Waiting for connection from Player " + str(x+1) # print which player the server is waiting for
    tcpc, ad = tcpsoc.accept()
    client.append(tcpc)
    address.append(ad)
    client[x].send(str(numPlayers)) # send the number of players to the joining client
    time.sleep(1)
    client[x].send(str(x+1)) # send the player number the client will be
    for y in range(len(client)): # for all joined clients send how many players the server is waiting for
        if numPlayers - (x+1) != 1:
            client[y].send("Player " + str(x+1) + " is connected. Wait for " + str(numPlayers-(x+1)) + " more players to connect.")
        elif numPlayers - (x+1) == 1:
            client[y].send("Player " + str(x+1) + " is connected. Wait for " + str(numPlayers-(x+1)) + " more player to connect.")
time.sleep(1)

outFile = open("winners.txt","w") # create a text file called winners
outFile.close()

winList = []
counter = 0
gameover = False
oldQuantity = 0
oldFace = 0
while gameover == False: # continue until someone loses all their dice
    playerDice = ""
    totalDice = 0
    for a in range (0,numPlayers):
        info = int(client[a].recv(1024)) # receive the number of dice from the clients
        print "Received from Player " + str(a+1) + " that he has " + str(info) + " dice."
        totalDice += info
    print "The total dice on the table are: " + str(totalDice)
    for b in range (0,numPlayers):
        client[b].send("There are " + str(totalDice) + " dice in play.") # send total dice to each client
        time.sleep(1)
        client[b].send(str(totalDice)) # send value of total dice to each player

    time.sleep(1)

    playerNumber = counter % numPlayers
    client[playerNumber].send("Player " + str(playerNumber+1) + "- It is your turn.") # send to player it is their turn
    print "Sent to Player " + str(playerNumber + 1) + " it is their turn."
    time.sleep(1)
    client[playerNumber].send(str(oldFace)) # send the player the last die faces to be bid
    time.sleep(1)
    client[playerNumber].send(str(oldQuantity)) # send the player the last quantity of dice to be bid
    time.sleep(1)
    newFace = client[playerNumber].recv(1024) # receive new face from player
    newQuantity = client[playerNumber].recv(1024) # receive new quantity from user
    print "Received from Player " + str(playerNumber+1) + ": Face: " + newFace + " Number: " + newQuantity
    for z in range (0, numPlayers): # loop through players telling every client, other than the bidder, what the new bid is
        if z != playerNumber:
            client[z].send("Player " + str(playerNumber+1) + " bid " + newQuantity+ ", " + newFace + "s.")
    for c in range (playerNumber+1,playerNumber+numPlayers): # loop through players, asking each if they would like to challenge the new bid
        client[c%numPlayers].send("Would you like to challenge the bid?") # send to player a question, asking them if they would like to challenge the bid
        time.sleep(1)
        challenge = client[c%numPlayers].recv(1024) # receive response from the client
        print "Receieved response for challenge: " + challenge
        if challenge[0].upper() == "Y": # there is a challenge
            for d in range (0, numPlayers): # loop through players telling them there is a challenge from a certain player
                client[d].send("Player " + str((c%numPlayers) + 1) + " challenged the bid.")
                time.sleep(1)
                playerDice += client[d].recv(1024) + ", " # receive the dice the client has
                time.sleep(1)
                print "Received from Player " + str(d+1) + " dice : " + playerDice
            winner, actualFaces = numFaces(playerDice, int(newFace), int(newQuantity)) # run function finding out the true number of the face there are
            if winner == "bidder": # the bidder won the challnge
                for f in range (0, numPlayers):
                    client[f].send("There are " + str(actualFaces) + " " + str(newFace) + "s on the board. Therefore Player " + str(playerNumber+1) + " was right.") # tell clients who was correct
                    time.sleep(1)
                    client[f].send("The winner of the round is Player " + str(playerNumber + 1) + ".") # send to client the winner of the round
                    time.sleep(1)
                    client[f].send("That means Player " + str((c%numPlayers)+1) + " loses a die.") # tell the clients who loses a die
                    time.sleep(1)

                    writeWinner = open("winners.txt", "a") # open winners.txt to writie the winner
                    writeWinner.write(str(playerNumber + 1) + "\n") # write to text file the winner of the round
                    writeWinner.close()

                newFace = 0 # the round is over, so any bid can take place, face and quantity must be reset
                newQuantity = 0
                break
                
            elif winner == "challenger": # the challenger won the challenge
                for g in range (0, numPlayers):
                    client[g].send("There are " + str(actualFaces) + " " + str(newFace) + "s on the board. Therefore Player " + str((c%numPlayers) + 1) + " was right.") # tell clients who was correct

                    time.sleep(1)
                    client[g].send("The winner of the round is Player " + str((c%numPlayers) + 1) + ".") # send to client the winner of the round
                    time.sleep(1)
                    client[g].send("That means Player " + str(playerNumber + 1) + " loses a die.") # tell the clients who loses a die
                    time.sleep(1)

                    writeWinner = open("winners.txt", "a") # open winners.txt to writie the winner
                    writeWinner.write(str((c%numPlayers) + 1) + "\n")  # write to text file the winner of the round
                    writeWinner.close()
                    
                newFace = 0 # the round is over, so any bid can take place, face and quantity must be reset
                newQuantity = 0
                break
        
        elif challenge[0].upper() == "N": # the client did not challenge
            for h in range (0, numPlayers): # tell all the players that the last player did not challenge
                client[h].send("Player " + str((c%numPlayers) + 1) + " chose to leave the bid unchallenged.")
                time.sleep(1)
            if c%numPlayers == playerNumber-1: # if the "last" player in the circle did not challenge, move on to next bid
                for o in range (0,numPlayers):
                    client[o].send("Next Turn")
            elif c%numPlayers == numPlayers:
                for o in range (0,numPlayers):
                    client[o].send("Next Turn")
            elif c%numPlayers == playerNumber:
                for o in range (0,numPlayers):
                    client[o].send("Next Turn")
        

    for j in range (0,numPlayers):
        clientDice = int(client[j].recv(1024)) # receive from clients the number of dice they have
        print "Reveived from player " + str(j+1) + " number of dice: " + str(clientDice)
        time.sleep(1)
        if clientDice == 0: # if ever the number of dice equals 0, then game is over
            gameover = True

    if gameover == True: # game is over so send game over to all clients
        for k in range (0,numPlayers):
            client[k].send("Game Over")
            time.sleep(1)

    else:
        for k in range (0,numPlayers): # game is not over so tell clients to continue playing
            client[k].send("Game On")
            time.sleep(1)
            
    counter = counter + 1
    oldQuantity = newQuantity
    oldFace = newFace

overallWin = findWinner() # find the overall winner of the game of liars dice

for m in range (0,numPlayers):
    client[m].send("The winner of this game of Liar's Dice is Player " + overallWin + ".") # send to clients the overall winner
      
print "Game Over."
raw_input("Press ENTER to close the window") # tell user to press enter to close window
tcpsoc.close()
