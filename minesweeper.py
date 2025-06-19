import pygame
import sys
import random

# Constants (can be grouped later for difficulty settings)
GRID_ROWS_DEFAULT = 10
GRID_COLS_DEFAULT = 10
NUM_MINES_DEFAULT = 10

CELL_SIZE = 30
UI_AREA_HEIGHT = 60

# Dynamic calculation of screen dimensions will be based on current grid settings
GAME_SCREEN_WIDTH = GRID_COLS_DEFAULT * CELL_SIZE
GAME_SCREEN_HEIGHT = GRID_ROWS_DEFAULT * CELL_SIZE
TOTAL_SCREEN_WIDTH = GAME_SCREEN_WIDTH
TOTAL_SCREEN_HEIGHT = GAME_SCREEN_HEIGHT + UI_AREA_HEIGHT

# Colors (remain the same)
BLACK = (0, 0, 0); WHITE = (255, 255, 255); GRAY_HIDDEN = (200, 200, 200)
GRAY_REVEALED_EMPTY = (160, 160, 160); BORDER_COLOR = (100, 100, 100)
TEXT_COLOR = BLACK; UI_TEXT_COLOR = WHITE; MINE_COLOR = (255, 0, 0)
FLAG_COLOR = (0, 0, 255); UI_BG_COLOR = (60, 60, 60)

EMPTY_CELL = 0; MINE_CELL = -1
CELL_HIDDEN = 0; CELL_REVEALED = 1; CELL_FLAGGED = 2
STATE_PLAYING = 0; STATE_GAME_OVER_LOSE = 1; STATE_GAME_OVER_WIN = 2

CELL_FONT = None
UI_FONT = None
UI_FONT_SMALL = None
UI_FONT_TINY = None  # Added tiny font for game over message

# --- Game State Variables --- (will be managed by a function or class later)
# These will be part of what reset_game_state handles
current_grid_rows = GRID_ROWS_DEFAULT
current_grid_cols = GRID_COLS_DEFAULT
current_num_mines = NUM_MINES_DEFAULT

mine_board = None
player_board = None
flags_placed = 0
game_state = STATE_PLAYING
is_first_click = True
start_time = 0
elapsed_time = 0


def update_screen_dimensions():
    global GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT, TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT, screen
    GAME_SCREEN_WIDTH = current_grid_cols * CELL_SIZE
    GAME_SCREEN_HEIGHT = current_grid_rows * CELL_SIZE
    TOTAL_SCREEN_WIDTH = GAME_SCREEN_WIDTH
    TOTAL_SCREEN_HEIGHT = GAME_SCREEN_HEIGHT + UI_AREA_HEIGHT
    # Re-create screen if dimensions change (important for difficulty changes)
    # screen = pygame.display.set_mode((TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT))


# (Board utility functions: create_empty_board, place_mines, calculate_adjacent_mines - remain largely the same)
# Minor adjustment to place_mines for clarity on safe_cells
def create_empty_board(rows, cols, default_value=0):
    return [[default_value for _ in range(cols)] for _ in range(rows)]

def place_mines(board, num_mines, first_click_coords=None):
    rows, cols = len(board), len(board[0])
    if num_mines >= rows * cols: num_mines = max(0, rows * cols -1)

    safe_zone = []
    if first_click_coords:
        for r_offset in range(-1, 2): # 3x3 area around first click
            for c_offset in range(-1, 2):
                safe_r, safe_c = first_click_coords[0] + r_offset, first_click_coords[1] + c_offset
                if 0 <= safe_r < rows and 0 <= safe_c < cols:
                    safe_zone.append((safe_r, safe_c))

    mines_placed_count = 0
    attempts = 0
    max_attempts = rows * cols * 5 # Safety break for dense minefields / small boards

    while mines_placed_count < num_mines and attempts < max_attempts:
        r, c = random.randint(0, rows - 1), random.randint(0, cols - 1)
        if (r,c) in safe_zone:
            attempts +=1
            continue
        if board[r][c] != MINE_CELL:
            board[r][c] = MINE_CELL
            mines_placed_count += 1
        attempts +=1

    # If not all mines placed (e.g. very dense board, small area after safe zone)
    # try to fill remaining mines in non-safe cells
    if mines_placed_count < num_mines:
        for r in range(rows):
            for c in range(cols):
                if mines_placed_count == num_mines: break
                if board[r][c] != MINE_CELL and (r,c) not in safe_zone:
                    board[r][c] = MINE_CELL
                    mines_placed_count +=1
            if mines_placed_count == num_mines: break


