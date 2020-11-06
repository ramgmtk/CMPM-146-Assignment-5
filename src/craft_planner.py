import json
from collections import namedtuple, defaultdict, OrderedDict
from timeit import default_timer as time

from heapq import heappop, heappush

Recipe = namedtuple('Recipe', ['name', 'check', 'effect', 'cost'])

class State(OrderedDict):
    """ This class is a thin wrapper around an OrderedDict, which is simply a dictionary which keeps the order in
        which elements are added (for consistent key-value pair comparisons). Here, we have provided functionality
        for hashing, should you need to use a state as a key in another dictionary, e.g. distance[state] = 5. By
        default, dictionaries are not hashable. Additionally, when the state is converted to a string, it removes
        all items with quantity 0.

        Use of this state representation is optional, should you prefer another.
    """

    def __key(self):
        return tuple(self.items())

    def __hash__(self):
        return hash(self.__key())

    def __lt__(self, other):
        return self.__key() < other.__key()

    def copy(self):
        new_state = State()
        new_state.update(self)
        return new_state

    def __str__(self):
        return str(dict(item for item in self.items() if item[1] > 0))


def make_checker(rule):
    # Implement a function that returns a function to determine whether a state meets a
    # rule's requirements. This code runs once, when the rules are constructed before
    # the search is attempted.

    def check(state):
        # This code is called by graph(state) and runs millions of times.
        # Tip: Do something with rule['Consumes'] and rule['Requires'].
        if 'Requires' in rule.keys():
            for required_key_item in rule['Requires'].keys():
                if state.get(required_key_item) == 0:
                    return False
        if 'Consumes' in rule.keys():
            for required_crafting_item, required_amount in rule['Consumes'].items():
                if state.get(required_crafting_item) < required_amount:
                    return False
        return True

    return check


def make_effector(rule):
    # Implement a function that returns a function which transitions from state to
    # new_state given the rule. This code runs once, when the rules are constructed
    # before the search is attempted.

    def effect(state):
        # This code is called by graph(state) and runs millions of times
        # Tip: Do something with rule['Produces'] and rule['Consumes'].
        next_state = state.copy()
        if 'Consumes' in rule.keys():
            for consumed_item, consumed_amount in rule['Consumes'].items():
                next_state[consumed_item] = state[consumed_item] - consumed_amount
        if 'Produces' in rule.keys():
            for produced_item, produced_amount in rule['Produces'].items():
                next_state[produced_item] = next_state[produced_item] + produced_amount
        return next_state

    return effect


def make_goal_checker(goal):
    # Implement a function that returns a function which checks if the state has
    # met the goal criteria. This code runs once, before the search is attempted.

    def is_goal(state):
        # This code is used in the search process and may be called millions of times.
        for goal_item, amount in goal.items():
            if state.get(goal_item) < amount:
                return False
        return True

    return is_goal


def graph(state):
    # Iterates through all recipes/rules, checking which are valid in the given state.
    # If a rule is valid, it returns the rule's name, the resulting state after application
    # to the given state, and the cost for the rule.
    for r in all_recipes:
        if r.check(state):
            yield (r.name, r.effect(state), r.cost)


