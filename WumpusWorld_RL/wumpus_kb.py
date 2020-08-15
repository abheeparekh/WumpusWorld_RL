

# wumpus_kb.py
# ------------
# Licensing Information:
# Please DO NOT DISTRIBUTE OR PUBLISH solutions to this project.
# You are free to use and extend these projects for EDUCATIONAL PURPOSES ONLY.
# The Hunt The Wumpus AI project was developed at University of Arizona
# by Clay Morrison (clayton@sista.arizona.edu), spring 2013.
# This project extends the python code provided by Peter Norvig as part of
# the Artificial Intelligence: A Modern Approach (AIMA) book example code;
# see http://aima.cs.berkeley.edu/code.html
# In particular, the following files come directly from the AIMA python
# code: ['agents.py', 'logic.py', 'search.py', 'utils.py']
# ('logic.py' has been modified by Clay Morrison in locations with the
# comment 'CTM')
# The file ['minisat.py'] implements a slim system call wrapper to the minisat
# (see http://minisat.se) SAT solver, and is directly based on the satispy
# python project, see https://github.com/netom/satispy .

import utils

# -------------------------------------------------------------------------------
# Wumpus Propositions
# -------------------------------------------------------------------------------

### atemporal variables

proposition_bases_atemporal_location = ['P', 'W', 'S', 'B']


def pit_str(x, y):
    "There is a Pit at <x>,<y>"
    return 'P{0}_{1}'.format(x, y)


def wumpus_str(x, y):
    "There is a Wumpus at <x>,<y>"
    return 'W{0}_{1}'.format(x, y)


def stench_str(x, y):
    "There is a Stench at <x>,<y>"
    return 'S{0}_{1}'.format(x, y)


def breeze_str(x, y):
    "There is a Breeze at <x>,<y>"
    return 'B{0}_{1}'.format(x, y)


### fluents (every proposition who's truth depends on time)

proposition_bases_perceptual_fluents = ['Stench', 'Breeze', 'Glitter', 'Bump', 'Scream']


def percept_stench_str(t):
    "A Stench is perceived at time <t>"
    return 'Stench{0}'.format(t)


def percept_breeze_str(t):
    "A Breeze is perceived at time <t>"
    return 'Breeze{0}'.format(t)


def percept_glitter_str(t):
    "A Glitter is perceived at time <t>"
    return 'Glitter{0}'.format(t)


def percept_bump_str(t):
    "A Bump is perceived at time <t>"
    return 'Bump{0}'.format(t)


def percept_scream_str(t):
    "A Scream is perceived at time <t>"
    return 'Scream{0}'.format(t)


proposition_bases_location_fluents = ['OK', 'L']


def state_OK_str(x, y, t):
    "Location <x>,<y> is OK at time <t>"
    return 'OK{0}_{1}_{2}'.format(x, y, t)


def state_loc_str(x, y, t):
    "At Location <x>,<y> at time <t>"
    return 'L{0}_{1}_{2}'.format(x, y, t)


def loc_proposition_to_tuple(loc_prop):
    """
    Utility to convert location propositions to location (x,y) tuples
    Used by HybridWumpusAgent for internal bookkeeping.
    """
    parts = loc_prop.split('_')
    return (int(parts[0][1:]), int(parts[1]))


proposition_bases_state_fluents = ['HeadingNorth', 'HeadingEast',
                                   'HeadingSouth', 'HeadingWest',
                                   'HaveArrow', 'WumpusAlive']


def state_heading_north_str(t):
    "Heading North at time <t>"
    return 'HeadingNorth{0}'.format(t)


def state_heading_east_str(t):
    "Heading East at time <t>"
    return 'HeadingEast{0}'.format(t)


def state_heading_south_str(t):
    "Heading South at time <t>"
    return 'HeadingSouth{0}'.format(t)


def state_heading_west_str(t):
    "Heading West at time <t>"
    return 'HeadingWest{0}'.format(t)


def state_have_arrow_str(t):
    "Have Arrow at time <t>"
    return 'HaveArrow{0}'.format(t)


def state_wumpus_alive_str(t):
    "Wumpus is Alive at time <t>"
    return 'WumpusAlive{0}'.format(t)


