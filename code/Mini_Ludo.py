import tkinter as tk
from tkinter import messagebox

#  CONSTANTS & BOARD LAYOUT
# ══════════════════════════════════════════════════════
END  = 57
CELL = 40
COLS, ROWS = 15, 15
W, H = COLS * CELL, ROWS * CELL

# Colors and positions
PLAYER_COLORS = ["#2196F3", "#F44336", "#4CAF50"]
PLAYER_NAMES  = ["AI الأزرق (Minimax)", "AI الأحمر (Greedy)", "أنت (Human)"]
BOARD_COLORS = {
    "BLUE": "#65B6F9", "RED": "#FF6675", "YELLOW": "#FAEC6A", "GREEN": "#7DFF81",
    "GOAL_BLUE": "#2196F3", "GOAL_RED": "#F44336",
    "GOAL_YELLOW": "#FBC02D", "GOAL_GREEN": "#4CAF50"
}

TRACK_COLOR, GRID_COLOR, BG_COLOR = "#FFFFFF", "#443C3C", "#F5F5F5"
SAFE_SPOTS = [(6,2),(2,8),(8,12),(12,6),(1,6),(6,13),(13,8),(8,1)]
RING = [
    (14,6),(13,6),(12,6),(11,6),(10,6),(9,6),(8,5),(8,4),(8,3),(8,2),(8,1),(8,0),
    (7,0),(6,0),(6,1),(6,2),(6,3),(6,4),(6,5),(5,6),(4,6),(3,6),(2,6),(1,6),(0,6),
    (0,7),(0,8),(1,8),(2,8),(3,8),(4,8),(5,8),(6,9),(6,10),(6,11),(6,12),(6,13),(6,14),
    (7,14),(8,14),(8,13),(8,12),(8,11),(8,10),(8,9),(9,8),(10,8),(11,8),(12,8),(13,8),(14,8),(14,7)
]

# Starting index of each player on the ring
START_IDX = {0: 0, 1: 26, 2: 39}

# HOME_COLS[player] gives the home column cells for each player when they enter the home stretch (pos > 51)
HOME_COLS = {
    0: [(13,7),(12,7),(11,7),(10,7),(9,7),(8,7)],
    1: [(1,7),(2,7),(3,7),(4,7),(5,7),(6,7)],
    2: [(7,13),(7,12),(7,11),(7,10),(7,9),(7,8)],   
}

HOME_DISPLAY = {
    0: [(1*CELL+20, 12*CELL+20), (3*CELL+20, 12*CELL+20)],
    1: [(10*CELL+20, 2*CELL+20), (12*CELL+20, 2*CELL+20)],
    2: [(10*CELL+20,12*CELL+20), (12*CELL+20,12*CELL+20)],
}
 # Returns the (row, col) cell for a given player's piece position on the ring
def ring_pos_to_cell(player, pos):
    pos = int(pos)
    if pos <= 0: return None
    if pos >= END: return (7, 7)
    if pos > 51:
        idx = pos - 52
        return HOME_COLS[player][idx] if idx < len(HOME_COLS[player]) else (7, 7)
    return RING[(START_IDX[player] + pos - 1) % 52]

