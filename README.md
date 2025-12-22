# Perudo

A terminal-based implementation of the classic dice bluffing game Perudo (also known as Liar's Dice or Dudo).

## About

Perudo is a strategic dice game of deception and probability where players make bids about the collective dice pool, attempting to outwit their opponents. The last player with dice remaining wins the game.

## Requirements

- Python 3.8 or higher
- pip (Python package installer)

## Installation

```bash
pip install -r requirements.txt
```

## How to Play

### Setup
- 2-6 players (local multiplayer)
- Each player starts with 5 dice and a cup
- Players roll their dice in secret at the start of each round

### Game Flow

1. **Bidding**: The first player makes a bid about the total number of a specific face value among all dice in play (e.g., "five 3s")

2. **Turn Progression**: Play proceeds clockwise. On your turn, you must either:
   - **Raise the bid**: Increase the quantity or the face value
   - **Call "Dudo"**: Challenge the previous bid
   - **Call "Calza"**: Claim the previous bid is exactly correct (to win back a die)

3. **Revealing**: When "Dudo" is called, all players reveal their dice:
   - If the bid was correct or exceeded: the challenger loses a die
   - If the bid was incorrect: the bidder loses a die

4. **Winning**: The last player with dice remaining wins

### Special Rules

#### Wild Ones
- Ones are wild and count as any face value
- Exception: During Palifico rounds (see below)

#### Bidding on Ones
- You may bid on face value 1 by halving the previous quantity (rounded up)
- Example: A bid of "six 4s" can become "three 1s"

#### Bidding Away from Ones
- When changing from a bid on 1s to another face value, you must double the quantity and add 1
- Example: A bid of "three 1s" must become at least "seven [2-6]s"

#### Calza
- Call "Calza" to claim the previous bid is exactly correct
- If correct: you gain one die (maximum of 5 dice)
- If incorrect: you lose a die

#### Palifico Round
- Triggered when a player is reduced to exactly one die (occurs only once per player)
- During this round:
  - The face value of bids cannot change (only quantities increase)
  - Ones are **not** wild
  - Palifico ends when that player gains or loses a die

## Development

This project is being developed for personal learning purposes.

### Project Structure
```
perudo/
├── README.md
├── Claude.md          # Agent-specific development notes
├── requirements.txt   # Python dependencies
└── src/              # Source code (to be implemented)
```

## License

This project is for personal and educational use.

## Contributing

This is a personal learning project and is not currently accepting contributions.