proposition_bases_actions = ['Forward', 'Grab', 'Shoot', 'Climb',
                             'TurnLeft', 'TurnRight', 'Wait']


def action_forward_str(t=None):
    "Action Forward executed at time <t>"
    return ('Forward{0}'.format(t) if t != None else 'Forward')


def action_grab_str(t=None):
    "Action Grab executed at time <t>"
    return ('Grab{0}'.format(t) if t != None else 'Grab')


def action_shoot_str(t=None):
    "Action Shoot executed at time <t>"
    return ('Shoot{0}'.format(t) if t != None else 'Shoot')


def action_climb_str(t=None):
    "Action Climb executed at time <t>"
    return ('Climb{0}'.format(t) if t != None else 'Climb')


def action_turn_left_str(t=None):
    "Action Turn Left executed at time <t>"
    return ('TurnLeft{0}'.format(t) if t != None else 'TurnLeft')


def action_turn_right_str(t=None):
    "Action Turn Right executed at time <t>"
    return ('TurnRight{0}'.format(t) if t != None else 'TurnRight')


def action_wait_str(t=None):
    "Action Wait executed at time <t>"
    return ('Wait{0}'.format(t) if t != None else 'Wait')


def add_time_stamp(prop, t): return '{0}{1}'.format(prop, t)


proposition_bases_all = [proposition_bases_atemporal_location,
                         proposition_bases_perceptual_fluents,
                         proposition_bases_location_fluents,
                         proposition_bases_state_fluents,
                         proposition_bases_actions]


# -------------------------------------------------------------------------------
# Axiom Generator: Current Percept Sentence
# -------------------------------------------------------------------------------

# def make_percept_sentence(t, tvec):
def axiom_generator_percept_sentence(t, tvec):
    """
    Asserts that each percept proposition is True or False at time t.
    t := time
    tvec := a boolean (True/False) vector with entries corresponding to
            percept propositions, in this order:
                (<stench>,<breeze>,<glitter>,<bump>,<scream>)
    Example:
        Input:  [False, True, False, False, True]
        Output: '~Stench0 & Breeze0 & ~Glitter0 & ~Bump0 & Scream0'
    """
    # Store a list of percepts
    percepts = ['Stench', 'Breeze', 'Glitter', 'Bump', 'Scream']
    propositions = []
    # Iterate over tvec
    for index, percept in enumerate(tvec):
        percept_string = ''
        # If percept is False, add '~' to the percept_string
        if not percept:
            percept_string += '~'
        # Add the corresponding percept from the percepts list
        # to the percept_string along with the t value
        percept_string += percepts[index] + str(t)
        # Append the percept_string to the propositions list
        propositions.append(percept_string)
    # Convert the propositions list to string seperated by & operators
    axiom_str = ' & '.join(propositions)
    # Return the axiom_str
    return axiom_str

# -------------------------------------------------------------------------------
# Axiom Generators: Initial Axioms
# -------------------------------------------------------------------------------

def axiom_generator_initial_location_assertions(x, y):
    """
    Assert that there is no Pit and no Wumpus in the location
    x,y := the location
    """
    # Return the axiom_string containing the proposition ~Px_y & ~Wx_y
    axiom_str = '(~{0}) & (~{1})'.format(pit_str(x, y), wumpus_str(x, y))
    return axiom_str

def axiom_generator_pits_and_breezes(x, y, xmin, xmax, ymin, ymax):
    """
    Assert that Breezes (atemporal) are only found in locations where
    there are one or more Pits in a neighboring location (or the same location!)
    x,y := the location
    xmin, xmax, ymin, ymax := the bounds of the environment; you use these
           variables to 'prune' any neighboring locations that are outside
           of the environment (and therefore are walls, so can't have Pits).
    """
    # Store of list of possible pit locations
    possiblePitLocations = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
    pits = []
    # Iterate over the possible pit locations and select those which
    # lie within the range of valid (x, y) values
    for (xvalue, yvalue) in possiblePitLocations:
        if xmin <= xvalue <= xmax and ymin <= yvalue <= ymax:
            pits.append(pit_str(xvalue, yvalue))
    # Add the current location too
    pits.append(pit_str(x, y))
    # Generate the axiom_str which specifies that if there is a breeze in (x, y)
    # location, then there can be a pit in any of the 4 adjacent valid locations and
    # vice versa
    axiom_str = '{0} <=> ({1})'.format(breeze_str(x, y), (' | ').join(pits))
    return axiom_str

