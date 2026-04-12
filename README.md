# sokoban-difficulty-metrics
Sokoban difficulty metrics

Metrics designed by Carlos Montiers Aguilera to reflect human-solving difficulty from LURD solutions:

- **Logical pushes**: Pushes where only one non-deadlocking option exists among alternatives; the player had choices, but only one avoids deadlock. Pushes of a box to its final goal are not considered.
- **Box detour**: Average (per box) of the maximum distance from its starting position, excluding the final push sequence to its goal; measures how much boxes "wander" before being solved. A higher number indicates a puzzle where boxes are pushed far from their original position. A low number indicates a puzzle where boxes are not moved much, which could be considered easier.
- **Air**: Floor count / boxes. This indicates the amount of "air" a puzzle has.
- **Task switching**: Box changes / boxes. This reflects how dynamic the player is, changing between boxes. A higher number reflects the solution pushing boxes more than once, meaning more repetitive pushing of boxes at different times.
- **Avg valid push directions**: The average number of positions a box can be pushed each time the player pushes it. Pushes to the final goal are not considered. This reflects the number of decisions a player considered and ignored when choosing a particular push. For example, the player could push this box to 10 positions; the next time, to 5 positions. This is used to calculate the average.
- **Deadlock guidance**: Logical pushes / Box lines (straight line box pushes). This indicates how much the puzzle structure helps to solve the puzzle. A higher value indicates an easier level (for players who consider this or who play with deadlock detection enabled).

### Analysis Example

Evaluated 7 puzzles from Aymeric du Peloux's Microcosmos and Minicosmos collections:

| # | Level             | Boxes | Floor | Moves | Pushes | Box-Lines | Box-Changes | Pushing-Sessions | Pusher-Lines | Logical-Pushes | Box-Detour | Air  | Task-Switching | Avg-Valid-Push-Directions | Deadlock-Guidance |
|---|-------------------|-------|-------|-------|--------|-----------|-------------|------------------|--------------|----------------|-----------|------|----------------|--------------------------|-------------------|
| 1 | Microcosmos 31    | 4     | 27    | 101   | 18     | 17        | 17          | 12               | 64           | 6              | 3.0     | 6.75 | 4.25           | 2.0                      | 0.35                |
| 2 | Microcosmos 29    | 4     | 21    | 101   | 26     | 22        | 16          | 19               | 77           | 6              | 2.25    | 5.25 | 4.0            | 2.21                     | 0.27                |
| 3 | Minicosmos 30     | 3     | 30    | 168   | 51     | 30        | 18          | 28               | 106          | 7              | 6.0     | 10.0 | 6.0            | 1.48                     | 0.23                |
| 4 | Microcosmos 22    | 4     | 36    | 208   | 57     | 33        | 22          | 30               | 97           | 6              | 6.75    | 9.0  | 5.5            | 2.06                     | 0.18                |
| 5 | Microcosmos 25    | 4     | 28    | 153   | 38     | 20        | 14          | 19               | 95           | 3              | 3.25    | 7.0  | 3.5            | 1.67                     | 0.15                |
| 6 | Microcosmos 24    | 5     | 34    | 191   | 37     | 28        | 23          | 25               | 114          | 4              | 2.4     | 6.8  | 4.6            | 1.57                     | 0.14                |
| 7 | Microcosmos 34    | 4     | 25    | 100   | 29     | 19        | 16          | 15               | 61           | 3              | 2.25    | 6.25 | 4.0            | 1.46                     | 0.16                |

The **deadlock-guidance** metric proved particularly useful for comparing difficulty—higher values indicate easier puzzles where the structure naturally guides players away from deadlock situations.
More details here: https://groups.io/g/sokoban/message/1186

Programmed with LLM assistance, then manually fixed and verified.

## Usage

```bash
python sokoban_metrics.py levels.xsb
