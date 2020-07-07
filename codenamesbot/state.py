import collections
import enum
import math
import random

from .words import WORDS

UNLIMITED = object()


class Player:

    def __init__(self, name):
        self.name = name
        self.team = None
        self.spymaster_preference = False

    def rename(self, new_name):
        self.name = new_name

    def toggle_spymaster_preference(self):
        self.spymaster_preference = not self.spymaster_preference
        return self.spymaster_preference

    def __str__(self):
        return self.name


class Players:

    def __init__(self):
        self.players = []

    def add(self, name):
        p = Player(name)
        self.players.append(p)
        return p

    def remove(self, name):
        self.players.remove(self[name])

    def get(self, name):
        for player in self.players:
            if player.name == name:
                return player

    def shuffled(self):
        shuffled_players = self.players[::]
        random.shuffle(shuffled_players)
        return shuffled_players

    def __iter__(self):
        return iter(self.players)

    def __len__(self):
        return len(self.players)

    def __contains__(self, name):
        return self.get(name) is not None

    def __getitem__(self, name):
        player = self.get(name)
        if player:
            return player

        raise KeyError(f"{name} is not playing!")

    def __str__(self):
        n = len(self)
        plural = "s" if n != 1 else ""
        players = ", ".join(map(str, self.players))

        return f"{n} player{plural}: {players}"


class GameMode(enum.Enum):
    GRAY = 1
    VERSUS = 2


class GamePhase(enum.Enum):
    PRE_GAME = 1
    HINTING = 2
    GUESSING = 3
    POST_GAME = 4


class Team(enum.Enum):
    GREEN = 1
    PINK = 2
    GRAY = 3

    def __str__(self):
        return self.name.title()

    def __invert__(self):
        return {Team.GREEN: Team.PINK, Team.PINK: Team.GREEN, Team.GRAY: Team.GRAY}[self]


class PlayingTeam:

    def __init__(self, team):
        self.team = team
        self.players = []

    @property
    def spymaster(self):
        if self.team == Team.GRAY or not self.players:
            return None

        return self.players[0]

    @property
    def guessers(self):
        if self.team == Team.GRAY:
            return self.players

        return self.players[1:]

    def add(self, player):
        self.players.append(player)

    def __len__(self):
        return len(self.players)

    def __iter__(self):
        return iter(self.players)

    def __contains__(self, player):
        return player in self.players


class InvalidGameState(Exception):
    pass