def generate_pit_and_breeze_axioms(xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_pits_and_breezes(x, y, xmin, xmax, ymin, ymax))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_pits_and_breezes')
    return axioms

def axiom_generator_wumpus_and_stench(x, y, xmin, xmax, ymin, ymax):
    """
    Assert that Stenches (atemporal) are only found in locations where
    there are one or more Wumpi in a neighboring location (or the same location!)
    (Don't try to assert here that there is only one Wumpus;
    we'll handle that separately)
    x,y := the location
    xmin, xmax, ymin, ymax := the bounds of the environment; you use these
           variables to 'prune' any neighboring locations that are outside
           of the environment (and therefore are walls, so can't have Wumpi).
    """
    # Store of list of possible Wumpus locations
    possibleWumpusLocations = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
    wumpus = []
    # Iterate over the possible Wumpus locations and select those which
    # lie within the range of valid (x, y) values
    for (xvalue, yvalue) in possibleWumpusLocations:
        if xmin <= xvalue <= xmax and ymin <= yvalue <= ymax:
            wumpus.append(wumpus_str(xvalue, yvalue))
    # Add the current location too
    wumpus.append(wumpus_str(x, y))
    # Generate the axiom_str which specifies that if there is a stench in (x, y)
    # location, then there can be a Wumpus in any of the 4 adjacent valid locations and
    # vice versa
    axiom_str = '{0} <=> ({1})'.format(stench_str(x, y), (' | ').join(wumpus))
    return axiom_str

def generate_wumpus_and_stench_axioms(xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_wumpus_and_stench(x, y, xmin, xmax, ymin, ymax))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_wumpus_and_stench')
    return axioms

def axiom_generator_at_least_one_wumpus(xmin, xmax, ymin, ymax):
    """
    Assert that there is at least one Wumpus.
    xmin, xmax, ymin, ymax := the bounds of the environment.
    """
    chambers = []
    # Since the Wumpus can be in atleast one of the total number
    # of chambers, we iterate over all the possible valid (x, y)
    # coordinates and join each Wx_y using the '|' connective
    for xvalue in range(xmin, xmax + 1):
        for yvalue in range(ymin, ymax + 1):
            chambers.append(wumpus_str(xvalue, yvalue))
    axiom_str = ' | '.join(chambers)
    return axiom_str

def axiom_generator_at_most_one_wumpus(xmin, xmax, ymin, ymax):
    """
    Assert that there is at at most one Wumpus.
    xmin, xmax, ymin, ymax := the bounds of the environment.
    """
    chambers = []
    # Iterate over all the possible valid (x, y) coordinates and
    # store each chamber location in a list
    for xvalue in range(xmin, xmax + 1):
        for yvalue in range(ymin, ymax + 1):
            chambers.append((xvalue, yvalue))
            #chambers.append(wumpus_str(xvalue, yvalue))

    # A list to store axioms for each room where there can be atmost
    # one Wumpus
    axiom_list = []

    for chamber in chambers:
        notChambers = []
        notWumpus = []
        # Store the list of all other locations except 'chamber'
        for otherChamber in chambers:
            if otherChamber != chamber:
                notChambers.append(otherChamber)
        # Assert that wumpus Wx_y does not exist using the '~' connective in each
        # of the locations in 'notChambers'
        for notChamber in notChambers:
            notWumpus.append('~' + wumpus_str(notChamber[0], notChamber[1]))
        # If there is a Wumpus at 'chamber', then use implication to state that no other
        # Wumpus can exist on other Wx_y locations. This is states by connective ~Wx_y of all
        # other chambers using '&' connective.
        axiom_list.append('({0} >> ({1}))'.format(wumpus_str(chamber[0], chamber[1]), ' & '.join(notWumpus)))
    # Join all the axioms in the axiom_list using the '&' connective to assure Wumpus is
    # only in one location
    axiom_str = ' & '.join(axiom_list)
    return axiom_str

