assignments = []
rows = 'ABCDEFGHI'
cols = '123456789'
def cross(A, B):
    return [s+t for s in A for t in B]
#Concatenates element by element for 2 2 lists of string. It is used for building diagonal unit below
def concat_zip(A,B):
    return [z[0]+z[1] for z in zip(A,B)]


boxes = cross(rows, cols)

row_units = [cross(r, cols) for r in rows]
column_units = [cross(rows, c) for c in cols]
square_units = [cross(rs, cs) for rs in ('ABC','DEF','GHI') for cs in ('123','456','789')]
#building diagonal units for diagonal sudoku
diagonal_units = [concat_zip(rows,cols), concat_zip(rows,cols[::-1])]
#create list of all constrained units including the diagonal units
unitlist = row_units + column_units + square_units + diagonal_units
units = dict((s, [u for u in unitlist if s in u]) for s in boxes)
peers = dict((s, set(sum(units[s],[]))-set([s])) for s in boxes)

def assign_value(values, box, value):
    """
    Update values dictionary representing the board
    """
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
	#Loop through all units
    for unit in unitlist:
        # Find all instances of naked twins
        
		# Define dictionary mapping box values to set of boxes
        # with the same values for all values of the length 2
        twin_candidates = {}
		
        unresolved = set()      # set of unresolved boxes in the unit
        for box in unit:
            val = values[box]
            box_len = len(val)
            if box_len > 1:
                unresolved.add(box)
                if box_len == 2:
                    if val not in twin_candidates.keys():
                        twin_candidates[val] = set()
                    twin_candidates[val].add(box)
		# select all the items in twin_candidates dictionary which map to the pair of boxes
        twins = {v: b for v, b in twin_candidates.items() if len(b) == 2}
		
        # Eliminate the naked twins as possibilities for their peers
        for twin_val, twin_boxes in twins.items():
            for box in unresolved:
                for val in twin_val:
                    if box not in twin_boxes:
                        assign_value(values,box,values[box].replace(val,''))            
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
    assert len(grid) == 81
    grid_val = dict(zip(boxes,grid))
    return  {b: '123456789' if v == '.' else v for b, v in grid_val.items()}

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
    solved_values = [box for box in values.keys() if len(values[box]) == 1]
    for box in solved_values:
        digit = values[box]
        for peer in peers[box]:
            assign_value(values, peer, values[peer].replace(digit,''))
    return values

def only_choice(values):
    for unit in unitlist:
        for digit in '123456789':
            dplaces = [box for box in unit if digit in values[box]]
            if len(dplaces) == 1:
                assign_value(values,dplaces[0],digit)
    return values


def reduce_puzzle(values):
	"""
    Perform one iteration in elimination using several constraint propagation techniques.
    Args:
        values(dict): The sudoku in dictionary form
    """
    stalled = False
    while not stalled:
        # Check how many boxes have a determined value
        solved_values_before = len([box for box in values.keys() if len(values[box]) == 1])
        # Apply the Eliminate Strategy
        values = eliminate(values)
        # Apply Only Choice Strategy
        values = only_choice(values)
        # Apply Naked Twins Strategy
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
    Search sudoku iteratively performing constraint propagation steps.
    Args:
        values(dict): The sudoku in dictionary form
    """
    values = reduce_puzzle(values)
    if values == False:
        return False
    
    unresolved = [(box,len(values[box])) for box in values.keys() if len(values[box]) > 1 ]
    if len(unresolved) == 0:
        return values
    # Choose one of the unfilled squares with the fewest possibilities
    box_min =  min(unresolved, key = lambda box_len: box_len[1])[0]
    # Now use recursion to solve each one of the resulting sudokus, and if one returns a value (not False), return that answer
    for digit in values[box_min]:
        newvalues = values.copy()
        newvalues[box_min] = digit
        attempt = search(newvalues)
        if attempt:
            return attempt

def solve(grid):
    """
    Find the solution to a Sudoku grid.
    Args:
        grid(string): a string representing a sudoku grid.
            Example: '2.............62....1....7...6..8...3...9...7...6..4...4....8....52.............3'
    Returns:
        The dictionary representation of the final sudoku grid. False if no solution exists.
    """
    return search(grid_values(grid))

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