def calculate_adjacent_mines(board):
    rows, cols = len(board), len(board[0])
    for r in range(rows):
        for c in range(cols):
            if board[r][c] == MINE_CELL: continue
            mine_count = 0
            for i in range(-1, 2):
                for j in range(-1, 2):
                    if i == 0 and j == 0: continue
                    nr, nc = r + i, c + j
                    if 0 <= nr < rows and 0 <= nc < cols and board[nr][nc] == MINE_CELL:
                        mine_count += 1
            board[r][c] = mine_count

def count_adjacent_mines(grid, row, col):
    # Count mines in all 8 adjacent cells
    count = 0
    
    # Check all 8 surrounding positions
    for i in range(max(0, row-1), min(len(grid), row+2)):
        for j in range(max(0, col-1), min(len(grid[0]), col+2)):
            # Skip the cell itself
            if (i == row and j == col):
                continue
            # If neighbor has a mine, increment count
            if grid[i][j].is_mine:
                count += 1
    
    return count

# Find where the grid is initialized and mine counts are assigned
# Replace or fix the current counting logic with:
def update_mine_counts(grid):
    rows, cols = len(grid), len(grid[0])
    for i in range(rows):
        for j in range(cols):
            # Skip mine cells
            if not grid[i][j].is_mine:
                # Count adjacent mines
                grid[i][j].adjacent_mines = count_adjacent_mines(grid, i, j)

def initialize_game_boards_for_state(rows, cols, num_m, first_click_coords=None): # Renamed
    global mine_board, player_board # Modify global boards
    mine_board = create_empty_board(rows, cols)
    place_mines(mine_board, num_m, first_click_coords)
    calculate_adjacent_mines(mine_board)
    player_board = create_empty_board(rows, cols, CELL_HIDDEN)


# (reveal_cell, toggle_flag, check_win_condition - remain the same)
def reveal_cell(p_board, m_board, r, c, current_state): # aliased params
    if not (0 <= r < current_grid_rows and 0 <= c < current_grid_cols): return current_state
    if p_board[r][c] == CELL_REVEALED or p_board[r][c] == CELL_FLAGGED: return current_state
    p_board[r][c] = CELL_REVEALED
    if m_board[r][c] == MINE_CELL: return STATE_GAME_OVER_LOSE
    if m_board[r][c] == EMPTY_CELL:
        for i in range(-1, 2):
            for j in range(-1, 2):
                if i == 0 and j == 0: continue
                nr, nc = r + i, c + j
                if 0 <= nr < current_grid_rows and 0 <= nc < current_grid_cols and p_board[nr][nc] == CELL_HIDDEN:
                    reveal_cell(p_board, m_board, nr, nc, current_state) # Pass current_state
    return current_state # Return original state if no mine hit, game continues

def toggle_flag(p_board, r, c):
    if not (0 <= r < current_grid_rows and 0 <= c < current_grid_cols) or p_board[r][c] == CELL_REVEALED: return 0
    if p_board[r][c] == CELL_HIDDEN:
        p_board[r][c] = CELL_FLAGGED; return 1
    elif p_board[r][c] == CELL_FLAGGED:
        p_board[r][c] = CELL_HIDDEN; return -1
    return 0

def check_win_condition(p_board, m_board):
    for r in range(current_grid_rows):
        for c in range(current_grid_cols):
            if m_board[r][c] != MINE_CELL and p_board[r][c] != CELL_REVEALED: return False
    return True

