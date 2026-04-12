import sys
from collections import deque
import math

# Metrics by Carlos Montiers Aguilera:
# logical-pushes, box-detour, air, task-switching, avg-valid-push-directions, deadlock-guidance.
# Programmed with LLM assistance, then manually fixed and verified.

DIRECTIONS = {'u': (0, -1), 'd': (0, 1), 'l': (-1, 0), 'r': (1, 0)}
WALL = '#'

def clean_lines(text):
    return [line.rstrip("\n") for line in text.splitlines()]

def is_board_line(line):
    stripped = line.strip()
    if stripped == "" or stripped.startswith("::"):
        return False
    return all(c in "#$@*+. _-" for c in stripped)

def is_solution_line(line):
    stripped = line.strip()
    if stripped == "" or stripped.startswith("::"):
        return False
    return all(c in "LURDlurd" for c in stripped)

def parse_levels(lines):
    parsed_levels = []
    index = 0
    while index < len(lines):
        while index < len(lines) and not is_board_line(lines[index]):
            index += 1
        if index >= len(lines): break
        level_name = f"Level_{len(parsed_levels) + 1}"
        search_idx = index - 1
        while search_idx >= 0:
            if lines[search_idx].strip() and not lines[search_idx].startswith("::"):
                level_name = lines[search_idx].strip().replace(",", " ")
                break
            search_idx -= 1
        grid_lines = []
        while index < len(lines) and is_board_line(lines[index]):
            grid_lines.append(lines[index])
            index += 1
        solution_moves = ""
        while index < len(lines) and "solution" not in lines[index].lower():
            if is_board_line(lines[index]): break
            index += 1
        if index < len(lines) and "solution" in lines[index].lower():
            index += 1
            while index < len(lines) and is_solution_line(lines[index]):
                solution_moves += lines[index].strip()
                index += 1
        else:
            while index < len(lines) and is_solution_line(lines[index]):
                solution_moves += lines[index].strip()
                index += 1
        if grid_lines:
            parsed_levels.append((level_name, grid_lines, solution_moves))
    return parsed_levels

def compute_floor_inside(grid, start_pos):
    queue = deque([start_pos])
    visited = {start_pos}
    count = 0

    while queue:
        x, y = queue.popleft()
        if grid[y][x] != WALL:
            count += 1

        for dx, dy in DIRECTIONS.values():
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited:
                continue
            if ny < 0 or ny >= len(grid) or nx < 0 or nx >= len(grid[0]):
                continue
            if grid[ny][nx] == WALL:
                continue

            visited.add((nx, ny))
            queue.append((nx, ny))

    return count

def build_state(grid_lines):
    width = max(len(row) for row in grid_lines)
    grid = [list(row.ljust(width, WALL)) for row in grid_lines]
    box_positions, goal_positions = {}, set()
    player_pos, next_box_id = None, 0
    for y, row in enumerate(grid):
        for x, cell in enumerate(row):
            if cell in ('$', '*'):
                box_positions[(x, y)] = next_box_id
                next_box_id += 1
            if cell in ('.', '*', '+'): goal_positions.add((x, y))
            if cell in ('@', '+'): player_pos = (x, y)
            # normalize grid
            grid[y][x] = WALL if cell == WALL else ' '
    # compute only reachable floor
    floor_count = compute_floor_inside(grid, player_pos)
    return grid, box_positions, player_pos, goal_positions, floor_count

def reachable_positions(grid, box_positions, start_pos):
    queue = deque([start_pos])
    visited = {start_pos}
    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS.values():
            nx, ny = x + dx, y + dy
            if (nx, ny) in visited: continue
            if ny < 0 or ny >= len(grid) or nx < 0 or nx >= len(grid[0]): continue
            if grid[ny][nx] == WALL or (nx, ny) in box_positions: continue
            visited.add((nx, ny))
            queue.append((nx, ny))
    return visited

def compute_safe_positions(grid, goal_positions):
    safe = set(goal_positions)
    queue = deque(goal_positions)
    h, w = len(grid), len(grid[0])
    while queue:
        x, y = queue.popleft()
        for dx, dy in DIRECTIONS.values():
            px, py = x - dx, y - dy
            plx, ply = px - dx, py - dy
            if not (0 <= py < h and 0 <= px < w and 0 <= ply < h and 0 <= plx < w): continue
            if grid[py][px] == WALL or grid[ply][plx] == WALL: continue
            if (px, py) not in safe:
                safe.add((px, py))
                queue.append((px, py))
    return safe