#  LudoProblem
# ══════════════════════════════════════════════════════
class LudoProblem:
    STEP_CHOICES = list(range(1, 11)) # Steps can be 1 to 10

    def __init__(self, state, player): # state is a list of Lists
        self.state  = [list(s) for s in state] # Deep copy to avoid mutation issues
        self.player = player # Current player index (0, 1, or 2)
        self.n      = len(state) # Number of players

    def actions(self): # Returns a list of (piece_index, step) tuples for legal moves
        legal = []
        for piece_idx in range(2):
            current_pos = self.state[self.player][piece_idx] # Current position of the piece
            if current_pos >= END:
                continue
            for step in self.STEP_CHOICES: # Check if the move is legal  
                if current_pos + step <= END:
                    legal.append((piece_idx, step))
        return legal if legal else [(-1, 0)] # If no legal moves, return a dummy action

    def result(self, piece_idx, step): # Returns the new state 
        new_state  = [list(s) for s in self.state] # Deep copy to avoid mutating the original state
        captured   = False #  capture occurred
        extra_turn = False #  player gets an extra turn  

        if piece_idx == -1:
            return new_state, False, False

        new_pos = int(self.state[self.player][piece_idx] + step)
        new_state[self.player][piece_idx] = new_pos

        if new_pos < 52:
            new_cell = ring_pos_to_cell(self.player, new_pos)
            if new_cell not in SAFE_SPOTS:
                for opp in range(self.n):
                    if opp == self.player: continue
                    for i in range(2):
                        opp_pos = new_state[opp][i]
                        if 0 < opp_pos < 52:
                            if ring_pos_to_cell(opp, opp_pos) == new_cell:
                                new_state[opp][i] = 0
                                captured   = True
                                extra_turn = True

        return new_state, captured, extra_turn

    # Check if the game is over and return the winner player index
    def is_terminal(self, state=None):
        s = state if state else self.state
        for p in range(self.n):
            if all(pos >= END for pos in s[p]):
                return p
        return None

#  Evaluation
# ══════════════════════════════════════════════════════
# AI Logic - Evaluation & Search Algorithms
# ══════════════════════════════════════════════════════

def evaluate(state, player): # Higher score means better for the player
    n     = len(state)
    score = 0.0

    for piece_idx in range(2):
        pos = state[player][piece_idx]

        if pos >= END:
            score += 100.0 # Piece has reached the end (Top Priority)
            continue
        if pos == 0:
            score -= 30.0 # Piece is still at home
            continue

        # Progress Score: The further along the track, the better
        score += pos * 0.5 
        
        if pos > 50:  
            score += (pos - 50) * 1.5 # In home stretch is very good

        cell = ring_pos_to_cell(player, pos)
        if cell in SAFE_SPOTS: # Safe spots are good for defense
            score += 2.0

        # (Opponent can capture us)
        if cell not in SAFE_SPOTS: 
            for opp in range(n):
                if opp == player: continue
                for opp_idx in range(2):
                    opp_pos = state[opp][opp_idx]
                    if 0 < opp_pos < 52:
                        for step in range(1, 11):
                            if opp_pos + step <= END:
                                opp_cell = ring_pos_to_cell(opp, opp_pos + step)
                                if opp_cell == cell:
                                    score -= 15.0 
                                    break

        # We can capture an opponent on this cell
        if pos < 52 and cell not in SAFE_SPOTS:
            for opp in range(n):
                if opp == player: continue
                for opp_idx in range(2):
                    opp_pos = state[opp][opp_idx]
                    if 0 < opp_pos < 52:
                        if ring_pos_to_cell(opp, opp_pos) == cell:
                            score += 20.0 

    # Endgame Penalty: Opponents close to winning should reduce our score
    for opp in range(n):
        if opp == player: continue
        for piece_idx in range(2):
            opp_pos = state[opp][piece_idx]
            if opp_pos >= END:
                score -= 100.0
            elif opp_pos > 0:
                score -= opp_pos * 0.05 

    return score

