# sokoban-difficulty-metrics
Sokoban difficulty metrics

Metrics designed by Carlos Montiers Aguilera to reflect human-solving difficulty from LURD solutions:

- **Logical pushes**: Pushes where only one non-deadlocking option exists among alternatives; the player had choices, but only one avoids deadlock. Pushes of a box to its final goal are not considered.
- **Box detour**: Average (per box) of the maximum distance from its starting position, excluding the final push sequence to its goal; measures how much boxes "wander" before being solved. A higher number indicates a puzzle where boxes are pushed far from their original position. A low number indicates a puzzle where boxes are not moved much, which could be considered easier.
- **Air**: Floor count / boxes. This indicates the amount of "air" a puzzle has.
- **Task switching**: Box changes / boxes. This reflects how dynamic the player is, changing between boxes. A higher number reflects the solution pushing boxes more than once, meaning more repetitive pushing of boxes at different times.
- **Avg valid push directions**: The average number of positions a box can be pushed each time the player pushes it. Pushes to the final goal are not considered. This reflects the number of decisions a player considered and ignored when choosing a particular push. For example, the player could push this box to 10 positions; the next time, to 5 positions. This is used to calculate the average.
- **Deadlock guidance**: Logical pushes / Box lines (straight line box pushes). This indicates how much the puzzle structure helps to solve the puzzle. A higher value indicates an easier level (for players who consider this or who play with deadlock detection enabled).

> **Puzzle credit**: The 7 puzzles used for evaluation are from Aymeric du Peloux's Microcosmos and Minicosmos collections.

Programmed with LLM assistance, then manually fixed and verified.

## Usage

```bash
python sokoban_metrics.py levels.xsb
