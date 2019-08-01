# < m a z e r >
# Programmed by Eugene Long.

#======================= DESCRIPTION =========================#
# Mazer is a cool maze solving game that runs on Python 3.7!
# Features:
# - Loading mazes from csv file (from parent file directory)
# - Viewing mazes
# - Playing mazes (scored by time)
# - Configuring mazes with inbuilt maze editor
# - Exporting current loaded maze to new csv file
# - Generating blank mazes for editing
# - Raspberry Pi SenseHat integration
# - Leaderboards! (Unique for every maze --> Console vs Pi!)
# Prerequisites:
# 1. Python 3.7
# 2. Raspberry Pi with SenseHat + Raspbian (and also py3.7)
# How to start:
# 1. Navigate to the directory you downloaded this game in
# 2. Run -> python3 mazer.py
#=============================================================#

#======================= HIGHLIGHTING ========================#
globalPrintMode = 0 # Defaults to no highlighting
# Set the variable above according to your preference and
# where you would run this program:
# 0: No color highlighting
# 1: Color highlighting for Terminal (Mac/Linux)
# 2: Color highlighting for IDLE (Windows/Mac)
#=============================================================#

#======================= CLASS INFO ==========================#
# Maze contains 3 variables:
# 1.    self.maze -----> 2D list containing maze data as
#       [[str, str, str...]]
# 2.    self.start ----> 1D list containing start coordinates
#       as [row, column] as [int, int]
# 3.    self.end ------> 1D list containing end coordinates as
#       [row, column] as [int, int]
#
# Leaderboard contains 1 variable:
# 1.    self.boards ---> 1D list containing only Board objects
#       as [Board, Board, Board...]
#
# Board contains 2 variables:
# 1.    self.digest_id > string containing the id of the board
# 2.    self.players --> 1D list of Player objects as
#       [Player, Player, Player...]
#
# Player contains 2 variables:
# 1.    self.playerID -> string containing id of player
# 2.    self.score ----> int containing score of player
#=============================================================#

# CODE STARTS HERE #

# NOTE: IMPORTS
import time, hashlib, copy, sys

# NOTE: CLASSES

########### NOTE: MAZE CLASS DEFINITION START ###########

class Maze:

    # NOTE: class init declaration
    def __init__(self, mazeArray, mazeStart, mazeEnd):
        '''Create a maze with a 2D list with maze data, a 1D list containing the start coords,
        and a 1D list containing the end coords'''
        self.maze, self.start, self.end = mazeArray, mazeStart, mazeEnd