#  Minimax Algorithm with Alpha-Beta Pruning
# ══════════════════════════════════════════════════════
def minimax(state, player, depth, alpha, beta, is_maximizing, ai_player):
    n         = len(state)
    problem   = LudoProblem(state, player)
    terminal  = problem.is_terminal()
    
    if terminal is not None:
        return 1000.0 if terminal == ai_player else -1000.0
    
    if depth == 0:
        return evaluate(state, ai_player) 

    actions = problem.actions()
    actions.sort(key=lambda x: x[1], reverse=True)
     
    if is_maximizing:
        best = -float('inf')
        for piece_idx, step in actions:
            new_state, captured, extra_turn = problem.result(piece_idx, step)
            next_player     = player if extra_turn else (player + 1) % n
            next_maximizing = True   if extra_turn else not is_maximizing
            val   = minimax(new_state, next_player, depth - 1, alpha, beta, next_maximizing, ai_player)
            best  = max(best, val)
            alpha = max(alpha, val)
            if beta <= alpha: break
        return best
    else:
        best = float('inf')
        for piece_idx, step in actions:
            new_state, captured, extra_turn = problem.result(piece_idx, step)
            next_player     = player if extra_turn else (player + 1) % n
            next_maximizing = False  if extra_turn else not is_maximizing
            val  = minimax(new_state, next_player, depth - 1, alpha, beta, next_maximizing, ai_player)
            best = min(best, val)
            beta = min(beta, val)
            if beta <= alpha: break
        return best

# Find the best action for the AI
def get_best_move(state, player, depth=3):
    n         = len(state)
    problem   = LudoProblem(state, player)
    actions   = problem.actions()
    best_score  = -float('inf')
    best_action = actions[0]
    action_log  = []

    for piece_idx, step in actions:
        new_state, captured, extra_turn = problem.result(piece_idx, step)
        next_player     = player if extra_turn else (player + 1) % n
        next_maximizing = True   if extra_turn else False
        score = minimax(new_state, next_player, depth - 1,
                        -float('inf'), float('inf'), next_maximizing, player)
        
        # Reward for capturing an opponent
        if captured:
            score += 20.0
            
        action_log.append((piece_idx, step, score))
        if score > best_score:
            best_score  = score
            best_action = (piece_idx, step)

    return best_action[0], best_action[1], best_score, action_log

#  Greedy Algorithm 
# ══════════════════════════════════════════════════════
def get_greedy_move(state, player):
    problem = LudoProblem(state, player)
    actions = problem.actions()

    capture_moves = []
    win_moves     = []
    normal_moves  = []

    for piece_idx, step in actions:
        pos = state[player][piece_idx]
        new_state, captured, _ = problem.result(piece_idx, step)

        if captured:
            capture_moves.append((piece_idx, step))
        elif pos + step == END:
            win_moves.append((piece_idx, step))
        else:
            normal_moves.append((piece_idx, step))

    if capture_moves:
        pool = capture_moves
    elif win_moves:
        pool = win_moves
    else:
        pool = normal_moves

    best_pi, best_step = max(pool, key=lambda x: x[1])

    ns, _, _ = problem.result(best_pi, best_step)
    score = evaluate(ns, player)
    return best_pi, best_step, score