def draw_board(surface, m_board_ref, p_board_ref): # Changed screen to surface
    global CELL_FONT
    surface.fill(GRAY_HIDDEN) # Fill game area background
    for r in range(current_grid_rows):
        for c in range(current_grid_cols):
            rect = pygame.Rect(c * CELL_SIZE, r * CELL_SIZE, CELL_SIZE, CELL_SIZE)
            cell_player_state = p_board_ref[r][c]
            value_in_mine_board = m_board_ref[r][c]

            # Determine background color based on state
            bg_color = GRAY_HIDDEN
            if cell_player_state == CELL_REVEALED:
                bg_color = GRAY_REVEALED_EMPTY
            pygame.draw.rect(surface, bg_color, rect)

            # Draw content
            if cell_player_state == CELL_REVEALED:
                if value_in_mine_board == MINE_CELL:
                    pygame.draw.rect(surface, MINE_COLOR, rect)
                elif value_in_mine_board > 0:
                    text_surface = CELL_FONT.render(str(value_in_mine_board), True, TEXT_COLOR)
                    text_rect = text_surface.get_rect(center=rect.center)
                    surface.blit(text_surface, text_rect)
            elif cell_player_state == CELL_FLAGGED:
                pygame.draw.circle(surface, FLAG_COLOR, rect.center, CELL_SIZE // 4)

            pygame.draw.rect(surface, BORDER_COLOR, rect, 1)


def get_cell_from_mouse_pos(mouse_pos):
    mouse_x, mouse_y = mouse_pos
    if mouse_y >= GAME_SCREEN_HEIGHT: return None
    row = mouse_y // CELL_SIZE
    col = mouse_x // CELL_SIZE
    if 0 <= row < current_grid_rows and 0 <= col < current_grid_cols: return row, col
    return None

def draw_ui_elements(surface, current_elapsed_time, mines_rem): # Changed screen to surface
    global UI_FONT
    ui_rect = pygame.Rect(0, GAME_SCREEN_HEIGHT, TOTAL_SCREEN_WIDTH, UI_AREA_HEIGHT)
    pygame.draw.rect(surface, UI_BG_COLOR, ui_rect)
    timer_text = UI_FONT.render(f"Time: {current_elapsed_time} sec", True, UI_TEXT_COLOR)
    timer_text_rect = timer_text.get_rect(midleft=(10, GAME_SCREEN_HEIGHT +2+ UI_AREA_HEIGHT // 2))
    surface.blit(timer_text, timer_text_rect)
    mine_text = UI_FONT.render(f"Mines: {mines_rem}", True, UI_TEXT_COLOR)
    mine_text_rect = mine_text.get_rect(midright=(TOTAL_SCREEN_WIDTH - 10, GAME_SCREEN_HEIGHT + UI_AREA_HEIGHT // 2))
    surface.blit(mine_text, mine_text_rect)

# --- Global screen variable ---
screen = None

def reset_game_state(rows=GRID_ROWS_DEFAULT, cols=GRID_COLS_DEFAULT, num_m=NUM_MINES_DEFAULT):
    global mine_board, player_board, flags_placed, game_state, is_first_click, start_time, elapsed_time
    global current_grid_rows, current_grid_cols, current_num_mines, screen

    current_grid_rows = rows
    current_grid_cols = cols
    current_num_mines = num_m

    update_screen_dimensions() # Update global screen dimension vars
    # Important: If screen dimensions change, Pygame window might need re-creation
    # For simplicity now, we assume it's handled if update_screen_dimensions re-sets 'screen'
    # However, screen re-initialization is better done once in main or if settings actually change.
    # The current update_screen_dimensions does not re-init screen, so window size is fixed after start.

    initialize_game_boards_for_state(current_grid_rows, current_grid_cols, current_num_mines) # Uses global boards

    flags_placed = 0
    game_state = STATE_PLAYING
    is_first_click = True
    start_time = 0
    elapsed_time = 0
    print(f"Game reset to: {rows}x{cols} grid, {num_m} mines.")


def main():
    global CELL_FONT, UI_FONT, UI_FONT_SMALL, UI_FONT_TINY, screen # Make screen global
    global mine_board, player_board, flags_placed, game_state, is_first_click, start_time, elapsed_time
    global current_grid_rows, current_grid_cols, current_num_mines


    pygame.init()
    CELL_FONT = pygame.font.SysFont("arial", CELL_SIZE // 2)
    UI_FONT = pygame.font.SysFont("arial", UI_AREA_HEIGHT // 3)
    UI_FONT_SMALL = pygame.font.SysFont('comicsans', 24)  # Create a smaller font (adjust size as needed)
    UI_FONT_TINY = pygame.font.SysFont('comicsans', 14)  # Create a very small font for the game over message

    # Initial game setup uses default values
    reset_game_state() # Initial setup

    # Initialize screen after setting initial dimensions via reset_game_state
    screen = pygame.display.set_mode((TOTAL_SCREEN_WIDTH, TOTAL_SCREEN_HEIGHT))
    pygame.display.set_caption("Minesweeper")

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: running = False

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    reset_game_state() # Reset with default settings
                    # Example for changing difficulty (conceptual):
                    # reset_game_state(rows=16, cols=16, num_m=40)
                    # This would require screen re-initialization if size changes.
                    # For now, K_r resets to default.

            if event.type == pygame.MOUSEBUTTONDOWN and game_state == STATE_PLAYING:
                mouse_pos = event.pos
                clicked_cell = get_cell_from_mouse_pos(mouse_pos)

                if clicked_cell:
                    row, col = clicked_cell

                    if is_first_click and event.button == 1:
                        start_time = pygame.time.get_ticks()
                        # First click safety: regenerate if mine is at (row,col) or immediate neighbors
                        while mine_board[row][col] == MINE_CELL or \
                              any(mine_board[nr][nc] == MINE_CELL for dr in range(-1,2) for dc in range(-1,2) \
                                  if 0 <= (nr:=row+dr) < current_grid_rows and 0 <= (nc:=col+dc) < current_grid_cols): # and (dr!=0 or dc!=0) removed to include center
                            print(f"First click ({row},{col}) or neighbor was mine. Regenerating...")
                            initialize_game_boards_for_state(current_grid_rows, current_grid_cols, current_num_mines, first_click_coords=(row,col))
                        is_first_click = False
                        # Auto-reveal first clicked cell after safety check
                        game_state = reveal_cell(player_board, mine_board, row, col, game_state)


                    elif not is_first_click and event.button == 1: # Normal Left click
                        game_state = reveal_cell(player_board, mine_board, row, col, game_state)

                    elif not is_first_click and event.button == 3: # Right click
                        flag_change = toggle_flag(player_board, row, col)
                        flags_placed += flag_change

                    # Check win/loss after any click that could change state
                    if game_state == STATE_PLAYING and check_win_condition(player_board, mine_board):
                        game_state = STATE_GAME_OVER_WIN
                    elif game_state == STATE_GAME_OVER_LOSE:
                        for r_idx in range(current_grid_rows):
                            for c_idx in range(current_grid_cols):
                                if mine_board[r_idx][c_idx] == MINE_CELL:
                                    player_board[r_idx][c_idx] = CELL_REVEALED

        if game_state == STATE_PLAYING and not is_first_click:
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000
        elif game_state != STATE_PLAYING and not is_first_click and start_time != 0:
            elapsed_time = (pygame.time.get_ticks() - start_time) // 1000


        screen.fill(UI_BG_COLOR)
        game_area_surface = screen.subsurface(pygame.Rect(0, 0, GAME_SCREEN_WIDTH, GAME_SCREEN_HEIGHT))
        # game_area_surface.fill(GRAY_HIDDEN) # draw_board fills its own background now

        if mine_board and player_board: # Ensure boards are initialized
            draw_board(game_area_surface, mine_board, player_board)

        mines_remaining = current_num_mines - flags_placed
        draw_ui_elements(screen, elapsed_time, mines_remaining)

        if game_state == STATE_GAME_OVER_LOSE:
            
            lose_text = UI_FONT_TINY.render("GAME OVER - YOU LOSE! (R to Restart)", True, MINE_COLOR)
            # Adjust only the Y-coordinate in the blit call to position it lower
            screen.blit(lose_text, (TOTAL_SCREEN_WIDTH//2 - lose_text.get_width()//2, GAME_SCREEN_HEIGHT - 0.05))

        elif game_state == STATE_GAME_OVER_WIN:
            win_text = UI_FONT_TINY.render("CONGRATULATIONS - YOU WIN! (R to Restart)", True, FLAG_COLOR)
            text_rect = win_text.get_rect(center=(TOTAL_SCREEN_WIDTH // 2, GAME_SCREEN_HEIGHT + UI_AREA_HEIGHT // 2))
            screen.blit(win_text, (TOTAL_SCREEN_WIDTH//2 - win_text.get_width()//2, GAME_SCREEN_HEIGHT - 0.05))

        pygame.display.flip()
        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == '__main__':
    main()