def axiom_generator_only_in_one_location(xi, yi, xmin, xmax, ymin, ymax, t=0):
    """
    Assert that the Agent can only be in one (the current xi,yi) location at time t.
    xi,yi := the current location.
    xmin, xmax, ymin, ymax := the bounds of the environment.
    t := time; default=0
    """
    notChambers = []
    # Iterate over all (x, y) co-ordinates and store the complement of each
    # Lx_y_t value except the currect location Lxi_yi_t
    for xvalue in range(xmin, xmax + 1):
        for yvalue in range(ymin, ymax + 1):
            if not (xi == xvalue and yi == yvalue):
                notChambers.append('~' + state_loc_str(xvalue, yvalue, t))
    # Append the conjunction of the current location Lxi_yi_t with all
    # other ~Lx_y_t locations
    axiom_str = '{0} & {1}'.format(state_loc_str(xi, yi, t), '{0}'.format(' & '.join(notChambers)))
    return axiom_str

def axiom_generator_only_one_heading(heading='north', t=0):
    """
    Assert that Agent can only head in one direction at a time.
    heading := string indicating heading; default='north';
               will be one of: 'north', 'east', 'south', 'west'
    t := time; default=0
    """
    # Store header axioms
    heading_axioms = [state_heading_north_str(t), state_heading_south_str(t), state_heading_east_str(t), state_heading_west_str(t)]
    # Store all possible heading values
    headings = ['north', 'south', 'east', 'west']
    # For storing the list of headers in our proposition
    headingList = []
    # Iterate over all the headings
    for index, heading_value in enumerate(headings):
        # For current heading value, append the heading string
        if heading_value == heading:
            headingList.append(heading_axioms[index])
        # For all other header values, append their completement
        else:
            headingList.append('~' + heading_axioms[index])
    # Join all the heading strings in the list using conjunction
    axiom_str = ' & '.join(headingList)
    return axiom_str

def axiom_generator_have_arrow_and_wumpus_alive(t=0):
    """
    Assert that Agent has the arrow and the Wumpus is alive at time t.
    t := time; default=0
    """
    # Store conjunction of HaveArrowt and WumpusAlivet
    axiom_str = '{0} & {1}'.format(state_have_arrow_str(t), state_wumpus_alive_str(t))
    return axiom_str

def initial_wumpus_axioms(xi, yi, width, height, heading='east'):
    """
    Generate all of the initial wumpus axioms
    xi,yi = initial location
    width,height = dimensions of world
    heading = str representation of the initial agent heading
    """
    axioms = [axiom_generator_initial_location_assertions(xi, yi)]
    axioms.extend(generate_pit_and_breeze_axioms(1, width, 1, height))
    axioms.extend(generate_wumpus_and_stench_axioms(1, width, 1, height))

    axioms.append(axiom_generator_at_least_one_wumpus(1, width, 1, height))
    axioms.append(axiom_generator_at_most_one_wumpus(1, width, 1, height))

    axioms.append(axiom_generator_only_in_one_location(xi, yi, 1, width, 1, height))
    axioms.append(axiom_generator_only_one_heading(heading))

    axioms.append(axiom_generator_have_arrow_and_wumpus_alive())

    return axioms


# -------------------------------------------------------------------------------
# Axiom Generators: Temporal Axioms (added at each time step)
# -------------------------------------------------------------------------------

def axiom_generator_location_OK(x, y, t):
    """
    Assert the conditions under which a location is safe for the Agent.
    (Hint: Are Wumpi always dangerous?)
    x,y := location
    t := time
    """
    # A location is safe if there is no pit in location (x, y) and if there is a Wumpus in (x, y),
    # then it is not alive.
    axiom_str = '{0} <=> (~{1} & ({2} >> ~{3}))'.format(state_OK_str(x, y, t), pit_str(x, y), wumpus_str(x, y), state_wumpus_alive_str(t))
    return axiom_str

def generate_square_OK_axioms(t, xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_location_OK(x, y, t))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_location_OK')
    return filter(lambda s: s != '', axioms)


# -------------------------------------------------------------------------------
# Connection between breeze / stench percepts and atemporal location properties

