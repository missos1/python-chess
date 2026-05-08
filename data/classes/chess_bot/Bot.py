import sys
import time
from .GameState import *
from .constants import *
from .evaluate import *
from .search import negamax, TimeOutException

class Bot:
    def __init__(self, color=WHITE, time_limit=6, verbose=False):
        self.color = color
        self.time_limit = time_limit
        self.verbose = verbose
        self.nodes_searched = 0
        self.start_time = 0
        
        # TT stores {hash: (depth, score, flag, best_move)}
        # flag: TT_EXACT, TT_UPPER_BOUND, or TT_LOWER_BOUND
        self.transposition_table = {}
        # killer moves [ply][0/1]
        self.killer_moves = [[None, None] for _ in range(64)]

    def _log(self, *parts):
        if self.verbose:
            print(*parts, file=sys.stderr)

    def get_best_move(self, state, max_depth=None, stop_event=None) -> tuple[int, int, int] | None:
        self.nodes_searched = 0
        self.start_time = time.time()
        self._log(f"Transposition table size at start of search: {len(self.transposition_table)} entries.")
        if len(self.transposition_table) > 4000000:
            self.transposition_table.clear()
        
        best_move = None
        
        legal_moves = state.get_strictly_legal_moves(self.color)
        if not legal_moves:
            return None
            
        legal_moves.sort(key=lambda m: score_move(m, state), reverse=True)
        
        null_prune_times = 0
        null_prune_scores = []
        # search_params = [nodes_searched, start_time, time_limit]
        search_params = [0, self.start_time, self.time_limit, null_prune_times]
        tt = self.transposition_table
        current_depth = 0
        
        # Iterative Deepening loop
        for current_depth in range(1, 1001):
            if max_depth is not None and current_depth > max_depth:
                break
            if stop_event is not None and stop_event.is_set():
                raise TimeOutException()

            try:
                alpha = -INFINITY
                beta = INFINITY
                depth_best_move = None
                
                # Bring the best move from the previous depth to the front to maximize Alpha-Beta snips
                if best_move and best_move in legal_moves:
                    legal_moves.remove(best_move)
                    legal_moves.insert(0, best_move)
                
                for move in legal_moves:
                    if stop_event is not None and stop_event.is_set():
                        raise TimeOutException()

                    state.make_move(move)
                    enemy_color = BLACK if self.color == WHITE else WHITE
                    score = -negamax(current_depth - 1, state, -beta, -alpha, enemy_color, search_params, tt, self.killer_moves, 1, stop_event)
                    state.undo_move(move)
                    
                    if score > alpha:
                        alpha = score
                        depth_best_move = move
                        
                if depth_best_move:
                    best_move = depth_best_move
                    
                # This isn't used because search uses pseudo-legal move generation, 
                # but it can be helpful for debugging to see if the search is correctly identifying checkmates
                # If we've found a guaranteed, forced checkmate against the opponent, stop searching immediately!
                # if alpha > 90000:
                #     print(f"--> Found a forced Checkmate! Ending search early at depth {current_depth}.")
                #     break
                    
            except TimeOutException:
                self._log(f"--> Aborting search! Max time limit ({self.time_limit}s) reached during depth {current_depth}.")
                break
                
        self.nodes_searched = search_params[0]

        if self.verbose:
            if best_move is not None:
                source = best_move[0]
                target = best_move[1]

            self._log(f"Bot searched {self.nodes_searched} nodes.")
            self._log(f"Null prunes attempted: {search_params[3]}")
            self._log(f"depth reached: {current_depth}")
            self._log(
                f"Best move: {index_to_algebraic(source) if best_move else 'None'} "
                f"to {index_to_algebraic(target) if best_move else 'None'}."
            )
        
        return best_move
    
def index_to_algebraic(index):
    # get the file (a-h)
    file_char = chr((index % 8) + ord('a'))
    # get the rank (1-8)
    rank_char = str((index // 8) + 1)
    return file_char + rank_char