def get_push_opts(grid, boxes, p_pos, b_pos, goals, safe):
    reachable = reachable_positions(grid, boxes, p_pos)
    bx, by = b_pos
    opts = []
    for d, (dx, dy) in DIRECTIONS.items():
        req_p, tar_b = (bx - dx, by - dy), (bx + dx, by + dy)
        if req_p in reachable and 0 <= tar_b[1] < len(grid) and 0 <= tar_b[0] < len(grid[0]):
            if grid[tar_b[1]][tar_b[0]] != WALL and tar_b not in boxes:
                is_deadlock = tar_b not in goals and tar_b not in safe
                opts.append(not is_deadlock)
    return opts

def simulate(grid, init_boxes, p_start, goals, safe, floor_count, solution):
    moves_list = [c for c in solution if c in "udlrUDLR"]
    num_boxes = len(init_boxes)
    
    curr_boxes = dict(init_boxes)
    p_pos = p_start
    box_push_history = {bid: [] for bid in init_boxes.values()}
    global_push_idx = 0
    for m in moves_list:
        dx, dy = DIRECTIONS[m.lower()]
        next_p = (p_pos[0] + dx, p_pos[1] + dy)
        if m.isupper():
            global_push_idx += 1
            bid = curr_boxes[next_p]
            next_b = (next_p[0] + dx, next_p[1] + dy)
            box_push_history[bid].append(global_push_idx)
            del curr_boxes[next_p]
            curr_boxes[next_b] = bid
        p_pos = next_p

    final_travel_start = {}
    for bid, history in box_push_history.items():
        if not history: continue
        start_idx = history[-1]
        for i in range(len(history)-2, -1, -1):
            if history[i] == history[i+1] - 1: start_idx = history[i]
            else: break
        final_travel_start[bid] = start_idx

    curr_boxes = dict(init_boxes)
    p_pos = p_start
    box_origins = {bid: pos for pos, bid in init_boxes.items()}
    push_total, box_switches, sessions, dir_changes, box_line_cnt = 0, 0, 0, 0, 0
    logical_pushes, total_valid_opts, valid_push_count = 0, 0, 0
    max_detours = {bid: 0 for bid in init_boxes.values()}
    last_m_dir, last_b_id, is_pushing = None, None, False
    global_push_idx = 0

    for m in moves_list:
        m_low = m.lower()
        dx, dy = DIRECTIONS[m_low]
        if m_low != last_m_dir: dir_changes += 1
        next_p = (p_pos[0] + dx, p_pos[1] + dy)
        if m.isupper():
            global_push_idx += 1
            push_total += 1
            bid = curr_boxes[next_p]
            next_b = (next_p[0] + dx, next_p[1] + dy)
            if global_push_idx < final_travel_start.get(bid, float('inf')):
                opts = get_push_opts(grid, curr_boxes, p_pos, next_p, goals, safe)
                valid_push_count += 1
                total_valid_opts += len(opts)
                if len(opts) > 1 and sum(opts) == 1: logical_pushes += 1
                dist = abs(next_b[0] - box_origins[bid][0]) + abs(next_b[1] - box_origins[bid][1])
                if dist > max_detours[bid]: max_detours[bid] = dist
            if not is_pushing:
                sessions += 1
                is_pushing = True
            if last_b_id != bid: box_switches += 1
            if last_b_id != bid or last_m_dir != m_low: box_line_cnt += 1
            del curr_boxes[next_p]
            curr_boxes[next_b] = bid
            last_b_id = bid
        else: is_pushing = False
        p_pos = next_p
        last_m_dir = m_low

    box_detour = round(sum(max_detours.values()) / len(max_detours) if max_detours else 0, 2)

    air = round(floor_count / num_boxes, 2) if num_boxes > 0 else 0

    task_switching = round(box_switches / num_boxes, 2) if num_boxes > 0 else 0
    avg_valid_push_directions = round(total_valid_opts / valid_push_count if valid_push_count > 0 else 0, 2)
    deadlock_guidance = round(logical_pushes / box_line_cnt, 2) if box_line_cnt > 0 else 0

    return [
        num_boxes, floor_count, len(moves_list), push_total, box_line_cnt, box_switches,
        sessions, dir_changes,
        logical_pushes, box_detour, air,
        task_switching, avg_valid_push_directions, deadlock_guidance
    ]

def main():
    if len(sys.argv) < 2: return
    with open(sys.argv[1], encoding="utf-8") as f:
        lines = clean_lines(f.read())
    levels = parse_levels(lines)
    
    header = ("# Level boxes floor moves pushes box-lines box-changes pushing-sessions pusher-lines "
              "logical-pushes box-detour air "
              "task-switching avg-valid-push-directions deadlock-guidance")
    print(header)
    
    for i, (name, grid_lines, sol) in enumerate(levels, 1):
        if not sol: continue
        grid, boxes, p_pos, goals, floor_count = build_state(grid_lines)
        safe = compute_safe_positions(grid, goals)
        res = simulate(grid, boxes, p_pos, goals, safe, floor_count, sol)
        print(f'{i} "{name}" {" ".join(map(str, res))}')

if __name__ == "__main__":
    main()