def axiom_generator_breeze_percept_and_location_property(x, y, t):
    """
    Assert that when in a location at time t, then perceiving a breeze
    at that time (a percept) means that the location is breezy (atemporal)
    x,y := location
    t := time
    """
    # If we are on location (x, y), then we use implication to indicate that perceiving a breeze means
    # that location is breezy. This is valid vice versa too, so we express it using a bidirectional connective. 
    axiom_str = '{0} >> ({1} <=> {2})'.format(state_loc_str(x ,y, t), percept_breeze_str(t), breeze_str(x, y))
    return axiom_str

def generate_breeze_percept_and_location_axioms(t, xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_breeze_percept_and_location_property(x, y, t))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_breeze_percept_and_location_property')
    return filter(lambda s: s != '', axioms)

def axiom_generator_stench_percept_and_location_property(x, y, t):
    """
    Assert that when in a location at time t, then perceiving a stench
    at that time (a percept) means that the location has a stench (atemporal)
    x,y := location
    t := time
    """
    # If we are on location (x, y), then we use implication to indicate that perceiving a stench means
    # that location has a stench. This is valid vice versa too, so we express it using a bidirectional connective.
    axiom_str = '{0} >> ({1} <=> {2})'.format(state_loc_str(x, y, t), percept_stench_str(t), stench_str(x, y))
    return axiom_str

def generate_stench_percept_and_location_axioms(t, xmin, xmax, ymin, ymax):
    axioms = []
    for x in range(xmin, xmax + 1):
        for y in range(ymin, ymax + 1):
            axioms.append(axiom_generator_stench_percept_and_location_property(x, y, t))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_stench_percept_and_location_property')
    return filter(lambda s: s != '', axioms)


# -------------------------------------------------------------------------------
# Transition model: Successor-State Axioms (SSA's)
# Avoid the frame problem(s): don't write axioms about actions, write axioms about
# fluents!  That is, write successor-state axioms as opposed to effect and frame
# axioms
#
# The general successor-state axioms pattern (where F is a fluent):
#   F^{t+1} <=> (Action(s)ThatCause_F^t) | (F^t & ~Action(s)ThatCauseNot_F^t)

# NOTE: this is very expensive in terms of generating many (~170 per axiom) CNF clauses!
def axiom_generator_at_location_ssa(t, x, y, xmin, xmax, ymin, ymax):
    """
    Assert the condidtions at time t under which the agent is in
    a particular location (state_loc_str: L) at time t+1, following
    the successor-state axiom pattern.
    See Section 7. of AIMA.  However...
    NOTE: the book's version of this class of axioms is not complete
          for the version in Project 3.
    x,y := location
    t := time
    xmin, xmax, ymin, ymax := the bounds of the environment.
    """
    # Agent with be at location (x, y) at time t + 1 if it is already at location (x, y)
    # at time t and exhibits any of the stationary moves such as not moving forward at
    # time t, shooting at time t, grabbing at time t, turning left at time t, turning
    # right at time t and bumping at time t + 1
    possibleActions = ['({0} & (~{1} | {2} | {3} | {4} | {5} | {6}))'.format(state_loc_str(x, y, t), action_forward_str(t),
                                                                   action_shoot_str(t), action_grab_str(t),
                                                                   action_turn_left_str(t), action_turn_right_str(t),
                                                                   percept_bump_str(t + 1))]

    # Store all possible (x, y) co-ordinate locations adjacent to the current location
    possibleLocations = [(x - 1, y), (x, y - 1), (x + 1, y), (x, y + 1)]
    # Store all heading strings
    heading_strings = [state_heading_east_str(t), state_heading_north_str(t),
                      state_heading_west_str(t), state_heading_south_str(t)]
    # Iterate over all possible adjacent locations
    for index, (xvalue, yvalue) in enumerate(possibleLocations):
        # If the agent is at a valid adjacent node, then it can reach the current location
        # on moving forward at time t depending on its header orientation at time t
        if xmin <= xvalue <= xmax and ymin <= yvalue <= ymax:
            possibleActions.append('({0} & {1} & {2})'.format(state_loc_str(xvalue, yvalue, t), heading_strings[index], action_forward_str(t)))

    # Store location string of the successor state
    successorLocation = state_loc_str(x, y, t + 1)
    # If agent is at current location (x, y) at time t, then it can reach there using
    # a disjunction of all the above possible moves
    axiom_str = '{0} <=> ({1})'.format(successorLocation,' | '.join(possibleActions))
    return axiom_str