# ══════════════════════════════════════════════════════
# GUI - Updated with Step Button, New Game, and Number Buttons
# ══════════════════════════════════════════════════════
class LudoApp:
    def __init__(self, root):
        self.root = root
        root.title("Ludo AI | Strategic Deterministic Environment")
        self.root.configure(bg="#263238") 
        
        self.n              = 3
        self.state          = [[0, 0], [0, 0], [0, 0]]
        self.anim_pos       = [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        self.current_player = 0
        self.game_over      = False
        self.auto_running   = False
        self.is_moving      = False
        self.waiting_human  = False
        self.minimax_depth  = 4
        self.last_best_score = 0

        self._build_ui()
        self._draw_board()

    def _build_ui(self):
        main = tk.Frame(self.root, bg="#263238")
        main.pack(padx=10, pady=10)

        self.canvas = tk.Canvas(main, width=W, height=H,
                                bg="#FFFFFF", highlightthickness=2, highlightbackground="#37474F")
        self.canvas.pack(side=tk.LEFT)

        side = tk.Frame(main, bg="#263238", width=260)
        side.pack(side=tk.LEFT, padx=16, fill=tk.Y)
        side.pack_propagate(False)
        
        #── Turn Label
        self.lbl_turn = tk.Label(
            side, text="🎮 Turn: Minimax (Blue)",
            font=("Cairo", 11, "bold"),
            fg=PLAYER_COLORS[0], bg="#263238", wraplength=220)
        self.lbl_turn.pack(pady=(0, 5))

        # ── AI Stats Panel
        stats_frame = tk.Frame(side, bg="#37474F", padx=5, pady=5)
        stats_frame.pack(fill=tk.X, pady=5)
        self.lbl_score_val = tk.Label(stats_frame, text="Best Score: 0", font=("Courier", 10, "bold"), fg="#81D4FA", bg="#37474F")
        self.lbl_score_val.pack(anchor="w")
        self.lbl_depth_val = tk.Label(stats_frame, text=f"Search Depth: {self.minimax_depth}", font=("Courier", 10), fg="#A5D6A7", bg="#37474F")
        self.lbl_depth_val.pack(anchor="w")

        # ── Human controls (Modified to Buttons)
        self.human_frame = tk.LabelFrame(
            side, text=" 👤 Human Player ",
            font=("Cairo", 10, "bold"), bg="#263238", fg="#4CAF50")
        self.human_frame.pack(fill=tk.X, pady=(5, 8))

        tk.Label(self.human_frame, text="Select Steps:", font=("Cairo", 9), bg="#263238", fg="white").pack(anchor="w")
        
        # أزرار الأرقام بدلاً من السلايدر
        btn_grid = tk.Frame(self.human_frame, bg="#263238")
        btn_grid.pack(pady=5)
        self.step_var = tk.IntVar(value=1)
        self.num_btns = []
        for i in range(1, 11):
            r, c = (i-1)//5, (i-1)%5
            b = tk.Button(btn_grid, text=str(i), width=3, font=("Arial", 8, "bold"),
                          command=lambda v=i: self._select_step(v),
                          bg="#455A64", fg="white", relief="flat")
            b.grid(row=r, column=c, padx=2, pady=2)
            self.num_btns.append(b)
        self._select_step(1) 

        tk.Label(self.human_frame, text="Select Piece:", font=("Cairo", 9), bg="#263238", fg="white").pack(anchor="w")
        self.piece_var = tk.IntVar(value=1)
        pf = tk.Frame(self.human_frame, bg="#263238")
        pf.pack()
        tk.Radiobutton(pf, text="P1", variable=self.piece_var, value=1, bg="#263238", fg="white", selectcolor="#37474F").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(pf, text="P2", variable=self.piece_var, value=2, bg="#263238", fg="white", selectcolor="#37474F").pack(side=tk.LEFT, padx=5)

        self.btn_play = tk.Button(self.human_frame, text="CONFIRM MOVE", command=self._human_play,
                                  bg="#4CAF50", fg="white", font=("Cairo", 10, "bold"), relief="flat", pady=3)
        self.btn_play.pack(fill=tk.X, pady=5)

        # ── AI Thinking Log
        self.think_box = tk.Text(side, height=6, width=24, font=("Courier", 9), bg="#102027", fg="#ECEFF1", relief="flat", state="disabled")
        self.think_box.pack(fill=tk.X, pady=5)
        
        #── Control Buttons (Regained Step and New Game)
        self.btn_step = tk.Button(side, text="⏭ STEP BY STEP", command=self._manual_step,
                                  bg="#FF9800", fg="white", font=("Cairo", 10, "bold"), relief="flat", pady=5)
        self.btn_step.pack(fill=tk.X, pady=2)

        self.btn_auto = tk.Button(side, text="RUN AUTO AI ▶️", command=self._toggle_auto,
                                  bg="#2196F3", fg="white", font=("Cairo", 10, "bold"), relief="flat", pady=5)
        self.btn_auto.pack(fill=tk.X, pady=2)

        tk.Button(side, text="🔄 NEW GAME", command=self._new_game,
                  bg="#546E7A", fg="white", font=("Cairo", 9, "bold"), relief="flat", pady=5).pack(fill=tk.X, pady=2)

        self._enable_human_ui(False)

    def _select_step(self, val):
        self.step_var.set(val)
        for i, btn in enumerate(self.num_btns):
            if i + 1 == val:
                btn.config(bg="#81C784", fg="black") 
            else:
                btn.config(bg="#455A64", fg="white")

    def _cell_color(self, r, c):
        if r < 6 and c < 6:   return BOARD_COLORS["YELLOW"]
        if r < 6 and c > 8:   return BOARD_COLORS["RED"]
        if r > 8 and c < 6:   return BOARD_COLORS["BLUE"]
        if r > 8 and c > 8:   return BOARD_COLORS["GREEN"]
        if c == 7 and 9 <= r <= 13: return BOARD_COLORS["BLUE"]
        if c == 7 and 1 <= r <= 5:  return BOARD_COLORS["RED"]
        if r == 7 and 1 <= c <= 5:  return BOARD_COLORS["YELLOW"]
        if r == 7 and 9 <= c <= 13: return BOARD_COLORS["GREEN"]
        if r == 7 and c == 7: return "#000000"
        if r == 6 and c == 7: return BOARD_COLORS["GOAL_RED"]
        if r == 8 and c == 7: return BOARD_COLORS["GOAL_BLUE"]
        if r == 7 and c == 6: return BOARD_COLORS["GOAL_YELLOW"]
        if r == 7 and c == 8: return BOARD_COLORS["GOAL_GREEN"]
        return TRACK_COLOR

    def _draw_board(self):
        self.canvas.delete("all")
        for r in range(ROWS):
            for c in range(COLS):
                x, y = c * CELL, r * CELL
                self.canvas.create_rectangle(x, y, x+CELL, y+CELL, fill=self._cell_color(r, c), outline=GRID_COLOR)
                if (r, c) in SAFE_SPOTS:
                    self.canvas.create_text(x+CELL//2, y+CELL//2, text="★", fill="#757575", font=("Arial", 12))
        self._draw_pieces()

    def _draw_pieces(self):
        self.canvas.delete("piece")
        offsets = [(-6, -6), (6, 6)]
        for p in range(self.n):
            for pc in range(2):
                pos  = self.anim_pos[p][pc]
                cell = ring_pos_to_cell(p, int(pos))
                if not cell: x, y = HOME_DISPLAY[p][pc]
                else:
                    ox, oy = offsets[pc]
                    x, y = cell[1]*CELL + CELL//2 + ox, cell[0]*CELL + CELL//2 + oy
                self.canvas.create_oval(x-12, y-12, x+12, y+12, fill=PLAYER_COLORS[p], outline="white", width=2, tags="piece")
                self.canvas.create_text(x, y, text=str(pc+1), font=("Arial", 9, "bold"), fill="white", tags="piece")

    def _manual_step(self):
        if self.is_moving or self.game_over or self.waiting_human: return
        self._step()

    def _step(self):
        self.is_moving = True
        p = self.current_player
        if p == 2:
            self.is_moving, self.waiting_human = False, True
            self._enable_human_ui(True)
            self.lbl_turn.config(text="👤 YOUR TURN", fg=PLAYER_COLORS[2])
            return
        if p == 0:
            piece_idx, step, score, action_log = get_best_move(self.state, p, depth=self.minimax_depth)
            self.last_best_score = score
            self._update_think_box(action_log, piece_idx, step, "Minimax")
        else:
            piece_idx, step, score = get_greedy_move(self.state, p)
            self.last_best_score = score
            self._update_think_box([(piece_idx, step, score)], piece_idx, step, "Greedy")
        
        self.lbl_score_val.config(text=f"Best Score: {self.last_best_score:.0f}")
        self._animate(p, piece_idx, self.state[p][piece_idx], self.state[p][piece_idx] + step)

    def _human_play(self):
        if not self.waiting_human: return
        p, piece_idx, step = self.current_player, self.piece_var.get() - 1, self.step_var.get()
        pos = self.state[p][piece_idx]
        if pos + step > END: messagebox.showwarning("Illegal", "Exceeds End!"); return
        self.waiting_human = False
        self._enable_human_ui(False)
        self._animate(p, piece_idx, pos, pos + step)

    def _enable_human_ui(self, on):
        s = "normal" if on else "disabled"
        self.btn_play.config(state=s)
        for b in self.num_btns: b.config(state=s)
        self.btn_step.config(state="disabled" if on else "normal")
        self.btn_auto.config(state="disabled" if on else "normal")

    def _update_think_box(self, action_log, chosen_pi, chosen_step, algo):
        self.think_box.config(state="normal")
        self.think_box.delete("1.0", "end")
        self.think_box.insert("end", f" [ {algo.upper()} ]\n")
        if algo != "Human":
            for pi, step, sc in sorted(action_log, key=lambda x: -x[2])[:5]:
                m = "★" if (pi == chosen_pi and step == chosen_step) else " "
                self.think_box.insert("end", f"{m} P{pi+1} S:{step} Sc:{sc:.0f}\n")
        self.think_box.config(state="disabled")

    def _animate(self, pid, pcid, start, end):
        if start < end:
            start += 1
            self.state[pid][pcid] = start
            self.anim_pos[pid][pcid] = float(start)
            self._draw_board()
            self.root.after(120, lambda: self._animate(pid, pcid, start, end))
        else: self._check_capture(pid, end)

    def _check_capture(self, p, pos):
        captured = False
        if pos < 52:
            cell = ring_pos_to_cell(p, pos)
            for opp in range(self.n):
                if opp == p: continue
                for i in range(2):
                    if 0 < self.state[opp][i] < 52 and ring_pos_to_cell(opp, self.state[opp][i]) == cell:
                        if cell not in SAFE_SPOTS:
                            self.state[opp][i] = self.anim_pos[opp][i] = 0.0
                            captured = True
        if captured: self._draw_board(); self.root.after(800, lambda: self._give_extra_turn(p))
        else: self._finalize()

    def _give_extra_turn(self, p):
        self.is_moving, self.current_player = False, p
        self.lbl_turn.config(text=f"🔥 EXTRA: {PLAYER_NAMES[p]}", fg=PLAYER_COLORS[p])
        if p == 2: self.waiting_human = True; self._enable_human_ui(True)
        elif self.auto_running: self.root.after(500, self._step)

    def _finalize(self):
        for p in range(self.n):
            if all(x >= END for x in self.state[p]):
                messagebox.showinfo("Winner", f"🏆 {PLAYER_NAMES[p]} WON!"); self._new_game(); return
        self.current_player = (self.current_player + 1) % self.n
        self.lbl_turn.config(text=f"Turn: {PLAYER_NAMES[self.current_player]}", fg=PLAYER_COLORS[self.current_player])
        self.is_moving = False
        if self.current_player == 2: self.waiting_human = True; self._enable_human_ui(True)
        elif self.auto_running: self.root.after(500, self._step)

    def _toggle_auto(self):
        if self.waiting_human and not self.auto_running: return
        self.auto_running = not self.auto_running
        self.btn_auto.config(text="STOP AI ⏹" if self.auto_running else "RUN AUTO AI ▶️", bg="#F44336" if self.auto_running else "#2196F3")
        if self.auto_running: self._step()

    def _new_game(self):
        self.state, self.anim_pos = [[0, 0], [0, 0], [0, 0]], [[0.0, 0.0], [0.0, 0.0], [0.0, 0.0]]
        self.current_player, self.game_over, self.auto_running, self.is_moving, self.waiting_human = 0, False, False, False, False
        self._enable_human_ui(False); self.lbl_score_val.config(text="Best Score: 0"); self._draw_board()
        self.lbl_turn.config(text=f"Turn: {PLAYER_NAMES[self.current_player]}", fg=PLAYER_COLORS[self.current_player])      


# ══════════════════════════════════════════════════════
if __name__ == "__main__":

    root = tk.Tk()

    app  = LudoApp(root)

    root.mainloop()