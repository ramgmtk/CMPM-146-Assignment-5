CMPM 146 Programming Assignment 5
Members:
Rammohan Ramanathan
Ana Guo

Search Approach:
The search is a standard A* search. When evaluating neighboring nodes the graph() function is used to fetch which neighbors are legal actions.
The main difference is that the search does not rune 'while' the queue isn't empty, but runs while there is still time alloted for the search.
If the queue does ampty and a goal isn't reached, it will throw and catch an IndexError.

Heuristic Approach:
The Heuristic has good elements and many bad ones. Objectively the heuristic is case specific in that it forsure will not work on situations that ask: goal "plank" : 100.
The Heuristic function is a series of checks that are meant to prune the search results.

Good decisions:
Do not craft more than 1 of a unique tool. I.e. do not make 2 benches, 2 stone pickaxes etc.
Do not use a tool of a lower tier if a higher 1 is available. I.e. if the action says to use a wooden pickaxe for stone, but we have an iron pickaxe, do not procede with this action.

Bad Decision:
Do not take more of a material than we can craft with. I.e. Do not take more than 8 cobble at a time, because the most cobble intensive crafting procedure needs at most 8 cobble.
Gathering wood should be last resort. I.e. we only gather wood if every other action is a waste of time.
Do not gather more coal than we have iron. I.e. We only need coal to smelt iron so it does not make sense to gather more coal than iron. vice versa.

Conclusion:
The heuristic is not good. It solves the programming assignements test cases, however it prioritizes crafting towards expensive items and ignores cases of gathering for material surplus.