########### NOTE: CLASS METHODS ###########

    def printMaze(self):
        '''Prints the maze in self.maze to the console.'''
        printSeparator(36)

        # Visual Enhancements Dictionary
        v_dict = {"X":"#", "O":".", "A":"a", "B":"b", "+":"+"}

        # Color Enhancements Dictionary
        if globalPrintMode == 1:
            c_dict = {"X":"\033[37m", "O":"\033[90m", "A":"\033[31m", "B":"\033[32m", "+":"\033[93m"}
        elif globalPrintMode == 2:
            c_dict = {"X":"OUTPUT", "O":"OUTPUT", "A":"STRING", "B":"COMMENT", "+":"KEYWORD"}

        for l in range(len(self.maze)):
            for c in range(len(self.maze[l])):

                # Print char + space for better visual representation, one at a time for all characters in a row
                if globalPrintMode == 1:
                    print(c_dict[self.maze[l][c]] + v_dict[self.maze[l][c]] + "\033[0m", end=" ")
                elif globalPrintMode == 2:
                    color.write(v_dict[self.maze[l][c]] + " ", c_dict[self.maze][l][c])
                else:
                    print(v_dict[self.maze[l][c]], end=" ")

            # Print newline for each new row
            print()

    def movePiece(self, piece_repr, bgMazeObj, user_input, invalid_spaces):
        '''Moves a piece (at the coords of self.start) depending on user input, and checks
        if the move is valid, else informing the user that the move is invalid. Requires a background
        Maze object to reference for the character that the piece is standing on.'''

        # Check that user input is within the move dictionary
        if user_input.upper() in ["W", "A", "S", "D"]:
            # Map movements from user input to array of x/y value changes
            moveMap = {'W':[-1,0], "A":[0,-1], "S":[1,0], "D":[0,1]}[user_input.upper()]
            upperLimit = [len(self.maze)-1, len(self.maze[0])-1]
        
            # Apply movements to temporary var p, then apply validation checks (within maze / no stepping on invalid spaces)
            p = [self.start[0]+moveMap[0], self.start[1]+moveMap[1]]
            if IntInRange(p[0], 0, upperLimit[0]) and IntInRange(p[1], 0, upperLimit[1]) and self.maze[p[0]][p[1]] not in invalid_spaces:
                # Update coords for piece, update maze representation
                self.maze[p[0]][p[1]] = piece_repr
                self.maze[self.start[0]][self.start[1]] = bgMazeObj.maze[self.start[0]][self.start[1]]
                self.start = p.copy()
            else:
                print("\nInvalid Movement. Please try again.\n")
        else:
            print("\nInvalid Input. Please try again.\n")

    def isLoaded(self):
        '''Checks if the maze has maze data loaded and returns the result.'''
        if self.maze != []:
            return True
        else:
            print("Maze not loaded!")
            return False

    def makeCopy(self):
        '''Makes a new Maze object with the same data as the caller and returns it.'''
        newObject = Maze([], [0, 0], [0, 0])
        newObject.maze = copy.deepcopy(self.maze)
        newObject.start = self.start.copy()
        newObject.end = self.end.copy()
        return newObject

    def copyFrom(self, other):
        '''Copies data from the Maze object passed into <other> into the caller.'''
        self.maze = copy.deepcopy(other.maze)
        self.start = other.start.copy()
        self.end = other.end.copy()

    def mazeToText(self):
        '''Returns a text representation of the maze data stored by the caller.'''
        strRepr = []
        for row in self.maze:
            strRepr.append("".join(row))
        return "\n".join(strRepr)

    def getMazeDigest(self):
        '''Returns the MD5 hash of the maze stored by the caller in hexadecimal format.'''
        encStrRep = self.mazeToText().encode('utf-8') # encode 
        digest = hashlib.md5(encStrRep).hexdigest()
        return digest

    def fetchBoard(self, l_board):
        '''Fetches the Board object from the Leaderboard object passed into <l_board> based
        on the maze data stored by the caller.'''
        return l_board.getBoard(self.getMazeDigest())

    def updateWinToBoard(self, score, l_board):
        '''Handles maze wins, prompts and validates for player nickname, then calls the 
        Leaderboard object in <l_board> to update with new values.'''
        board = self.fetchBoard(l_board)
        rank = board.getRank(score) # Returns rank, zero indexed
        if rank >= 0:
            print(f"You're ranked {rank+1} on the leaderboards!")

            # Player name request + validation
            while True:
                player_name = input("Enter your name: ")
                if player_name == "":
                    player_name = "Anonymous"
                    break
                elif len(player_name) > 25 or "|" in player_name:
                    print("Invalid name / Name too long!\n")
                else:
                    break

            # Update board
            board.players.insert(rank, Player(player_name, score))
            board.players = board.players[:10]

            # Update leaderboard
            l_board.updateLeaderboard()
        else:
            print("You weren't ranked... Try better next time!")
    
    def printToPi(self):
        '''Prints the maze to the display on a SenseHat. Requires this program to
        be running on a Raspberry Pi with SenseHat attached.'''
        for r in range(8):
            for c in range(8):
                s.set_pixel(c,r,127,127,127) # Set background to white, regardless of size of maze

        for r in range(len(self.maze)):
                for c in range(len(self.maze[r])):
                    c_dict = {"X": [127,127,127], "O":[0, 0, 0], "A":[127,0,0], "B":[0,127,0]}
                    rgb = c_dict[self.maze[r][c]]
                    s.set_pixel(c,r,rgb[0],rgb[1],rgb[2]) # Print actual maze data on top

