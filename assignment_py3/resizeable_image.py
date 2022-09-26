import imagematrix

# Finds the vertical seam with the lowest energy to reduce the size
# Of an image while preserving its distinguishing features.
class ResizeableImage(imagematrix.ImageMatrix):
    def best_seam(self, dp=True):
        if dp:
            ''' Dynamic Approach '''
            # Initialize the dynamic table and the base case on the first row
            dp_table = []
            for j in range(self.height):
                dp_table.append([])
            for i in range(self.width):
                dp_table[0].append(self.energy(i, 0))

            # Fill in the remaining cells of our table using the recurrence relation
            for j in range(1, self.height):                                                   # leftmost column
                neighbors = [dp_table[j-1][0], dp_table[j-1][1]]                              # neighbors on [LEFT, CENTER]
                dp_table[j].append(self.energy(0,j) + min(neighbors)) #=> table

                for i in range(1, self.width-1):                                              # center columns
                    neighbors = [dp_table[j-1][i-1], dp_table[j-1][i], dp_table[j-1][i+1]]    # neighbors on [LEFT, CENTER, RIGHT]
                    dp_table[j].append(self.energy(i,j) + min(neighbors)) #=> table
                
                                                                                              # rightmost column
                neighbors = [dp_table[j-1][i-1], dp_table[j-1][i]]                            # neighbors on [CENTER, RIGHT]
                dp_table[j].append(self.energy(self.width-1,j) + min(neighbors)) #=> table
            
            """ Reconstruct the path using indexes """
            # Get the pixel on the last row with the lowest value
            prev_index = dp_table[-1].index(min(dp_table[-1]))
            indexes = [prev_index]

            # For each level, find the minimum value among the 2 or 3 neighbors of the previous cell
            for j in range(self.height-2, -1, -1):
                if prev_index > 0 and prev_index < self.width-1:
                    neighbors = dp_table[j][prev_index-1:prev_index+2]
                elif prev_index == 0:                                    #################################
                    neighbors = [float('inf')] + dp_table[j][:2]         #  The imaginary left neighbor  #
                else:                                                    #  is necessary for indexing    #
                    neighbors = dp_table[j][prev_index-1:]               #################################
                
                prev_index += neighbors.index(min(neighbors))-1
                indexes.append(prev_index)

            # Convert the list of indexes into a list of coordinates denoting the path
            path = []
            h = self.height-1
            for index in indexes:
                path.append((index, h))
                h -= 1

            return path

        else:
            ''' Naive Approach '''
            # Build the energy table so that we don't repeatedly
            # calculate the energy of pixels.
            energy_table = []
            for j in range(self.height):
                energy_table.append([])
                for i in range(self.width):
                    energy_table[j].append(self.energy(i,j))

            # Without dynamic programming, the naive approach using recursion with a helper function
            def find_best_path(index, height):
                path_object = [energy_table[height][index], [(index, height)]]

                if height == 0:                           # The recursive base case is being on the top row
                    return path_object
                elif index > 0 and index < self.width-1:
                    new_paths = (find_best_path(index-1, height-1),   # neighbors [LEFT, CENTER, RIGHT]
                                    find_best_path(index, height-1),
                                    find_best_path(index+1, height-1))

                elif index == 0:
                    new_paths = (find_best_path(index, height-1),     # neightbors [CENTER, RIGHT]
                                    find_best_path(index+1, height-1))            
                else:
                    new_paths = (find_best_path(index-1, height-1),   # neighbors [LEFT, CENTER]
                                    find_best_path(index, height-1))

                # Find the shortest path from among the subproblems
                shortest_path = None
                shortest_length = float('inf')
                for path in new_paths:
                    if path[0] < shortest_length:
                        shortest_length = path[0]
                        shortest_path = path[1]

                # Add the current node to the shortest path
                path_object[0] += shortest_length
                path_object[1] += shortest_path

                return path_object


            # Start the recursive process
            shortest_path = None
            shortest_path_length = float('inf')
            for i in range(self.width):
                path = find_best_path(i, self.height-1)
                if path[0] < shortest_path_length:      # Calculate the shortest path for each pixel
                    shortest_path_length = path[0]      # on the bottom row and return the shortest
                    shortest_path = path[1]

            return shortest_path

    def remove_best_seam(self):
        self.remove_seam(self.best_seam())