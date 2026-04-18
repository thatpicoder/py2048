import random
import sys

GRID_SIZE = 4
TARGET = 2048

try:
    import msvcrt

    def get_key():
        while True:
            key = msvcrt.getch()
            if key in b"\x00\xe0":
                msvcrt.getch()
                continue
            try:
                return key.decode("utf-8", errors="ignore")
            except Exception:
                continue
except ImportError:
    import termios
    import tty

    def get_key():
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            char = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return char


def new_grid():
    grid = [[0] * GRID_SIZE for _ in range(GRID_SIZE)]
    add_random_tile(grid)
    add_random_tile(grid)
    return grid


def add_random_tile(grid):
    empty = [(r, c) for r in range(GRID_SIZE) for c in range(GRID_SIZE) if grid[r][c] == 0]
    if not empty:
        return False
    r, c = random.choice(empty)
    grid[r][c] = 4 if random.random() < 0.1 else 2
    return True


def enable_ansi():
    if sys.platform.startswith("win"):
        try:
            import ctypes

            kernel32 = ctypes.windll.kernel32
            handle = kernel32.GetStdHandle(-11)
            mode = ctypes.c_uint()
            if kernel32.GetConsoleMode(handle, ctypes.byref(mode)):
                kernel32.SetConsoleMode(handle, mode.value | 0x0004)
        except Exception:
            pass


def clear_screen():
    sys.stdout.write("\033[2J\033[H")
    sys.stdout.flush()


def move_cursor(row, col):
    sys.stdout.write(f"\033[{row};{col}H")
    sys.stdout.flush()


def write(text):
    sys.stdout.write(text)
    sys.stdout.flush()


def format_cell(value):
    return f" {value or '.':4} |"


def print_grid(grid):
    line = "+" + "------+" * GRID_SIZE
    print(line)
    for row in grid:
        print("|" + "".join(format_cell(cell) for cell in row))
        print(line)


def draw_initial(grid, score):
    enable_ansi()
    clear_screen()
    write("2048, made by bitetheapple\n")
    write(f"target: {TARGET}\n")
    write(f"score: {score}\033[K\n")
    write(f"highest number: {max(cell for row in grid for cell in row)}\033[K\n")
    print_grid(grid)


def update_score(score, highest):
    move_cursor(3, 1)
    write(f"score: {score}\033[K")
    move_cursor(4, 1)
    write(f"highest number: {highest}\033[K")


def update_grid(old_grid, new_grid):
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE):
            if old_grid[r][c] != new_grid[r][c]:
                move_cursor(6 + r * 2, 2 + c * 6)
                write(format_cell(new_grid[r][c]))


def transpose(grid):
    return [list(row) for row in zip(*grid)]


def reverse(grid):
    return [list(reversed(row)) for row in grid]


def compress(row):
    new_row = [value for value in row if value != 0]
    new_row += [0] * (GRID_SIZE - len(new_row))
    return new_row


def merge(row):
    score = 0
    for i in range(GRID_SIZE - 1):
        if row[i] != 0 and row[i] == row[i + 1]:
            row[i] *= 2
            row[i + 1] = 0
            score += row[i]
    return row, score


def move_left(grid):
    changed = False
    score = 0
    new_grid = []
    for row in grid:
        compressed = compress(row)
        merged, row_score = merge(compressed)
        compressed = compress(merged)
        if compressed != row:
            changed = True
        new_grid.append(compressed)
        score += row_score
    return new_grid, changed, score


def move_right(grid):
    reversed_grid = reverse(grid)
    moved, changed, score = move_left(reversed_grid)
    return reverse(moved), changed, score


def move_up(grid):
    transposed = transpose(grid)
    moved, changed, score = move_left(transposed)
    return transpose(moved), changed, score


def move_down(grid):
    transposed = transpose(grid)
    moved, changed, score = move_right(transposed)
    return transpose(moved), changed, score


def can_move(grid):
    if any(cell == 0 for row in grid for cell in row):
        return True
    for r in range(GRID_SIZE):
        for c in range(GRID_SIZE - 1):
            if grid[r][c] == grid[r][c + 1]:
                return True
    for c in range(GRID_SIZE):
        for r in range(GRID_SIZE - 1):
            if grid[r][c] == grid[r + 1][c]:
                return True
    return False


def has_won(grid):
    return any(cell >= TARGET for row in grid for cell in row)


def read_move():
    while True:
        char = get_key().lower()
        if char in {"w", "a", "s", "d", "q"}:
            return char


def main():
    grid = new_grid()
    score = 0
    draw_initial(grid, score)

    while True:
        if has_won(grid) or not can_move(grid):
            break

        move = read_move()
        if move == "q":
            break

        old_grid = [row[:] for row in grid]
        if move == "a":
            new_grid_state, changed, gained = move_left(grid)
        elif move == "d":
            new_grid_state, changed, gained = move_right(grid)
        elif move == "w":
            new_grid_state, changed, gained = move_up(grid)
        else:
            new_grid_state, changed, gained = move_down(grid)

        if not changed:
            continue

        grid = new_grid_state
        score += gained
        add_random_tile(grid)
        update_grid(old_grid, grid)
        update_score(score, max(cell for row in grid for cell in row))
        move_cursor(14, 1)

    move_cursor(14, 1)
    write(f"game over. final score: {score}\033[K\n")


if __name__ == "__main__":
    main()
