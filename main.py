#!/usr/bin/env python3
"""Entry point for Perudo game."""

from src.game import PerudoGame


def main():
    """Run the Perudo game."""
    try:
        game = PerudoGame()
        game.play()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
        raise


if __name__ == "__main__":
    main()