########## NOTE: CLASS APPLICATIONS ###########

    def loadMaze(self):
        '''Loads the data from a file as text, converts the data into a suitable
        format for Maze objects and writes the data to the caller Maze object.'''

        # Validation for .csv file
        file_name = input("Enter name of the data file: ").split('.')
        if len(file_name) != 2 or file_name[1] != "csv":
            print("Invalid .csv file!")
            return None
        file_name = ".".join(file_name)

        try:
            with open(file_name) as f:

                r_maze = [] # Read-maze
                for line in f.readlines():
                    # strips whitespace, seperates the string into a list of characters and appends it to r_maze
                    r_maze.append(line.strip().split(','))

            # Validate maze is square or rectangle
            validate_shape = len(r_maze[0])
            for line in r_maze:
                if len(line) != validate_shape:
                    print("Maze should be of shape square or rectangle, not uneven!")
                    return None
            
            # Validate maze has only 1 set of start and end points
            abResult = verifyAB(r_maze, "A", "B")
            if abResult[0] == False:
                return None

            print(f"Number of lines read: {len(r_maze)}")
            # Write maze
            self.maze, self.start, self.end = r_maze, abResult[1], abResult[2]
        except FileNotFoundError:
            print("File Not Found.\n")

    def playMaze(self, isTerminal):
        '''Allows the user to play with the maze.'''
        fg_m = self.makeCopy() # Make temporary foreground Maze object
        bg_m = self.makeCopy() # Make temporary background Maze object
        pi_verify = len(fg_m.maze) <= 8 or len(fg_m.maze[0]) <= 8 # Caps pi maze to max dimensions: 8x8
        # Verify that the maze has only 1 start and end, and when set to Pi Mode, verifies that the maze is within dimensions
        if verifyAB(fg_m.maze, "A", "B")[0] and (not isTerminal or pi_verify):
            bg_m.maze[bg_m.start[0]][bg_m.start[1]] = "O" # Remove player for bg and set to proper background character "O"
            startTime = time.time() # Start timer for scoring
            while True:
                if isTerminal:
                    fg_m.printMaze()

                    print(f"\nLocation of Start (A) = (Row {fg_m.start[0]}, Column {fg_m.start[1]})")
                    print(f"Location of End (B) = (Row {fg_m.end[0]}, Column {fg_m.end[1]})\n")
                else:
                    fg_m.printToPi()

                if fg_m.start == fg_m.end:
                    timeTaken = round(time.time() - startTime, 2)
                    print("Congratulations! You win! ~\n")
                    if isTerminal:
                        self.updateWinToBoard(timeTaken, leaderboard)
                    else:
                        self.updateWinToBoard(timeTaken, pi_leaderboard)
                        s.clear()
                    break

                # Get user input
                if isTerminal:
                    user_input = input("Press 'W' for UP, 'A' for LEFT, 'S' for DOWN, 'D' for RIGHT, 'M' for MAIN MENU: ")
                else:
                    user_input = inputFromPi()

                # Move with validation and break when required
                if user_input.upper() == "M":
                    break
                else:
                    fg_m.movePiece("A", bg_m, user_input, ["X"])
        else: 
            print("Maze cannot be played!")

    def configureMaze(self):
        '''Allows the user to edit the maze'''
        bg_m = self.makeCopy() # Make fg, bg like playmaze
        fg_m = self.makeCopy() # bg in this case is the actual maze we want to export.
        fg_m.maze[0][0], fg_m.start, brush_mode = "+", [0, 0], 0 # Initialise cursor piece

        while True:
            fg_m.printMaze()
            print("\nKEYBINDS\n"+"="*8)
            options = {
                1:"Set normal cursor",
                2:"Toggle Wall Brush",
                3:"Toggle Passageway Brush",
                4:"Set to Start",
                5:"Set to End",
                "W":"Move up",
                "A":"Move left",
                "S":"Move right",
                "D":"Move down",
                "F":"Force Exit to Main Menu (Changes not applied!)",
                0:"Exit to Main Menu"
                }
            print(f"Cursor Mode: {['normal', 'wall', 'passage'][brush_mode]}")
            user_input = displayMenu(options, "Enter key (Adding a start/end point will reset the cursor to normal mode): ", "Invalid key!")
            
            if type(user_input) == int and IntInRange(user_input, -1, 5): # Do actions for options 0 through 5 (-1 is for error code handling)
                if user_input == 0: # Exit Maze

                    abResult = verifyAB(bg_m.maze, "A", "B")
                    if abResult[0] and input("Confirm exit editor mode? [Y/N]: ").upper() == "Y":
                        bg_m.start, bg_m.end = abResult[1].copy(), abResult[2].copy() # Copy over start and end coordinates
                        break
                        
                elif IntInRange(user_input, 1, 3): # toggle brush mode
                    brush_mode = user_input-1

                elif IntInRange(user_input, 4, 5): # Set the char at cursor to start/end
                    brush_mode = 0
                    bg_m.maze[fg_m.start[0]][fg_m.start[1]] = ["A", "B"][user_input-4]
                    
                # If (-1), don't do anything.
            else:
                if user_input == "F": # Force quit to main
                    return
                fg_m.movePiece("+", bg_m, user_input, []) # Move piece with no invalid spaces

            if brush_mode != 0: # Overwrite any char under cursor as long as brush mode is on
                bg_m.maze[fg_m.start[0]][fg_m.start[1]] = ["X", "O"][brush_mode-1]

        
        if input("Save edited maze to current maze? [Y/N]: ").upper() == "Y":
            self.copyFrom(bg_m) # Save changes

    def exportMaze(self):
        '''Prompts user for a valid .csv filename and then exports the current maze under that filename.'''

        # Get valid filename
        while True:
            file_name = input("Enter filename to save to: ").split(".")
            if len(file_name) == 2 and file_name[1] == "csv" and "/" not in file_name:
                break
            else:
                print("Invalid filename for export!")
                return
        file_name = ".".join(file_name)

        # Do the actual writing
        with open(file_name, 'w') as f:
            raw = self.mazeToText().split()
            for line in raw:
                f.write(",".join(list(line)) + "\n")
            f.truncate()
        print(f"File {file_name} created with {len(raw)} records.")

    def createNewMaze(self):
        '''Allows the user to generate a new maze object and overwrites the current maze with it'''
        if input("This will empty the current maze. Are you sure [Y/N]: ").upper() == "Y":
            new_xy = input("Enter dimensions of new maze. Max dimensions: (33,33) (row, column): ").split(",")
            # Validation! Check for proper number of elements, if they are digits, in range, etc.
            if len(new_xy) == 2 and new_xy[0].isdigit() and new_xy[1].isdigit() and IntInRange(int(new_xy[0]), 2, 33) and IntInRange(int(new_xy[1]), 2, 33):
                
                newMaze, rows, cols = [], int(new_xy[0]), int(new_xy[1])
                # Generate actual maze
                for _ in range(rows):
                    newMaze.append(['O']*cols)

                # Copy maze to current maze
                self.copyFrom(Maze(newMaze, [0,0], [0,0]))
                print(f"A new maze of {rows} by {cols} has been created.")

                # Ask user to choose next step
                if input("Would you like to directly edit it now? [Y/N]: ").upper() == "Y":
                    self.configureMaze()
                else:
                    print("Alright, but remember that you can configure it using option [4] in the menu.")
            else:
                print("Invalid Format!")

    def displayMazeLeaderboards(self):
        '''Display leaderboards for current maze'''
        if self.isLoaded():
            options = {1:"Console Leaderboards", 2:"Raspberry Pi Leaderboards"}
            # Fetch appropriate leaderboard depending on user input
            choice = displayMenu(options, "Choose a leaderboard: ", "Invalid option!")
            if choice == 1:
                board = self.fetchBoard(leaderboard)
            elif choice == 2:
                board = self.fetchBoard(pi_leaderboard)
            else:
                return None

            # Print leaderboards
            print(f"\n{'map: ' + self.getMazeDigest():^42s}\n")
            print(f"{'---HALL OF SEMI-PERMANENT FAME---':^42s}\n\n{'Name':<28s} {'Seconds':>13s}")
            printSeparator(42)
            for i in range(len(board.players)):
                p = board.players[i]
                print(f"<#{i+1:2d}> {p.playerID:<25s} {p.score:>10.2f}")