def heuristic(state, action):
    # Implement your heuristic here!
    total_weight = 0
    
    #bELOW ARE DECENT HEURISTICS
    #items where there is no need to have more than 1
    redundant_list = ["bench", "cart", "furnace", "iron_axe", "iron_pickaxe", "stone_axe", "stone_pickaxe", "wooden_axe", "wooden_pickaxe"]
    for redundancy in redundant_list:
        if state[redundancy] > 1 :
            return float('inf')
            
    #if we have a tool of a higher tier do not use the lower tier one.
    if 'stone_pickaxe' in action:
        if state['iron_pickaxe'] >= 1:
            return float('inf')
    elif 'wooden_pickaxe' in action:
        if state['iron_pickaxe'] >= 1 or state['stone_pickaxe'] >= 1:
            return float('inf')
    if 'stone_axe' in action:
        if state['iron_axe'] >= 1:
            return float('inf')
    elif 'wooden_axe' in action:
        if state['iron_axe'] >= 1 or state['stone_axe'] >= 1:
            return float('inf')
    elif 'punch' in action:
        if state['wooden_axe'] >= 1 or state['iron_axe'] >= 1 or state['stone_axe'] >= 1:
            return float('inf')
            
    #BELOW ARE MORE CASE SPECIFIC HEURISTICS THAT WILL NOT WORK FOR GOALS SUCH AS: GET PLANK: 30        
    #we do not need more coal than we have ore
    #might not work cause what if the goal is 64 coal? Then the planner will try to seek at least 64 ore as well     
    if 'for coal' in action or 'for ore' in action:
        if abs(state['ore'] - state['coal']) > 1:
            total_weight += float('inf')
   
    #THIS BELOW HEURISTIC IS INCREDIBLY CASE SENSITIVE
    #gather wood as last resort
    if 'for wood' in action:
        if state['wood'] > 0:
            total_weight += 300
    
    #essentially take no more of these than what we can craft at a given moment.
    #again this heurstic ignores case specific actions.
    max_bench_space = {"cobble" : 8, "ingot" : 6, "plank" : 13, "stick" : 5, "wood" : 1, "ore" : 6, "coal" : 6}   
    for resource, amount in max_bench_space.items():
        if state[resource] > amount:
            total_weight += float('inf')
    
    return total_weight

def search(graph, state, is_goal, limit, heuristic):

    start_time = time()
    queue = [(0, state)]
    predecessor = { state : (None, None) } 
    cost_to_travel = { state : 0 }

    # Implement your search here! Use your heuristic here!
    # When you find a path to the goal return a list of tuples [(state, action)]
    # representing the path. Each element (tuple) of the list represents a state
    # in the path and the action that took you to this state
    try :
        while time() - start_time < limit:
            _, current_state = heappop(queue)
            current_cost = cost_to_travel[current_state]
            
            if is_goal(current_state):
                print("Path found in : ", time() - start_time," seconds")
                resulting_path = []
                state, action = predecessor[current_state]
                while state:
                    resulting_path.append((state, action))
                    state, action = predecessor[state]
                print("Total Actions: ", len(resulting_path))
                print("Total Cost: ", cost_to_travel.get(current_state))
                return resulting_path[::-1]
            
            for recipe_name, next_state, state_cost in graph(current_state):
                craft_cost = state_cost + current_cost
                if next_state not in cost_to_travel or craft_cost < cost_to_travel[next_state]:
                    cost_to_travel[next_state] = craft_cost
                    priority = craft_cost + heuristic(next_state, recipe_name)
                    heappush(queue, (priority, next_state))
                    predecessor[next_state] = (current_state, recipe_name)                          
    except IndexError:
        print("Queue empty: path failed")
        
    # Failed to find a path
    print(time() - start_time, 'seconds.')
    print("Failed to find a path from", state, 'within time limit.')
    return None

if __name__ == '__main__':
    with open('Crafting.json') as f:
        Crafting = json.load(f)

    # # List of items that can be in your inventory:
    # print('All items:', Crafting['Items'])
    #
    # # List of items in your initial inventory with amounts:
    # print('Initial inventory:', Crafting['Initial'])
    #
    # # List of items needed to be in your inventory at the end of the plan:
    # print('Goal:',Crafting['Goal'])
    #
    # # Dict of crafting recipes (each is a dict):
    # print('Example recipe:','craft stone_pickaxe at bench ->',Crafting['Recipes']['craft stone_pickaxe at bench'])

    # Build rules
    all_recipes = []
    for name, rule in Crafting['Recipes'].items():
        checker = make_checker(rule)
        effector = make_effector(rule)
        recipe = Recipe(name, checker, effector, rule['Time'])
        all_recipes.append(recipe)
        
    # Create a function which checks for the goal
    is_goal = make_goal_checker(Crafting['Goal'])
    

    # Initialize first state from initial inventory
    state = State({key: 0 for key in Crafting['Items']})
    state.update(Crafting['Initial'])

    # Search for a solution
    resulting_plan = search(graph, state, is_goal, 200, heuristic)

    if resulting_plan:
        # Print resulting plan
        for state, action in resulting_plan:
            print('\t',state)
            print(action)
