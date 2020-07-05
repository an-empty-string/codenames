import logging

from .state import UNLIMITED, Team
from .utils import plural


class Interface():

    def set_game(self, game):
        self.game = game

    def tell(self, message):
        logging.info(message)

    def tell_private(self, player, message):
        logging.info(f"(privately to {player}): {message}")

    def format_team(self, team):
        return str(team)

    def format_player(self, player):
        return str(player)

    def player_joins(self, player, team=None):
        if team is None:
            self.tell(f"{self.format_player(player)} has joined the game.")
        else:
            self.tell(
                f"{self.format_player(player)} has joined the {self.format_team(team)} team.")

    def player_leaves(self, player):
        self.tell(f"{self.format_player(player)} has left the game.")

    def player_team_moved(self, player, new_team):
        self.tell(
            f"{self.format_player(player)}'s team preference was unavailable, so they have been moved to the "
            f"{self.format_team(new_team)} team.")

    def assassin_guessed(self, actor, word):
        self.tell(f"{self.format_player(actor)} has revealed the assassin, {word}!")

    def civilian_guessed(self, actor, word):
        self.tell(f"{self.format_player(actor)} has revealed a civilian ({word}).")

    def team_guessed(self, actor, team, word):
        remaining = len(self.game.remaining_words[team])
        self.tell(
            f"{self.format_player(actor)} has revealed a {self.format_team(team)} agent. {remaining} left."
        )

        if team == self.game.active_team and self.game.remaining_guesses:
            if self.game.remaining_guesses is not UNLIMITED:
                self.tell(f"The {self.format_team(team)} team has "
                          f"{plural(self.game.remaining_guesses, 'guess', 'guesses')} left.")

            else:
                self.tell(f"The {self.format_team(team)} team has unlimited guesses left.")

    def spymaster_view(self):
        greens = ", ".join(self.game.remaining_words[Team.GREEN])
        pinks = ", ".join(self.game.remaining_words[Team.PINK])
        civilians = ", ".join(self.game.remaining_words[Team.GRAY])

        return (f"Assassin: {self.game.assassin} | {self.format_team(Team.GREEN)}: {greens} | "
                f"{self.format_team(Team.PINK)}: {pinks} | Civilians: {civilians}")

    def full_words_view(self):
        greens = ", ".join(self.game.words[Team.GREEN])
        pinks = ", ".join(self.game.words[Team.PINK])
        civilians = ", ".join(self.game.words[Team.GRAY])

        return (f"Assassin: {self.game.assassin} | {self.format_team(Team.GREEN)}: {greens} | "
                f"{self.format_team(Team.PINK)}: {pinks} | Civilians: {civilians}")

    def notify_start(self):
        players = ", ".join(self.format_player(p) for p in self.game.players)
        self.tell(f"{players}: Welcome to an exciting game of Codenames.")
        self.notify_teams()

        self.tell_private(self.game.teams[Team.PINK].spymaster, self.spymaster_view())

    def notify_teams(self):
        for team in [Team.GREEN, Team.PINK]:
            team = self.game.teams[team]
            members = ", ".join([f"{self.format_player(team.spymaster)} (spymaster)"] +
                                [self.format_player(p) for p in team.guessers])
            self.tell(f"{self.format_team(team.team)}: {members}")

        if self.game.teams[Team.GRAY].guessers:
            members = ", ".join(self.format_player(p) for p in self.game.teams[Team.GRAY])
            self.tell(f"{self.format_team(Team.GRAY)}: {members}")

    def notify_hinting(self, team, spymaster):
        self.tell(
            f"{self.format_player(spymaster)}: You're up! It's {self.format_team(team)}'s turn to hint."
        )
        self.tell_private(spymaster, self.spymaster_view())

    def notify_guessing(self, team, guessers):
        joined = ", ".join(self.format_player(g) for g in guessers)

        hint = self.game.current_hint
        number_str = "unlimited" if hint[1] is UNLIMITED else str(hint[1])

        self.tell(f"{joined}: You're up! It's {self.format_team(team)}'s turn to guess. "
                  f"The clue is {hint[0]} ({number_str}).")

        words_left = ", ".join(self.game.all_words)
        self.tell(f"Here are the remaining words: {words_left}.")

    def notify_winner(self):
        self.tell(f"The game is over. The {self.format_team(self.game.winner)} team wins!")
        self.tell(f"Words: {self.full_words_view()}")
