import heapq
import random

class AStarSearch:
    def __init__(self):
        self.visited_states = set()

    def execute(self, board, rows, cols, empty, piece, goal_row):
        """
        Ejecuta el algoritmo A* para determinar el mejor movimiento inmediato,
        evaluando varios pasos hacia adelante.
        """
        start_state = tuple(tuple(row) for row in board)
        priority_queue = []
        self.visited_states.clear()

        # Inicializar la cola de prioridad con el estado inicial
        heapq.heappush(priority_queue, (0, start_state, [], None))  # (f_score, state, path, root_move)
        best_move = None
        best_score = float('-inf')

        while priority_queue:
            f_score, current_state, path, root_move = heapq.heappop(priority_queue)
            current_board = [list(row) for row in current_state]

            # Evitar ciclos
            if current_state in self.visited_states:
                continue
            self.visited_states.add(current_state)

            # Generar movimientos válidos
            for row in range(rows):
                for col in range(cols):
                    if current_board[row][col] == piece:
                        valid_moves = self.get_valid_moves(current_board, row, col, empty)
                        for nr, nc in valid_moves:
                            move = ((row, col), (nr, nc))
                            new_board = self.apply_virtual_move(current_board, move[0], move[1], piece, empty)
                            new_state = tuple(tuple(r) for r in new_board)
                            new_path = path + [move]

                            # El movimiento raíz es el primer movimiento del camino
                            next_root_move = root_move if root_move else move

                            # Calcular la heurística
                            h_score = self.heuristic(new_board, move, goal_row, rows, cols, empty, piece)
                            f_score = len(new_path) + h_score
                            heapq.heappush(priority_queue, (f_score, new_state, new_path, next_root_move))

                            # Registrar el mejor movimiento raíz
                            if h_score > best_score:
                                best_score = h_score
                                best_move = next_root_move

        # Si no se encuentra un camino óptimo, fuerza el movimiento aleatorio
        if best_move:
            print(f"Agente movido de {best_move[0]} a {best_move[1]}")
            return best_move
        else:
            print("Movimiento forzado para el agente.")
            return self.force_random_move(board, rows, cols, empty, piece)

    def get_valid_moves(self, board, row, col, empty):
        """
        Obtiene movimientos válidos para una pieza.
        """
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        moves = []
        for dr, dc in directions:
            nr, nc = row + dr, col + dc
            # Validar límites y celdas vacías
            if 0 <= nr < len(board) and 0 <= nc < len(board[0]) and board[nr][nc] == empty:
                moves.append((nr, nc))
        return moves

    def apply_virtual_move(self, board, move_from, move_to, piece, empty):
        """
        Aplica un movimiento virtual y devuelve un nuevo estado del tablero.
        """
        fr, fc = move_from
        tr, tc = move_to

        # Crear una copia completamente nueva del tablero
        new_board = [row[:] for row in board]

        # Validar que el destino es vacío antes de mover
        if new_board[tr][tc] == empty:
            new_board[tr][tc] = piece
            new_board[fr][fc] = empty

        return new_board

    def heuristic(self, board, move, goal_row, rows, cols, empty, piece):
        """
        Calcula la heurística para evaluar un movimiento.
        """
        (_, _), (target_row, target_col) = move
        score = 0

        # Premiar movimientos hacia el objetivo
        progress = abs(target_row - goal_row)
        score -= progress * 10

        # Premiar desbloquear caminos estratégicos
        unblock_score = self.unblock_paths(board, rows, cols, empty, piece)
        score += unblock_score * 30

        # Evaluar el progreso global de todas las fichas hacia la fila objetivo
        global_progress = self.global_progress(board, goal_row, rows, cols, piece)
        score += global_progress * 15

        # Penalizar si el movimiento genera bloqueos propios
        if self.blocks_others(board, move, piece, rows, cols, empty):
            score -= 50

        return score

    def global_progress(self, board, goal_row, rows, cols, piece):
        """Evalúa el progreso global de todas las fichas hacia la fila objetivo."""
        total_progress = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == piece:
                    total_progress += abs(goal_row - row)
        return -total_progress  # Valor negativo porque queremos minimizar la distancia

    def unblock_paths(self, board, rows, cols, empty, piece):
        """
        Evalúa si un movimiento desbloquea caminos para otras fichas.
        """
        score = 0
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == piece:
                    valid_moves = self.get_valid_moves(board, row, col, empty)
                    score += len(valid_moves)  # Más movimientos disponibles significa más desbloqueo
        return score

    def blocks_others(self, board, move, piece, rows, cols, empty):
        """
        Evalúa si un movimiento bloquea a otras fichas del mismo jugador.
        """
        (_, _), (target_row, target_col) = move
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dr, dc in directions:
            nr, nc = target_row + dr, target_col + dc
            if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == piece:
                # Si hay otra ficha del mismo jugador en una posición bloqueada
                if not self.get_valid_moves(board, nr, nc, empty):
                    return True
        return False

    def force_random_move(self, board, rows, cols, empty, piece):
        """Fuerza un movimiento aleatorio considerando todas las fichas."""
        all_possible_moves = []
        for row in range(rows):
            for col in range(cols):
                if board[row][col] == piece:
                    valid_moves = self.get_valid_moves(board, row, col, empty)
                    for move in valid_moves:
                        all_possible_moves.append(((row, col), move))
        if all_possible_moves:
            return random.choice(all_possible_moves)
        return None