def generate_at_location_ssa(t, x, y, xmin, xmax, ymin, ymax, heading):
    """
    The full at_location SSA converts to a fairly large CNF, which in
    turn causes the KB to grow very fast, slowing overall inference.
    We therefore need to restric generating these axioms as much as possible.
    This fn generates the at_location SSA only for the current location and
    the location the agent is currently facing (in case the agent moves
    forward on the next turn).
    This is sufficient for tracking the current location, which will be the
    single L location that evaluates to True; however, the other locations
    may be False or Unknown.
    """
    axioms = [axiom_generator_at_location_ssa(t, x, y, xmin, xmax, ymin, ymax)]
    if heading == 'west' and x - 1 >= xmin:
        axioms.append(axiom_generator_at_location_ssa(t, x - 1, y, xmin, xmax, ymin, ymax))
    if heading == 'east' and x + 1 <= xmax:
        axioms.append(axiom_generator_at_location_ssa(t, x + 1, y, xmin, xmax, ymin, ymax))
    if heading == 'south' and y - 1 >= ymin:
        axioms.append(axiom_generator_at_location_ssa(t, x, y - 1, xmin, xmax, ymin, ymax))
    if heading == 'north' and y + 1 <= ymax:
        axioms.append(axiom_generator_at_location_ssa(t, x, y + 1, xmin, xmax, ymin, ymax))
    if utils.all_empty_strings(axioms):
        utils.print_not_implemented('axiom_generator_at_location_ssa')
    return filter(lambda s: s != '', axioms)


# ----------------------------------

def axiom_generator_have_arrow_ssa(t):
    """
    Assert the conditions at time t under which the Agent
    has the arrow at time t+1
    t := time
    """
    # Agent has arrow at time t + 1 if it has an arrow at time t and has not already
    # shot the arrow at time t, and vice versa
    axiom_str = '{0} <=> ({1} & ~{2})'.format(state_have_arrow_str(t + 1), state_have_arrow_str(t), action_shoot_str(t))
    return axiom_str

def axiom_generator_wumpus_alive_ssa(t):
    """
    Assert the conditions at time t under which the Wumpus
    is known to be alive at time t+1
    (NOTE: If this axiom is implemented in the standard way, it is expected
    that it will take one time step after the Wumpus dies before the Agent
    can infer that the Wumpus is actually dead.)
    t := time
    """
    # Wumpus is alive at time t + 1 if it is alive at time t and there is not
    # scream percept at time t + 1, and vice versa
    axiom_str = '{0} <=> ({1} & ~{2})'.format(state_wumpus_alive_str(t + 1), state_wumpus_alive_str(t), percept_scream_str(t + 1))
    return axiom_str

# ----------------------------------


