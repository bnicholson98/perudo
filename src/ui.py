"""Terminal UI for Perudo game."""
from typing import List, Optional
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt, IntPrompt
from rich.text import Text
from rich import box
from src.player import Player
from src.bid import Bid


# Dice face representations
DICE_FACES = {
    1: "⚀",
    2: "⚁",
    3: "⚂",
    4: "⚃",
    5: "⚄",
    6: "⚅"
}


class UI:
    """Handles all terminal input/output for the game."""

    def __init__(self):
        """Initialize UI with rich console."""
        self.console = Console()

    def clear_screen(self):
        """Clear the terminal screen."""
        self.console.clear()

    def print_banner(self):
        """Print the game banner."""
        banner_text = Text("PERUDO", style="bold magenta", justify="center")
        subtitle = Text("The Game of Bluff and Deception", style="italic cyan", justify="center")

        self.console.print()
        self.console.print(Panel(
            Text.assemble(banner_text, "\n", subtitle),
            box=box.DOUBLE,
            style="bold cyan",
            padding=(1, 2)
        ))
        self.console.print()

    def print_rules_summary(self):
        """Print a brief rules summary."""
        rules = """
[bold cyan]Quick Rules:[/bold cyan]
  [yellow]•[/yellow] Ones are [bold red]WILD[/bold red] (except during Palifico)
  [yellow]•[/yellow] Bid higher quantity [bold]OR[/bold] higher face value
  [yellow]•[/yellow] Call [bold red]'dudo'[/bold red] to challenge, [bold green]'calza'[/bold green] for exact match
  [yellow]•[/yellow] [bold magenta]Palifico[/bold magenta]: When reduced to 1 die, face value locks
"""
        self.console.print(Panel(rules, border_style="cyan", padding=(0, 2)))
        self.console.print()

    def get_player_count(self) -> int:
        """Get number of players from user.

        Returns:
            Number of players (2-6)
        """
        while True:
            count = IntPrompt.ask(
                "[bold cyan]Enter number of players[/bold cyan]",
                console=self.console
            )
            if 2 <= count <= 6:
                return count
            self.console.print("[red]Please enter a number between 2 and 6.[/red]")

    def get_player_names(self, count: int) -> List[str]:
        """Get player names from user.

        Args:
            count: Number of players

        Returns:
            List of player names
        """
        names = []
        for i in range(count):
            name = Prompt.ask(
                f"[bold cyan]Enter name for Player {i + 1}[/bold cyan]",
                console=self.console,
                default=f"Player {i + 1}"
            ).strip()
            if not name:
                name = f"Player {i + 1}"
            names.append(name)
        return names

    def show_player_dice(self, player: Player):
        """Show a player their dice.

        Args:
            player: The player whose dice to show
        """
        dice_display = " ".join(DICE_FACES.get(d, str(d)) for d in player.dice.get_values())

        self.console.print()
        self.console.print(Panel(
            f"[bold yellow]{player.name}[/bold yellow], your dice:\n\n"
            f"[bold white]{dice_display}[/bold white]\n"
            f"[dim]({player.dice.get_values()})[/dim]",
            border_style="yellow",
            box=box.ROUNDED,
            padding=(1, 2)
        ))

    def show_all_dice(self, players: List[Player]):
        """Show all players' dice (for reveal).

        Args:
            players: List of all players
        """
        table = Table(title="[bold red]REVEALING ALL DICE[/bold red]", box=box.DOUBLE_EDGE, border_style="red")
        table.add_column("Player", style="cyan", justify="left")
        table.add_column("Dice", style="bold white", justify="center")
        table.add_column("Values", style="dim", justify="left")

        for player in players:
            if player.is_active and player.dice.count > 0:
                dice_display = " ".join(DICE_FACES.get(d, str(d)) for d in player.dice.get_values())
                table.add_row(
                    player.name,
                    dice_display,
                    str(player.dice.get_values())
                )

        self.console.print()
        self.console.print(table)
        self.console.print()

    def show_game_state(self, players: List[Player], current_bid: Optional[Bid],
                       current_player_idx: int, is_palifico: bool):
        """Show current game state.

        Args:
            players: List of all players
            current_bid: Current bid (None if start of round)
            current_player_idx: Index of current player
            is_palifico: Whether this is a Palifico round
        """
        table = Table(title="[bold cyan]GAME STATE[/bold cyan]", box=box.ROUNDED, border_style="cyan")
        table.add_column("Player", style="yellow")
        table.add_column("Dice", justify="center")
        table.add_column("Status", justify="center")

        for idx, player in enumerate(players):
            is_current = idx == current_player_idx

            if player.is_active:
                dice_icons = "🎲 " * player.dice.count
                status_parts = []

                if is_current:
                    status_parts.append("[bold green]← CURRENT[/bold green]")
                if player.is_in_palifico():
                    status_parts.append("[bold magenta]PALIFICO[/bold magenta]")

                status = " ".join(status_parts) if status_parts else ""

                name_style = "bold green" if is_current else "yellow"
                table.add_row(
                    f"[{name_style}]{player.name}[/{name_style}]",
                    dice_icons,
                    status
                )
            else:
                table.add_row(
                    f"[dim]{player.name}[/dim]",
                    "[dim]---[/dim]",
                    "[red]ELIMINATED[/red]"
                )

        self.console.print()
        self.console.print(table)

        if is_palifico:
            self.console.print()
            self.console.print(Panel(
                "[bold magenta]PALIFICO ROUND[/bold magenta]\n"
                "Face value locked • Ones are NOT wild",
                border_style="magenta",
                box=box.HEAVY
            ))

        if current_bid:
            bid_face = DICE_FACES.get(current_bid.face, str(current_bid.face))
            self.console.print()
            self.console.print(Panel(
                f"[bold white]Current bid: {current_bid.quantity} × {bid_face} ({current_bid.face}s)[/bold white]",
                border_style="white",
                box=box.ROUNDED
            ))
        else:
            self.console.print("\n[dim]No bid yet this round.[/dim]")

        self.console.print()

    def get_player_action(self, player: Player, has_bid: bool) -> str:
        """Get action from player.

        Args:
            player: The current player
            has_bid: Whether there's a current bid

        Returns:
            Action string ('bid', 'dudo', or 'calza')
        """
        self.console.print(f"\n[bold yellow]{player.name}'s turn:[/bold yellow]")

        if not has_bid:
            self.console.print("  [cyan]1[/cyan] Make a bid")
            choice = Prompt.ask(
                "Choose action",
                choices=["1"],
                default="1",
                console=self.console
            )
            return "bid"
        else:
            self.console.print("  [cyan]1[/cyan] Raise the bid")
            self.console.print("  [red]2[/red] Call 'Dudo' (challenge)")
            self.console.print("  [green]3[/green] Call 'Calza' (claim exact)")

            choice = Prompt.ask(
                "Choose action",
                choices=["1", "2", "3"],
                console=self.console
            )

            if choice == "1":
                return "bid"
            elif choice == "2":
                return "dudo"
            else:
                return "calza"

    def get_bid_input(self, previous_bid: Optional[Bid], is_palifico: bool) -> Optional[Bid]:
        """Get bid from user.

        Args:
            previous_bid: Previous bid (None if first)
            is_palifico: Whether this is a Palifico round

        Returns:
            Bid object or None if cancelled
        """
        self.console.print("\n[bold cyan]Enter your bid:[/bold cyan]")

        while True:
            try:
                quantity = IntPrompt.ask("  Quantity", console=self.console)

                if is_palifico and previous_bid:
                    face = previous_bid.face
                    face_icon = DICE_FACES.get(face, str(face))
                    self.console.print(f"  [magenta]Face value locked at: {face_icon} ({face}) (Palifico)[/magenta]")
                else:
                    face = IntPrompt.ask("  Face value (1-6)", console=self.console)

                if face < 1 or face > 6:
                    self.console.print("[red]Face value must be between 1 and 6.[/red]")
                    continue

                return Bid(quantity, face)

            except ValueError:
                self.console.print("[red]Please enter valid numbers.[/red]")

    def pause_for_player_change(self, next_player: Player):
        """Pause and prompt for next player.

        Args:
            next_player: The next player
        """
        self.console.print()
        self.console.print(Panel(
            f"[bold yellow]Pass to {next_player.name}[/bold yellow]",
            border_style="yellow",
            box=box.ROUNDED
        ))
        self.console.input("[dim]Press Enter when ready...[/dim]")
        self.clear_screen()

    def show_message(self, message: str):
        """Show a message to the user.

        Args:
            message: Message to display
        """
        self.console.print(f"\n[bold]{message}[/bold]\n")

    def show_winner(self, player: Player):
        """Display the winner.

        Args:
            player: The winning player
        """
        winner_text = Text(f"{player.name} WINS!", style="bold yellow", justify="center")
        trophy = "🏆"

        self.console.print()
        self.console.print(Panel(
            Text.assemble(
                Text(f"{trophy} ", style="yellow"),
                winner_text,
                Text(f" {trophy}", style="yellow")
            ),
            box=box.DOUBLE,
            style="bold yellow",
            padding=(2, 4)
        ))
        self.console.print()

    def show_round_start(self):
        """Display round start message."""
        self.console.print()
        self.console.print(Panel(
            "[bold cyan]NEW ROUND - ROLLING DICE[/bold cyan] 🎲",
            border_style="cyan",
            box=box.HEAVY,
            padding=(1, 2)
        ))
