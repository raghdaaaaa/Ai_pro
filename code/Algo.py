# # Problem Definition and Search Algorithms for Mini Ludo



# # Ludo Problem Definition
# class LudoProblem:
#     STEP_CHOICES = list(range(1, 11)) # Steps can be 1 to 10

#     def __init__(self, state, player): # state is a list of Lists
#         self.state  = [list(s) for s in state] # Deep copy to avoid mutation issues
#         self.player = player # Current player index (0, 1, or 2)
#         self.n      = len(state) # Number of players

#     def actions(self): # Returns a list of (piece_index, step) tuples for legal moves
#         legal = []
#         for piece_idx in range(2):
#             current_pos = self.state[self.player][piece_idx] # Current position of the piece
#             if current_pos >= END:
#                 continue
#             for step in self.STEP_CHOICES: # Check if the move is legal  
#                 if current_pos + step <= END:
#                     legal.append((piece_idx, step))
#         return legal if legal else [(-1, 0)] # If no legal moves, return a dummy action

#     def result(self, piece_idx, step): # Returns the new state 
#         new_state  = [list(s) for s in self.state] # Deep copy to avoid mutating the original state
#         captured   = False #  capture occurred
#         extra_turn = False #  player gets an extra turn  

#         if piece_idx == -1:
#             return new_state, False, False

#         new_pos = new_state[self.player][piece_idx] + step
#         new_state[self.player][piece_idx] = new_pos

#         if new_pos < 52:
#             new_cell = ring_pos_to_cell(self.player, new_pos)
#             if new_cell not in SAFE_SPOTS:
#                 for opp in range(self.n):
#                     if opp == self.player: continue
#                     for i in range(2):
#                         opp_pos = new_state[opp][i]
#                         if 0 < opp_pos < 52:
#                             if ring_pos_to_cell(opp, opp_pos) == new_cell:
#                                 new_state[opp][i] = 0
#                                 captured   = True
#                                 extra_turn = True

#         return new_state, captured, extra_turn

#     # Check if the game is over and return the winner player index
#     def is_terminal(self, state=None):
#         s = state if state else self.state
#         for p in range(self.n):
#             if all(pos >= END for pos in s[p]):
#                 return p
#         return None

# #  Evaluation
# # ══════════════════════════════════════════════════════
# # Score the board state from the given player's perspective
# def evaluate(state, player): # Higher score means better for the player
#     n     = len(state)
#     score = 0.0

#     for piece_idx in range(2): #
#         pos = state[player][piece_idx]

#         if pos >= END:
#             score += 10000 # Piece has reached the end
#             continue
#         if pos == 0:
#             score -= 1000 # Piece is still at home
#             continue

#         score += pos * 65 # Progress towards the end is good
#         if pos > 50:  
#             score += (pos - 50) * 100 # In home stretch is very good

#         cell = ring_pos_to_cell(player, pos)
#         if cell in SAFE_SPOTS: # Safe spots are good for defense
#             score += 200

#         if cell not in SAFE_SPOTS: 
#             for opp in range(n):
#                 if opp == player: continue
#                 for opp_idx in range(2):
#                     opp_pos = state[opp][opp_idx]
#                     if 0 < opp_pos < 52:
#                         for step in range(1, 11):
#                             if opp_pos + step <= END:
#                                 opp_cell = ring_pos_to_cell(opp, opp_pos + step)
#                                 if opp_cell == cell:
#                                     score -= 1500 # Opponent can capture us next turn
#                                     break

#         if pos < 52 and cell not in SAFE_SPOTS:
#             for opp in range(n):
#                 if opp == player: continue
#                 for opp_idx in range(2):
#                     opp_pos = state[opp][opp_idx]
#                     if 0 < opp_pos < 52:
#                         if ring_pos_to_cell(opp, opp_pos) == cell:
#                             score += 2000 # We can capture an opponent on this cell