########### NOTE: MAZE CLASS DEFINITION END ###########

########### NOTE: LEADERBOARD & PLAYER CLASS DEFINITION START ###########

class Leaderboard:
    def __init__(self, l_file):
        self.boards = []
        self.l_file = l_file
        try:
            with open(l_file, 'r') as f:
                raw = f.read().split("\n;\n") # Get raw data
            
            # Parse raw data into proper objects (Basically splitting lots of delimiters)
            if len(raw) >= 1:
                boards = []
                for chunk in raw:
                    data = chunk.strip().split("\n")
                    digest_id = data[0]
                    players = []
                    for line in data[1:]:
                        playerID, score = line.split("|")
                        players.append(Player(playerID, score))
                    boards.append(Board(digest_id, players))

                self.boards = boards

        # Make new file if no leaderboard file found
        except FileNotFoundError:
            with open(l_file, 'w') as f:
                f.write("")

    def getBoard(self, digest_id):
        '''Returns the Board object in the caller Leaderboard with the id <digest_id>'''
        for board in self.boards:
            if board.digest_id == digest_id:
                return board
        
        # No matches so make new Board, append to Leaderboard and return it instead
        newBoard = Board(digest_id, [])
        self.boards.append(newBoard)
        return newBoard

    def updateLeaderboard(self):
        '''Updates the Leaderboard's storage file with the most current Leaderboard data'''
        load = []

        # basically the reverse of Leaderboard init
        for board in self.boards:
            board_load = [board.digest_id]
            for p in board.players:
                board_load.append(f"{p.playerID}|{str(p.score)}")
            load.append("\n".join(board_load))

        with open(self.l_file, 'w') as f:
            f.write("\n;\n".join(load))
            f.truncate()

