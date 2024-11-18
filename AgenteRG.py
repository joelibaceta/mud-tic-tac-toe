import pygame
import copy
from IDA import IDAStarStrategic

# Inicializar Pygame
pygame.init()

class Board:
    # Dimensiones del tablero
    GRID_SIZE = 100  # Tamaño de cada celda
    ROWS, COLS = 7, 3  # Número de filas y columnas
    WIDTH, HEIGHT = COLS * GRID_SIZE, ROWS * GRID_SIZE  # Ajuste dinámico al tamaño del tablero
    WHITE = (255, 255, 255)
    BLACK = (0, 0, 0)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    GRAY = (200, 200, 200)

    # Representación del tablero
    EMPTY = 1  # Casilla vacía
    GREEN_PLAYER = 2  # Verde (jugador humano)
    RED_PLAYER = 3  # Rojo (agente)

    # Tablero inicial directamente con números
    INITIAL_BOARD = [
        [2, 2, 2],  # Fichas verdes (jugador humano)
        [0, 1, 0],  # Obstáculos y celdas vacías
        [1, 1, 0],
        [0, 1, 0],
        [0, 1, 1],
        [0, 1, 0],
        [3, 3, 3],  # Fichas rojas (agente)
    ]

    def __init__(self):
        self.board = copy.deepcopy(self.INITIAL_BOARD)
        self.selected_piece = None  # Guarda la pieza seleccionada por el usuario

    def draw(self, screen):
        for row in range(self.ROWS):
            for col in range(self.COLS):
                x = col * self.GRID_SIZE
                y = row * self.GRID_SIZE
                if self.board[row][col] == self.GREEN_PLAYER:
                    pygame.draw.circle(screen, self.GREEN, (x + self.GRID_SIZE // 2, y + self.GRID_SIZE // 2), 30)
                elif self.board[row][col] == self.RED_PLAYER:
                    pygame.draw.circle(screen, self.RED, (x + self.GRID_SIZE // 2, y + self.GRID_SIZE // 2), 30)
                elif self.board[row][col] == self.EMPTY:
                    pygame.draw.rect(screen, self.WHITE, (x, y, self.GRID_SIZE, self.GRID_SIZE))
                else:
                    pygame.draw.rect(screen, self.BLACK, (x, y, self.GRID_SIZE, self.GRID_SIZE))

                # Dibujar borde para la pieza seleccionada
                if self.selected_piece == (row, col):
                    pygame.draw.rect(screen, self.GRAY, (x, y, self.GRID_SIZE, self.GRID_SIZE), 3)

    def is_valid_move(self, player, row, col, target_row, target_col):
        """
        Valida si un movimiento es posible para una ficha dada.
        """
        if 0 <= target_row < self.ROWS and 0 <= target_col < self.COLS:
            if self.board[target_row][target_col] == self.EMPTY:
                if abs(row - target_row) + abs(col - target_col) == 1:
                    return True
        return False

    def move_piece(self, row, col, target_row, target_col):
        """
        Realiza un movimiento válido en el tablero.
        """
        if self.is_valid_move(self.board[row][col], row, col, target_row, target_col):
            self.board[target_row][target_col] = self.board[row][col]
            self.board[row][col] = self.EMPTY
            return True
        return False

    def check_game_state(self, player_turn, agent):
        """
        Verifica si el juego ha terminado o está bloqueado.
        """
        if all(self.board[self.ROWS - 1][col] == self.GREEN_PLAYER for col in range(self.COLS)):
            return "Jugador Gana"
        if all(self.board[0][col] == self.RED_PLAYER for col in range(self.COLS)):
            return "Agente Gana"
        player = self.GREEN_PLAYER if player_turn else self.RED_PLAYER
        is_blocked = not any(
            agent.algorithm.get_valid_moves(self.board, row, col, self.EMPTY)
            for row in range(self.ROWS)
            for col in range(self.COLS)
            if self.board[row][col] == player
        )
        if is_blocked:
            return f"Empate ({'Jugador' if player_turn else 'Agente'} bloqueado)"
        return "En Progreso"

class Agent:
    def __init__(self, algorithm):
        self.algorithm = algorithm

    def move(self, board):
        """
        Ejecuta el algoritmo y realiza el movimiento en el tablero.
        """
        best_move = self.algorithm.execute(
            board=board.board,
            rows=board.ROWS,
            cols=board.COLS,
            empty=board.EMPTY,
            agent_piece=board.RED_PLAYER,
            goal_row=0
        )
        if best_move:
            (row, col), (target_row, target_col) = best_move
            board.move_piece(row, col, target_row, target_col)
            print(f"Agente movido de ({row}, {col}) a ({target_row}, {target_col})")
        else:
            print("Movimiento forzado para el agente.")

# Configuración del juego
board = Board()
agent = Agent(IDAStarStrategic())
screen = pygame.display.set_mode((board.WIDTH, board.HEIGHT))
pygame.display.set_caption("Juego Verde vs Rojo")

running = True
player_turn = True

def show_end_screen(message):
    screen.fill(board.BLACK)
    font = pygame.font.Font(None, 30)  # Ajustar el tamaño de la fuente según sea necesario

    # Dividir el mensaje en líneas si es demasiado largo
    words = message.split()
    lines = []
    current_line = ""
    max_width = board.WIDTH - 20  # Dejar un margen de 10 píxeles en cada lado

    for word in words:
        test_line = f"{current_line} {word}".strip()
        text_width, _ = font.size(test_line)
        if text_width <= max_width:
            current_line = test_line
        else:
            lines.append(current_line)
            current_line = word

    if current_line:
        lines.append(current_line)

    # Calcular la posición para centrar las líneas en la pantalla
    total_height = len(lines) * font.get_linesize()
    start_y = (board.HEIGHT - total_height) // 2

    for i, line in enumerate(lines):
        text = font.render(line, True, board.WHITE)
        text_rect = text.get_rect(center=(board.WIDTH // 2, start_y + i * font.get_linesize()))
        screen.blit(text, text_rect)

    pygame.display.flip()
    pygame.time.wait(2000)

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if player_turn and event.type == pygame.MOUSEBUTTONDOWN:
            game_state = board.check_game_state(player_turn, agent)
            if game_state != "En Progreso":
                show_end_screen(f"Fin del juego: {game_state}")
                running = False
                break
            x, y = event.pos
            row, col = y // board.GRID_SIZE, x // board.GRID_SIZE
            if board.selected_piece:
                if board.move_piece(*board.selected_piece, row, col):
                    player_turn = False
                board.selected_piece = None
            elif board.board[row][col] == board.GREEN_PLAYER:
                board.selected_piece = (row, col)

    if not player_turn and running:
        game_state = board.check_game_state(player_turn, agent)
        if game_state != "En Progreso":
            show_end_screen(f"Fin del juego: {game_state}")
            running = False
            break
        agent.move(board)
        player_turn = True

    if running:
        screen.fill(board.WHITE)
        board.draw(screen)
        pygame.display.flip()

pygame.quit()