def axiom_generator_heading_north_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be North at time t+1
    t := time
    """
    # Agent will be heading towards north at time t + 1 if it was already heading north at time t
    # and it continues to make any of the moves which does not change its header value. These
    # include waiting at time t, grabbing at time t, shooting at time t, bumping at time t + 1 or
    # moving forward at time t
    headerConsistentMoves = '({0} & ({1} | {2} | {3} | {4} | {5}))'.format(state_heading_north_str(t), action_forward_str(t),
                                                            action_grab_str(t), action_wait_str(t),
                                                            action_shoot_str(t), percept_bump_str(t + 1))
    # Agent will be heading towards north at time t + 1 if it was heading east at time t and
    # turns left at time t.
    turnLeft = '({0} & {1})'.format(state_heading_east_str(t), action_turn_left_str(t))
    # Agent will be heading towards north at time t + 1 if it was heading west at time t and
    # turns right at time t.
    turnRight = '({0} & {1})'.format(state_heading_west_str(t), action_turn_right_str(t))
    # The resultant axiom states that the for an agent to be heading towards north at time t + 1, it
    # should satisfy at least one of the above 3 cases, and vice versa.
    axiom_str = '{0} <=> ({1} | {2} | {3})'.format(state_heading_north_str(t + 1), headerConsistentMoves, turnLeft, turnRight)
    return axiom_str

def axiom_generator_heading_east_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be East at time t+1
    t := time
    """
    # Agent will be heading towards east at time t + 1 if it was already heading east at time t
    # and it continues to make any of the moves which does not change its header value. These
    # include waiting at time t, grabbing at time t, shooting at time t, bumping at time t + 1 or
    # moving forward at time t
    headerConsistentMoves = '({0} & ({1} | {2} | {3} | {4} | {5}))'.format(state_heading_east_str(t), action_forward_str(t),
                                                            action_grab_str(t), action_wait_str(t),
                                                            action_shoot_str(t), percept_bump_str(t + 1))
    # Agent will be heading towards east at time t + 1 if it was heading south at time t and
    # turns left at time t.
    turnLeft = '({0} & {1})'.format(state_heading_south_str(t), action_turn_left_str(t))
    # Agent will be heading towards east at time t + 1 if it was heading north at time t and
    # turns right at time t.
    turnRight = '({0} & {1})'.format(state_heading_north_str(t), action_turn_right_str(t))
    # The resultant axiom states that the for an agent to be heading towards east at time t + 1, it
    # should satisfy at least one of the above 3 cases, and vice versa.
    axiom_str = '{0} <=> ({1} | {2} | {3})'.format(state_heading_east_str(t + 1), headerConsistentMoves, turnLeft, turnRight)
    return axiom_str