class Game:

    def __init__(self, interface=None):
        # State machine consists of these two variables
        self.phase = GamePhase.PRE_GAME
        self.active_team = None

        # Game active state consists of these
        self.teams = {team: PlayingTeam(team) for team in Team}

        self.words = {team: [] for team in Team}  # gray words are civilians
        self.remaining_words = {team: [] for team in Team}
        self.guessed_words = {team: [] for team in Team}
        self.assassin = None

        self.all_words = []

        self.current_hint = (None, 0)
        self.remaining_guesses = 0

        self.winner = None

        # Game moderation state consists of these
        self.votekicks = collections.defaultdict(set)

        # Game configuration consists of these
        self.players = Players()
        self.mode = GameMode.VERSUS

        if interface is None:
            from .interface import Interface
            interface = Interface()

        self.interface = interface
        interface.set_game(self)

    def join(self, player, team=None):
        if self.phase == GamePhase.POST_GAME:
            raise InvalidGameState("Joins are not accepted after the game is over.")

        if player in self.players:
            raise InvalidGameState(f"{player} is already in the game!")

        player = self.players.add(player)

        if self.phase != GamePhase.PRE_GAME:
            # try to assign the player to their preferred team, but fail if unbalanced or in gray mode
            if self.mode == GameMode.GRAY:
                if team is not None and team != Team.GRAY:
                    self.interface.player_team_moved(player, Team.GRAY)

                team = Team.GRAY

            elif team == Team.GRAY:
                team = None

            elif len(self.teams[Team.GREEN]) < len(self.teams[Team.PINK]) and team == Team.PINK:
                team = Team.GREEN
                self.interface.player_team_moved(player, Team.GREEN)

            elif len(self.teams[Team.PINK]) < len(self.teams[Team.GREEN]) and team == Team.GREEN:
                team = Team.PINK
                self.interface.player_team_moved(player, Team.PINK)

            if not team:
                if len(self.teams[Team.GREEN]) < len(self.teams[Team.PINK]):
                    team = Team.GREEN
                elif len(self.teams[Team.PINK]) < len(self.teams[Team.GREEN]):
                    team = Team.PINK
                else:
                    team = random.choice([Team.GREEN, Team.PINK])

            self.teams[team].add(player)
            self.interface.player_joins(player, team=team)

        else:
            self.interface.player_joins(player)

        player.team = team
        return player

    def leave(self, player):
        if self.phase != GamePhase.PRE_GAME:
            raise InvalidGameState("You can only leave the game before it has started.")

        if player not in self.players:
            raise InvalidGameState(f"{player} is already not in the game!")

        self.players.remove(player)
        self.interface.player_leaves(player)

    def assign_teams(self):
        players = self.players.shuffled()

        for player in players[::]:
            # pull players with team preference to the front
            if player.team is not None:
                players.remove(player)
                players.insert(0, player)

        for player in players[::]:
            # pull players with spymaster preference but no team preference to the front
            if player.spymaster_preference:
                players.remove(player)
                players.insert(0, player)

        # player order is random but with these groups in order:
        # - first, players with spymaster preference, but no team preference
        # - second, players with team preference
        # - third, players with no preference at all

        # this makes it pretty easy for gamemode assignment methods to simply assign to teams that have
        # room left on them while respecting team preference

        if self.mode == GameMode.GRAY:
            self._assign_teams_gray(players)

        elif self.mode == GameMode.VERSUS:
            self._assign_teams_versus(players)

        for player in self.players:
            for team, playing_team in self.teams.items():
                if player in playing_team:
                    player.team = team

    def _assign_teams_gray(self, players):
        # find the first green and pink player. sort gray players at the back
        green = None
        pink = None

        for player in players[::]:
            if player.team == Team.GRAY:
                players.remove(player)
                players.append(player)

        for player in players[::]:
            if player.team == Team.GREEN and green is None:
                green = player
                players.remove(player)

            elif player.team == Team.PINK and pink is None:
                pink = player
                players.remove(player)

        if green is None:
            green = players.pop(0)
        if pink is None:
            pink = players.pop(0)

        self.teams[Team.GREEN].add(green)
        self.teams[Team.PINK].add(pink)
        self.teams[Team.GRAY].players.extend(players)

    def _assign_teams_versus(self, players):
        max_players = math.ceil(len(self.players) / 2)

        for player in players:
            if player.team in {Team.GREEN, Team.PINK}:
                # try assigning to preference first
                if len(self.teams[player.team]) < max_players:
                    self.teams[player.team].add(player)
                    continue

            # assign to first non-full team, unless spymaster pref + empty team
            if player.spymaster_preference and self.teams[Team.GREEN].spymaster is None:
                self.teams[Team.GREEN].add(player)
            elif player.spymaster_preference and self.teams[Team.PINK].spymaster is None:
                self.teams[Team.PINK].add(player)
            elif len(self.teams[Team.GREEN]) < max_players:
                self.teams[Team.GREEN].add(player)
            else:
                self.teams[Team.PINK].add(player)

    def assign_words(self):
        # word assignment is consistent regardless of gamemode:
        # - 9 green
        # - 8 pink
        # - 7 civilian
        # - 1 assassin

        words = WORDS.copy()
        random.shuffle(words)

        self.words[Team.GREEN] = words.consume(9)
        self.words[Team.PINK] = words.consume(8)
        self.words[Team.GRAY] = words.consume(7)
        self.assassin = words.popleft()

        self.all_words = (self.words[Team.GREEN] + self.words[Team.PINK] + self.words[Team.GRAY] +
                          [self.assassin])

        random.shuffle(self.all_words)

        for team in Team:
            self.remaining_words[team] = self.words[team].copy()

    def notify_phase(self):
        if self.phase == GamePhase.POST_GAME:
            self.interface.notify_winner()
        elif self.phase == GamePhase.HINTING:
            self.interface.notify_hinting(self.active_team, self.teams[self.active_team].spymaster)
        elif self.phase == GamePhase.GUESSING:
            guessers = self.teams[Team.GRAY].players + self.teams[self.active_team].guessers
            self.interface.notify_guessing(self.active_team, guessers)

    def start_game(self):
        if len(self.players) < 3:
            raise InvalidGameState("Not enough players to start the game.")

        if self.phase != GamePhase.PRE_GAME:
            raise InvalidGameState("Cannot start an in-progress game.")

        # make sure a valid game mode is selected for the given player count
        if len(self.players) < 4 and self.mode == GameMode.VERSUS:
            self.mode = GameMode.GRAY

        self.assign_teams()
        self.assign_words()

        self.phase = GamePhase.HINTING
        self.active_team = Team.GREEN

        self.interface.notify_start()
        self.notify_phase()

    def word_in_game(self, word):
        return any(word.lower() == i.lower() for i in self.all_words)

    def hint(self, actor, word, number):
        if self.phase != GamePhase.HINTING:
            raise InvalidGameState("Hints are not permitted outside of the hinting phase.")
        elif actor.team != self.active_team:
            raise InvalidGameState(f"{actor} can't hint for the {self.active_team} team.")
        elif self.teams[actor.team].spymaster != actor:
            raise InvalidGameState("Only spymasters are permitted to hint.")
        elif self.word_in_game(word.lower()):
            raise InvalidGameState("Hints may not be a word currently active in the game.")
        elif number is not UNLIMITED and (number < 0 or
                                          number > len(self.remaining_words[self.active_team])):
            raise InvalidGameState("Hints must be for either zero words, unlimited words, or "
                                   "some amount of words remaining for your team.")

        if number == 0 or number is UNLIMITED:
            self.remaining_guesses = UNLIMITED
        else:
            self.remaining_guesses = number + 1

        self.current_hint = (word, number)
        self.phase = GamePhase.GUESSING

        self.notify_phase()

    def guess(self, actor, word):
        if self.phase != GamePhase.GUESSING:
            raise InvalidGameState("Guesses are not permitted outside of the guessing phase.")
        elif actor.team not in {self.active_team, Team.GRAY}:
            raise InvalidGameState(f"{actor} can't guess for the {self.active_team} team.")
        elif self.teams[actor.team].spymaster == actor:
            raise InvalidGameState("Spymasters are not permitted to guess.")
        elif not self.word_in_game(word):
            raise InvalidGameState(f"{word} is not currently active in the game.")

        word = word.title()
        self.all_words.remove(word)

        if word == self.assassin:
            self.interface.assassin_guessed(actor, word)

            self.phase = GamePhase.POST_GAME
            self.winner = ~self.active_team

            self.interface.notify_winner()

        elif word in self.words[Team.GRAY]:
            self.remaining_words[Team.GRAY].remove(word)
            self.guessed_words[Team.GRAY].append(word)

            self.interface.civilian_guessed(actor, word)
            self.end_guessing()

        elif word in self.words[~self.active_team]:
            self.remaining_words[~self.active_team].remove(word)
            self.guessed_words[~self.active_team].append(word)

            self.interface.team_guessed(actor, ~self.active_team, word)
            self.end_guessing()

        elif word in self.words[self.active_team]:
            self.remaining_words[self.active_team].remove(word)
            self.guessed_words[self.active_team].append(word)

            if self.remaining_guesses != UNLIMITED:
                self.remaining_guesses -= 1

            self.interface.team_guessed(actor, self.active_team, word)

            if not self.check_win() and self.remaining_guesses == 0:
                self.end_guessing()

    def stop(self, actor):
        if self.phase != GamePhase.GUESSING:
            raise InvalidGameState(
                "The guessing phase can only be stopped when it is in progress.")
        elif actor.team not in {self.active_team, Team.GRAY}:
            raise InvalidGameState(f"{actor} can't stop the {self.active_team}'s guessing phase.")
        elif self.teams[actor.team].spymaster == actor:
            raise InvalidGameState("Spymasters are not permitted to stop the guessing phase.")

        self.end_guessing()

    def end_guessing(self):
        assert self.phase == GamePhase.GUESSING

        if self.check_win():
            return

        self.phase = GamePhase.HINTING
        self.active_team = ~self.active_team

        self.notify_phase()

    def check_win(self):
        for team in {Team.GREEN, Team.PINK}:
            if not self.remaining_words[team]:
                self.phase = GamePhase.POST_GAME
                self.winner = team

                self.notify_phase()
                return True

        return False