class Board:
    def __init__(self, digest_id, players):
        self.digest_id = digest_id
        self.players = players

    def getRank(self, score):
        '''Gets the rank of a score within the context of the players already on the board.
        Returns -1 if the score doesn't beat anyone.'''
        for i in range(len(self.players)):
            if self.players[i].score > score:
                return i
        
        # Didn't beat anyone
        if len(self.players) < 10:
            return len(self.players)
        else:
            return -1

class Player:
    def __init__(self, playerID, score):
        self.playerID, self.score = str(playerID), float(score)

    def betterThanPlayer(self, Player):
        '''Comparison function based on score. Returns True if the other Player's score is higher than the callers'.'''
        return True if self.score < Player.score else False

########### NOTE: LEADERBOARD & PLAYER CLASS DEFINITION END ###########

# NOTE: GLOBAL FUNCTIONS
def displayMenu(optionDict, qn, error_msg): 
    '''Displays a menu and accepts input. Does not support lowercase keys.'''
    for option in optionDict:
        if option == 0:
            print(f"\n[{option}] {optionDict[option]}")
        else:
            print(f"[{option}] {optionDict[option]}")
    choice = input("\n"+qn)
    choice = int(choice) if choice.isdigit() else choice.upper()
    if choice in optionDict:
        return choice
    else:
        print(error_msg)
        return -1

