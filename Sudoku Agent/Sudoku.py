assignments = []

rows = 'ABCDEFGHI'
cols = '123456789'

def cross(A, B):
    "Cross product of elements in A and elements in B."
    return [s+t for s in A for t in B]

#Define boxes and units
boxes = cross(rows, cols)
row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
diag_unit_1 = [r+c for r,c in zip(rows,cols)]
diag_unit_2 = [r+c for r,c in zip(rows,cols[::-1])]
unitlist = row_units + column_units + square_units + [diag_unit_1] + [diag_unit_2]
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Please use this function to update your values dictionary!
    Assigns a value to a given box. If it updates the board record it.
    """

    # Don't waste memory appending actions that don't actually change any values
    if values[box] == value:
        return values

    values[box] = value
    if len(value) == 1:
        assignments.append(values.copy())
    return values

def naked_twins(values):
    """Eliminate values using the naked twins strategy.
    Args:
        values(dict): a dictionary of the form {'box_name': '123456789', ...}

    Returns:
        the values dictionary with the naked twins eliminated from peers.
    """
    for unit in unitlist:
        #Identify naked twins
        val_list = [values[box] for box in unit if len(values[box])==2]
        val_list = set([val for val in val_list if val_list.count(val)==2])
        #Eliminate naked twins from other boxes
        for vals in val_list:
            retain_box = [box for box in unit if values[box]==vals]
            for val in vals:
                for box in unit:
                    if box not in retain_box:
                        values = assign_value(values, box, values[box].replace(val,''))
    return values

    

def grid_values(grid):
    """
    Convert grid into a dict of {square: char} with '123456789' for empties.
    Args:
        grid(string) - A grid in string form.
    Returns:
        A grid in dictionary form
            Keys: The boxes, e.g., 'A1'
            Values: The value in each box, e.g., '8'. If the box has no value, then the value will be '123456789'.
    """
    mod_grid = [ val if val !='.' else '123456789' for val in grid]
    return dict(zip(cross(rows,cols),mod_grid))

def display(values):
    """
    Display the values as a 2-D grid.
    Args:
        values(dict): The sudoku in dictionary form
    """
    width = 1+max(len(values[s]) for s in boxes)
    line = '+'.join(['-'*(width*3)]*3)
    for r in rows:
        print(''.join(values[r+c].center(width)+('|' if c in '36' else '')
                      for c in cols))
        if r in 'CF': print(line)
    return

def eliminate(values):
    """Eliminate values from peers of each box with a single value.

    Go through all the boxes, and whenever there is a box with a single value,
    eliminate this value from the set of values of all its peers.

    Args:
        values: Sudoku in dictionary form.
    Returns:
        Resulting Sudoku in dictionary form after eliminating values.
    """    
    for box,val in values.items():
        if len(val)==1:
            for peer in peers[box]:
                values = assign_value(values, peer, values[peer].replace(val,''))
    return values

def only_choice(values):
    """Finalize all values that are the only choice for a unit.

    Go through all the units, and whenever there is a unit with a value
    that only fits in one box, assign the value to this box.

    Input: Sudoku in dictionary form.
    Output: Resulting Sudoku in dictionary form after filling in only choices.
    """
    for unit in unitlist:
        #Identify numbers which occurs only once
        val_list = ''.join([values[box] for box in unit])
        val_list = [val for val in val_list if val_list.count(val)==1]
        #Find those numbers and replace the box with that value
        for val in val_list:
            target = [box for box in unit if val in values[box]]
            if len(target) == 1:
                values = assign_value(values, target[0], val)
    return values

def reduce_puzzle(values):
    """
    Iterate eliminate() and only_choice(). If at some point, there is a box with no available values, return False.
    If the sudoku is solved, return the sudoku.
    If after an iteration of both functions, the sudoku remains the same, return the sudoku.
    Input: A sudoku in dictionary form.
    Output: The resulting sudoku in dictionary form.
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        values = eliminate(values)
        values = only_choice(values)
        values = naked_twins(values)
        # Check how many boxes have a determined value, to compare
        solved_values_after = len([box for box in values.keys() if len(values[box]) == 1])
        # If no new values were added, stop the loop.
        stalled = solved_values_before == solved_values_after
        # Sanity check, return False if there is a box with zero available values:
        if len([box for box in values.keys() if len(values[box]) == 0]):
            return False
    return values

def search(values):
    """
    Using depth-first search and propagation, create a search tree and solve the sudoku.
    First, reduce the puzzle using the previous function
    """
    values = reduce_puzzle(values)
    
    if values == False:
        return False
        
    #check if sudoku is solved, then return
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    if len(values) == len(solved_values):
        return values
        
    # Choose one of the unfilled squares with the fewest possibilities
    filtered_values = {k:v for (k,v) in values.items() if len(v)>1}
    mink=min(filtered_values, key=lambda k: len(filtered_values[k]))
    
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer!
    possible_values = values[mink]    
    for val in possible_values:
        new_values = values.copy()
        new_values[mink] = val
        result = search(new_values)
        if result:
            return result

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    values = grid_values(grid)
    return search(values)


if __name__ == '__main__':
    diag_sudoku_grid = '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    display(solve(diag_sudoku_grid))

    try:
        from visualize import visualize_assignments
        visualize_assignments(assignments)

    except SystemExit:
        pass
    except:
        print('We could not visualize your board due to a pygame issue. Not a problem! It is not a requirement.')