def axiom_generator_heading_south_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be South at time t+1
    t := time
    """
    # Agent will be heading towards south at time t + 1 if it was already heading south at time t
    # and it continues to make any of the moves which does not change its header value. These
    # include waiting at time t, grabbing at time t, shooting at time t, bumping at time t + 1 or
    # moving forward at time t
    headerConsistentMoves = '({0} & ({1} | {2} | {3} | {4} | {5}))'.format(state_heading_south_str(t), action_forward_str(t),
                                                            action_grab_str(t), action_wait_str(t),
                                                            action_shoot_str(t), percept_bump_str(t + 1))
    # Agent will be heading towards south at time t + 1 if it was heading west at time t and
    # turns left at time t.
    turnLeft = '({0} & {1})'.format(state_heading_west_str(t), action_turn_left_str(t))
    # Agent will be heading towards south at time t + 1 if it was heading east at time t and
    # turns right at time t.
    turnRight = '({0} & {1})'.format(state_heading_east_str(t), action_turn_right_str(t))
    # The resultant axiom states that the for an agent to be heading towards south at time t + 1, it
    # should satisfy at least one of the above 3 cases, and vice versa.
    axiom_str = '{0} <=> ({1} | {2} | {3})'.format(state_heading_south_str(t + 1), headerConsistentMoves, turnLeft, turnRight)
    return axiom_str

def axiom_generator_heading_west_ssa(t):
    """
    Assert the conditions at time t under which the
    Agent heading will be West at time t+1
    t := time
    """
    # Agent will be heading towards west at time t + 1 if it was already heading west at time t
    # and it continues to make any of the moves which does not change its header value. These
    # include waiting at time t, grabbing at time t, shooting at time t, bumping at time t + 1 or
    # moving forward at time t
    headerConsistentMoves = '({0} & ({1} | {2} | {3} | {4} | {5}))'.format(state_heading_west_str(t), action_forward_str(t),
                                                            action_grab_str(t), action_wait_str(t),
                                                            action_shoot_str(t), percept_bump_str(t + 1))
    # Agent will be heading towards west at time t + 1 if it was heading north at time t and
    # turns left at time t.
    turnLeft = '({0} & {1})'.format(state_heading_north_str(t), action_turn_left_str(t))
    # Agent will be heading towards west at time t + 1 if it was heading south at time t and
    # turns right at time t.
    turnRight = '({0} & {1})'.format(state_heading_south_str(t), action_turn_right_str(t))
    # The resultant axiom states that the for an agent to be heading towards west at time t + 1, it
    # should satisfy at least one of the above 3 cases, and vice versa.
    axiom_str = '{0} <=> ({1} | {2} | {3})'.format(state_heading_west_str(t + 1), headerConsistentMoves, turnLeft, turnRight)
    return axiom_str

def generate_heading_ssa(t):
    """
    Generates all of the heading SSAs.
    """
    return [axiom_generator_heading_north_ssa(t),
            axiom_generator_heading_east_ssa(t),
            axiom_generator_heading_south_ssa(t),
            axiom_generator_heading_west_ssa(t)]

def generate_non_location_ssa(t):
    """
    Generate all non-location-based SSAs
    """
    axioms = []  # all_state_loc_ssa(t, xmin, xmax, ymin, ymax)
    axioms.append(axiom_generator_have_arrow_ssa(t))
    axioms.append(axiom_generator_wumpus_alive_ssa(t))
    axioms.extend(generate_heading_ssa(t))
    return filter(lambda s: s != '', axioms)

# ----------------------------------

def axiom_generator_heading_only_north(t):
    """
    Assert that when heading is North, the agent is
    not heading any other direction.
    t := time
    """
    # If Agent is heading North if and only if Agent is not heading South, West and East
    axiom_str = '{0} <=> (~{1} & ~{2} & ~{3})'.format(state_heading_north_str(t),
                                                      state_heading_south_str(t),
                                                      state_heading_west_str(t),
                                                      state_heading_east_str(t))
    return axiom_str

def axiom_generator_heading_only_east(t):
    """
    Assert that when heading is East, the agent is
    not heading any other direction.
    t := time
    """
    # If Agent is heading East if and only if Agent is not heading North, South and West
    axiom_str = '{0} <=> (~{1} & ~{2} & ~{3})'.format(state_heading_east_str(t),
                                                      state_heading_north_str(t),
                                                      state_heading_south_str(t),
                                                      state_heading_west_str(t))
    return axiom_str

def axiom_generator_heading_only_south(t):
    """
    Assert that when heading is South, the agent is
    not heading any other direction.
    t := time
    """
    # If Agent is heading South if and only if Agent is not heading North, West and East
    axiom_str = '{0} <=> (~{1} & ~{2} & ~{3})'.format(state_heading_south_str(t),
                                                      state_heading_north_str(t),
                                                      state_heading_west_str(t),
                                                      state_heading_east_str(t),)
    return axiom_str

def axiom_generator_heading_only_west(t):
    """
    Assert that when heading is West, the agent is
    not heading any other direction.
    t := time
    """
    # If Agent is heading West if and only if Agent is not heading North, South and East
    axiom_str = '{0} <=> (~{1} & ~{2} & ~{3})'.format(state_heading_west_str(t),
                                                      state_heading_north_str(t),
                                                      state_heading_south_str(t),
                                                      state_heading_east_str(t))
    return axiom_str

def generate_heading_only_one_direction_axioms(t):
    return [axiom_generator_heading_only_north(t),
            axiom_generator_heading_only_east(t),
            axiom_generator_heading_only_south(t),
            axiom_generator_heading_only_west(t)]


def axiom_generator_only_one_action_axioms(t):
    """
    Assert that only one axion can be executed at a time.
    t := time
    """
    # Store a list of all action strings
    action_strings = [action_forward_str(t), action_grab_str(t), action_shoot_str(t), action_climb_str(t),
                      action_turn_left_str(t), action_turn_right_str(t), action_wait_str(t)]
    axioms = []
    # Iterate over all the actions 
    for index, currentAction in enumerate(action_strings):
        otherActions = []
        # Store all other actions except the current actions in a list
        for idx, otherAction in enumerate(action_strings):
            if idx != index:
                otherActions.append('~' + otherAction)
        # If the current actions is true, then all other actions are false
        axioms.append('({0} <=> ({1}))'.format(currentAction, ' & '.join(otherActions)))
    # Now join all the axioms using conjunction
    axiom_str = ' & '.join(axioms)
    return axiom_str

def generate_mutually_exclusive_axioms(t):
    """
    Generate all time-based mutually exclusive axioms.
    """
    axioms = []

    # must be t+1 to constrain which direction could be heading _next_
    axioms.extend(generate_heading_only_one_direction_axioms(t + 1))

    # actions occur in current time, after percept
    axioms.append(axiom_generator_only_one_action_axioms(t))

    return filter(lambda s: s != '', axioms)

# -------------------------------------------------------------------------------