def printSeparator(spaces):
    print("="*spaces+"\n")

def IntInRange(x, minX, maxX):
    return True if x >= minX and x <= maxX else False

def IntInput(msg, minX, maxX):
    while True:
        user_in = input(msg)
        if user_in.isdigit():
            if IntInRange(int(user_in), minX, maxX): return int(user_in)
            else: print("Out of range!\n")
        else:
            print("Invalid Input!\n")

def verifyAB(maze, start_char, end_char):
        '''Verifies if there are only 1 set of start_char and end_char characters within a 2D list,
        and returns the positions if they exist, else it is defaulted to [0,0]'''
        a_validate, b_validate, start, end = 0, 0, [0,0], [0,0]

        # Iterate through the list and locate all occurences of "A" and "B"
        for i in range(len(maze)):
            for j in range(len(maze[0])):

                if maze[i][j] == start_char:
                    a_validate += 1
                    start = [i, j]
                elif maze[i][j] == end_char:
                    b_validate += 1
                    end = [i, j]

        # Validate if there is only 1 set of "A" and "B"
        if a_validate != 1 or b_validate != 1:
            print(f"Invalid maze! Maze contains [{a_validate}/1] starting points and [{b_validate}/1] end points!")
            valid = False
        else:
            valid = True

        return [valid, start, end]

def DisplayMainMenu():
    print("\nMAIN MENU" + "\n=========")
    options = {
        1:"Read and load maze from file",
        2:"View maze",
        3:"Play maze game",
        4:"Configure current maze",
        5:"Export maze to file",
        6:"Create new maze",
        7:"Play maze using SenseHAT",
        8:"View Leaderboard",
        0:"Exit Maze"
                }
    choice = displayMenu(options, "Enter an option: ", "Invalid Option!")
    if choice != -1:
        print(f"\nOption [{choice}] {options[choice]}\n")
    return choice

def inputFromPi():
    while True:
        time.sleep(0.3)
        direction_map = {"up":"W", "down":"S", "left":"A", "right":"D", "middle":"M"}
        for event in s.stick.get_events():
            if event.action == "pressed":
                if event.direction in direction_map:
                    return direction_map[event.direction]

def checkPiAvailable(s_available):
    if s_available:
        return True
    else:
        print("Module <sense_hat> Not Found!")
        return False
        
# NOTE: MAIN
def Main():
    # Check if sense_hat can be imported
    try:
        from sense_hat import SenseHat
        s = SenseHat()
        s_available = True
    except:
        s_available = False

    # Setup for IDLE color highlighting
    if globalPrintMode == 2:
        color = sys.stdout.shell
        
    while True:
        choice = DisplayMainMenu()
        if choice == 0: break
        elif choice == 1: currentMaze.loadMaze()
        elif choice == 2 and currentMaze.isLoaded(): currentMaze.printMaze()
        elif choice == 3 and currentMaze.isLoaded(): currentMaze.playMaze(True)
        elif choice == 4 and currentMaze.isLoaded(): currentMaze.configureMaze()
        elif choice == 5 and currentMaze.isLoaded(): currentMaze.exportMaze()
        elif choice == 6: currentMaze.createNewMaze()
        elif choice == 7 and currentMaze.isLoaded() and checkPiAvailable(s_available): currentMaze.playMaze(False)
        elif choice == 8 and currentMaze.isLoaded(): currentMaze.displayMazeLeaderboards()
        input("\nPress [ENTER] to continue:")

# NOTE: GLOBAL VARIABLES
currentMaze = Maze([], [0, 0], [0, 0])
leaderboard, pi_leaderboard = Leaderboard("leaderboard.txt"), Leaderboard("pi_leaderboard.txt")

# Run Main
Main()