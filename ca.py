SIDES = ("N", "S", "E", "W", "NW", "NE", "SE", "SW")
GRIDSIZE = (140,140)

class CAGrid:

    def __init__(self):
        self.xdim = GRIDSIZE[0]
        self.ydim = GRIDSIZE[1]
        self.timeStep = 0
        self.maxTimeSteps = 100
        self.outFile = open("results.txt", 'w')
        self.outJSFile = open("results.js", 'w')
        self.outJSFile.write("window.fIndex = 0;\n")
        self.outJSFile.write("window.frameWidth = %s;\n" % GRIDSIZE[0])
        self.outJSFile.write("window.frameHeight = %s;\n" % GRIDSIZE[1])
        self.jsFrames = []

        # grid is just a dictionary x --> y --> cell
        #   so to access cell (3,4)... 
        #       cell = x_y_cell[3][4]
        #   (0,0) will be bottom left
        self.x_y_cell = {}

        # this is just a helper list for easy scrolling through all the coordinates
        #   (0,0), (0,1), ...
        self.allCoords = [] 
        for x in range(0, self.xdim):
            for y in range(0, self.ydim):
                self.allCoords.append((x,y))

        #for every cell on the grid, create a Cell object on that cell with state 0
        for (x,y) in self.allCoords:
            self.x_y_cell.setdefault(x, {})[y] = Cell(0, (x,y), self)

        self.initialize_grid()

    def initialize_grid(self):

        self.x_y_cell[70][10].state = 1
        self.x_y_cell[90][90].state = 1

    def update(self):

        #update all cells according to each cell/agent rule using current state
        for (x,y) in self.allCoords:
            cellAtCoord = self.x_y_cell[x][y]
            cellAtCoord.update()
       
        #transfer all this steps state changes to the grid
        for (x,y) in self.allCoords:
            cellAtCoord = self.x_y_cell[x][y]
            cellAtCoord.state = cellAtCoord.nextStepState

        #write step result to file
        self.output_grid_state()
       
    def run(self):
        
        theGrid.output_grid_state()

        for tStep in range(0, self.maxTimeSteps):
            self.timeStep = tStep
            self.update()

        self.finish()

    def output_grid_state(self):
        "output time state to open text file"
      
        [self.outFile.write("-") for x in range(0, self.ydim)] 
        self.outFile.write("\n")

        yRangeRev = range(0, self.ydim)
        yRangeRev.reverse()
        for y in yRangeRev:
            wString = [str(self.x_y_cell[x][y].state) for x in range(0, self.xdim)]
            wString = "|" + "".join(wString) + '|\n'
            wString = wString.replace("0", " ")
            self.outFile.write(wString)

        #add newline after each state
        self.outFile.write("\n")

        newFrame = ""
        for y in yRangeRev:
            for x in range(0, self.xdim):
                newFrame = newFrame + str(self.x_y_cell[x][y].state)
        self.jsFrames.append(newFrame)
            

    def finish(self):
        self.outFile.close()

        self.outJSFile.write("var frames = [") 
        for frame in self.jsFrames:
            self.outJSFile.write("\"%s\"," % frame)
        self.outJSFile.write("];\n") 
        self.outJSFile.write("setInterval(function(){draw_next_frame(frames)}, 50);")
        self.outJSFile.close()

class Cell:

    def __init__(self, initialState, position, grid):
        self.state = initialState
        self.grid = grid
        self.position = position
        self.nextStepState = self.state

    def update(self):
       
        # The nextStepState is the state that this cell will be once all the state calculations have been done for ALL cells
        # We need it because other cells might still need to make a state-change decision based on this cell's current state
        self.nextStepState = self.state

        #if any of my neighbors are infected, infect me
        neighborStates = []
        for side in SIDES:
            neighborStates.append(self.neighbor_state(side)) 

        #now neighborStates looks something like this [0,0,1,None]
        #it will be None if there is NO neighbor (like on the edge where cells have either 2 or 3)

        if 1 in neighborStates:
            self.nextStepState = 1

        if neighborStates.count(1) > 4:
            self.nextStepState = 0

    def neighbor_state(self, side):
        
        if side == "N":
            coord_x = self.position[0]  
            coord_y = self.position[1] + 1
        elif side == "S":
            coord_x = self.position[0]  
            coord_y = self.position[1] - 1
        elif side == "E":
            coord_x = self.position[0] + 1  
            coord_y = self.position[1]
        elif side == "W":
            coord_x = self.position[0] - 1  
            coord_y = self.position[1]
        elif side == "NW":
            coord_x = self.position[0] - 1  
            coord_y = self.position[1] + 1
        elif side == "NE":
            coord_x = self.position[0] + 1  
            coord_y = self.position[1] + 1
        elif side == "SE":
            coord_x = self.position[0] + 1  
            coord_y = self.position[1] - 1
        elif side == "SW":
            coord_x = self.position[0] - 1  
            coord_y = self.position[1] - 1

        xInGrid = (0 < coord_x < self.grid.xdim - 1)
        yInGrid = (0 < coord_y < self.grid.ydim - 1)

        if (not xInGrid) or (not yInGrid):
            return None
        else:
            return self.grid.x_y_cell[coord_x][coord_y].state

if __name__ == "__main__":
    import sys

    theGrid = CAGrid()
    theGrid.run()