#     for opp in range(n):
#         if opp == player: continue
#         for piece_idx in range(2):
#             opp_pos = state[opp][piece_idx]
#             if opp_pos >= END:
#                 score -= 10000
#             elif opp_pos > 0:
#                 score -= opp_pos * 50 # Opponent's progress is bad for us

#     return score

# #  Minimax Algorithm with Alpha-Beta Pruning
# # ══════════════════════════════════════════════════════
# # Search the game tree to find the best move using alpha-beta pruning
# def minimax(state, player, depth, alpha, beta, is_maximizing, ai_player):
#     n        = len(state)
#     problem  = LudoProblem(state, player)
#     terminal = problem.is_terminal()
    
#     # Terminal state: return a large positive score if AI wins, large negative if AI loses
#     if terminal is not None:
#         return 100000 if terminal == ai_player else -100000
#     if depth == 0:
#         return evaluate(state, ai_player) 

#     actions = problem.actions()
#     actions.sort(key=lambda x: x[1], reverse=True)
     
#     # Maximizing player (AI) tries to maximize the score
#     if is_maximizing:
#         best = -float('inf')
#         for piece_idx, step in actions:
#             new_state, captured, extra_turn = problem.result(piece_idx, step)
#             next_player     = player if extra_turn else (player + 1) % n
#             next_maximizing = True   if extra_turn else not is_maximizing
#             val   = minimax(new_state, next_player, depth - 1, alpha, beta, next_maximizing, ai_player)
#             best  = max(best, val)
#             alpha = max(alpha, val)
#             if beta <= alpha: break
#         return best
#     else:
#         best = float('inf')
#         for piece_idx, step in actions:
#             new_state, captured, extra_turn = problem.result(piece_idx, step)
#             next_player     = player if extra_turn else (player + 1) % n
#             next_maximizing = False  if extra_turn else not is_maximizing
#             val  = minimax(new_state, next_player, depth - 1, alpha, beta, next_maximizing, ai_player)
#             best = min(best, val)
#             beta = min(beta, val)
#             if beta <= alpha: break
#         return best

# # Find the best action for the AI by evaluating all possible moves
# def get_best_move(state, player, depth=3):
#     n        = len(state)
#     problem  = LudoProblem(state, player)
#     actions  = problem.actions()
#     best_score  = -float('inf')
#     best_action = actions[0]
#     action_log  = []

#     for piece_idx, step in actions:
#         new_state, captured, extra_turn = problem.result(piece_idx, step)
#         next_player     = player if extra_turn else (player + 1) % n
#         next_maximizing = True   if extra_turn else False
#         score = minimax(new_state, next_player, depth - 1,
#                         -float('inf'), float('inf'), next_maximizing, player)
#         if captured:
#             score += 2000
#         action_log.append((piece_idx, step, score))
#         if score > best_score:
#             best_score  = score
#             best_action = (piece_idx, step)

#     return best_action[0], best_action[1], best_score, action_log

# #  Greedy Algorithm 
# # ══════════════════════════════════════════════════════
# # Pick a move using simple priority rules (capture > win > biggest step)
# def get_greedy_move(state, player):
#     problem = LudoProblem(state, player)
#     actions = problem.actions()

#     capture_moves = []
#     win_moves     = []
#     normal_moves  = []

#     for piece_idx, step in actions:
#         pos = state[player][piece_idx]
#         new_state, captured, _ = problem.result(piece_idx, step)

#         if captured:
#             capture_moves.append((piece_idx, step))
#         elif pos + step == END:          # Winning move
#             win_moves.append((piece_idx, step))
#         else:
#             normal_moves.append((piece_idx, step))

#     # Prioritize capture moves, then winning moves, then normal moves
#     if capture_moves:
#         pool = capture_moves
#     elif win_moves:
#         pool = win_moves
#     else:
#         pool = normal_moves

#     best_pi, best_step = max(pool, key=lambda x: x[1])

#     ns, _, _ = problem.result(best_pi, best_step)
#     score = evaluate(ns, player)
#     return best_pi, best_step, score
