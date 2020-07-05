from pyrcb2 import Event, IRCBot

from .interface import Interface
from .state import UNLIMITED, Game, GamePhase, InvalidGameState, Team

PREFIX = "-"
TEAM_MAP = {
    "g": Team.GREEN,
    "green": Team.GREEN,
    "p": Team.PINK,
    "pink": Team.PINK,
    "gray": Team.GRAY,
    "grey": Team.GRAY,
    "none": None
}


def command(names, only_during_game=False, only_for_joined=False):

    def wrapper(f):
        f._is_command = True
        f._command_names = names
        f._during_game = only_during_game
        f._only_for_joined = only_for_joined
        return f

    return wrapper


class IRCInterface(Interface):

    def __init__(self, nick, channel):
        self.bot = IRCBot(log_communication=True)
        self.bot.load_events(self)

        self.commands = dict()
        self.load_commands()

        self.nick = nick
        self.channel = channel
        self.game = Game(interface=self)

    def load_commands(self):
        for thing in dir(self):
            thing = getattr(self, thing)
            if not getattr(thing, "_is_command", False):
                continue

            for name in thing._command_names:
                self.commands[name] = thing

    def start(self):
        self.bot.call_coroutine(self.start_async())

    async def start_async(self):
        await self.bot.connect("chat.freenode.net", 6697, ssl=True)
        await self.bot.register(self.nick)
        await self.bot.join(self.channel)
        await self.bot.listen()

    @Event.privmsg
    def on_privmsg(self, sender, channel, message):
        if channel is None:
            # ignore PMs
            return

        message = message.strip()
        if not message.startswith(PREFIX):
            # ignore non-commands
            return

        command_and_args = message[1:].lower().split()
        command, args = command_and_args[0], command_and_args[1:]

        try:
            self.handle_command(sender, command, args)
        except InvalidGameState as e:
            self.tell(str(e))

    @Event.nick
    def on_nick(self, sender, new_nick):
        if sender in self.game.players:
            self.game.players[sender].rename(new_nick)

    def handle_command(self, actor, command, args):
        if command not in self.commands:
            return

        command = self.commands[command]
        if command._during_game:
            if self.game.phase == GamePhase.PRE_GAME:
                self.tell("Sorry, this command only works during a game.")
                return

        if command._during_game or command._only_for_joined:
            actor = self.game.players.get(actor)
            if actor is None:
                self.tell("Sorry, you need to be in the game to do that.")
                return

        command(actor, args)

    @command({"j", "join", "jonge", "jord"})
    def command_join(self, actor, args):
        if args:
            team_pref = TEAM_MAP.get(args[0].lower())
        else:
            team_pref = None

        self.game.join(actor, team_pref)

    @command({"l", "leave"})
    def command_leave(self, actor, args):
        self.game.leave(actor)

    @command({"t", "team"}, only_for_joined=True)
    def command_team_pref(self, actor, args):
        if not args:
            raise InvalidGameState("You need to specify a team preference (green, pink, gray).")

        if self.game.phase is not GamePhase.PRE_GAME:
            raise InvalidGameState("You can only specify a team preference before the game.")

        team_pref = TEAM_MAP.get(args[0].lower())
        if not team_pref:
            raise InvalidGameState("Invalid team preference.")

        actor.team = team_pref
        if team_pref is not None:
            self.tell(f"{actor} wants to be on the {team_pref} team.")
        else:
            self.tell(f"{actor} has no team preference.")

    @command({"spymaster"}, only_for_joined=True)
    def command_spymaster_pref(self, actor, args):
        if self.game.phase is not GamePhase.PRE_GAME:
            raise InvalidGameState("You can only specify a spymaster preference before the game.")

        actor.toggle_spymaster_preference()
        pref = "wants" if actor.spymaster_preference else "does not want"

        self.tell(f"{actor} {pref} to be a spymaster.")

    @command({"start"})
    def command_start(self, actor, args):
        self.game.start_game()

    @command({"endgame"})
    def command_force_endgame(self, actor, args):
        self.tell(f"{actor} is forcing the game to end immediately.")
        self.tell(self.full_words_view())
        self.game = Game(interface=self)

    @command({"c", "clue", "h", "hint"}, only_during_game=True)
    def command_hint(self, actor, args):
        if len(args) != 2:
            raise InvalidGameState("Invalid syntax. !c takes two arguments, a word and a number.")

        if not args[1].isnumeric():
            if args[1] in {"unlimited", "infinity", "infty", "inf"}:
                args[1] = UNLIMITED
            else:
                raise InvalidGameState("Invalid syntax. Number must be numeric or 'unlimited'")
        else:
            args[1] = int(args[1])

        self.game.hint(actor, args[0], args[1])

    @command({"g", "guess"}, only_during_game=True)
    def command_guess(self, actor, args):
        if len(args) == 0:
            raise InvalidGameState("Invalid syntax. Specify a word you want to guess.")

        word = " ".join(args)
        self.game.guess(actor, word)

    @command({"s", "stop"}, only_during_game=True)
    def command_stop(self, actor, args):
        self.game.stop(actor)

    @command({"stats", "status"})
    def command_stats(self, actor, args):
        if self.game.phase in {GamePhase.GUESSING, GamePhase.HINTING}:
            self.notify_teams()
            action = ("guess" if self.game.phase == GamePhase.GUESSING else
                      "hint" if self.game.phase == GamePhase.HINTING else "???")

            self.tell(f"It's {self.game.active_team}'s turn to {action}.")

        elif self.game.phase == GamePhase.PRE_GAME:
            n = len(self.game.players)
            players = ", ".join(p.name for p in self.game.players)

            self.tell(f"{n} players: {players}. The game hasn't started yet.")

    @command({"w", "words"}, only_during_game=True)
    def command_words(self, actor, args):
        remaining = ", ".join(self.game.all_words)

        greens = ", ".join(self.game.guessed_words[Team.GREEN])
        pinks = ", ".join(self.game.guessed_words[Team.PINK])
        civilians = ", ".join(self.game.guessed_words[Team.GRAY])

        self.tell(f"Green: {greens} | Pink: {pinks} | Civilians: {civilians}")
        self.tell(f"Remaining words: {remaining}.")

        if actor in {self.game.teams[Team.GREEN].spymaster, self.game.teams[Team.PINK].spymaster}:
            self.tell_private(actor, self.spymaster_view())

    def notify_winner(self):
        super().notify_winner()
        self.game = Game(interface=self)

    def tell(self, message):
        self.bot.privmsg(self.channel, message)

    def tell_private(self, player, message):
        self.bot.privmsg(player.name, message)


def run_bot(nick, channel):
    bot = IRCInterface(nick, channel)
    bot.start()
