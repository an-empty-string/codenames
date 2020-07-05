import logging

import pytest
from codenamesbot.state import (UNLIMITED, Game, GameMode, GamePhase, InvalidGameState, Player,
                                Players, PlayingTeam, Team)

logging.basicConfig(level=logging.DEBUG)


def test_player_rename():
    p = Player("tris")
    assert p.name == "tris"

    p.rename("nottris")
    assert p.name == "nottris"


def test_toggle_spymaster_preference():
    p = Player("tris")
    assert not p.spymaster_preference

    p.toggle_spymaster_preference()
    assert p.spymaster_preference

    p.toggle_spymaster_preference()
    p.toggle_spymaster_preference()
    assert p.spymaster_preference


def test_players_track_rename():
    ps = Players()

    tris = ps.add("tris")
    assert ps["tris"] == tris
    assert "tris" in ps

    ps["tris"].rename("nottris")
    assert ps["nottris"] is tris
    assert "tris" not in ps

    claire = ps.add("claire")
    assert tris != claire

    with pytest.raises(KeyError):
        ps["tris"]


def test_players_track_length():
    ps = Players()

    ps.add("tris")
    ps.add("claire")
    ps.add("bob")
    assert len(ps) == 3

    ps.remove("claire")
    assert len(ps) == 2


def test_players_shuffle():
    ps = Players()

    ps.add("tris")
    ps.add("claire")
    ps.add("bob")

    assert len(ps.shuffled()) == 3


def test_players_to_str():
    ps = Players()

    ps.add("tris")
    ps.add("claire")
    ps.add("bob")
    assert str(ps) == "3 players: tris, claire, bob"

    ps.remove("bob")
    ps.remove("tris")
    assert str(ps) == "1 player: claire"


def test_team_opposite():
    assert ~Team.GREEN == Team.PINK
    assert ~Team.PINK == Team.GREEN


def test_playingteam_normal():
    for t in [Team.GREEN, Team.PINK]:
        team = PlayingTeam(t)

        team.add(Player("tris"))
        team.add(Player("claire"))

        assert team.spymaster.name == "tris"
        assert len(team.guessers) == 1
        assert team.guessers[0].name == "claire"

        players = list(team)
        assert players == team.players


def test_playingteam_gray():
    team = PlayingTeam(Team.GRAY)

    team.add(Player("tris"))
    team.add(Player("claire"))

    assert team.spymaster is None
    assert len(team.guessers) == 2


def test_playingteam_length():
    team = PlayingTeam(Team.GRAY)

    team.add(Player("tris"))
    team.add(Player("claire"))

    assert len(team) == 2


def test_playingteam_contains():
    team = PlayingTeam(Team.GRAY)

    tris = Player("tris")
    claire = Player("claire")
    team.add(tris)

    assert tris in team
    assert claire not in team


def test_player_double_join():
    game = Game()
    game.join("tris")

    with pytest.raises(InvalidGameState):
        game.join("tris")


def test_player_double_leave():
    game = Game()

    with pytest.raises(InvalidGameState):
        game.leave("tris")


def test_assign_players_gray_small():
    game = Game()

    tris = game.join("tris")
    claire = game.join("claire")
    bob = game.join("bob")

    bob.team = Team.GREEN
    tris.team = Team.PINK

    game.mode = GameMode.GRAY
    game.assign_teams()

    assert tris.team == Team.PINK
    assert claire.team == Team.GRAY
    assert bob.team == Team.GREEN

    assert game.teams[Team.GREEN].spymaster == bob
    assert not game.teams[Team.GREEN].guessers

    assert game.teams[Team.PINK].spymaster == tris
    assert not game.teams[Team.PINK].guessers

    assert game.teams[Team.GRAY].guessers == [claire]


def test_assign_players_gray_big():
    for _ in range(100):
        game = Game()

        game.join("tris")
        game.join("claire")
        game.join("bob")
        alice = game.join("alice")
        eve = game.join("eve")

        # two players want to be on the green team
        # nobody in particular wants to be on the pink team
        alice.team = Team.GREEN
        eve.team = Team.GREEN

        game.mode = GameMode.GRAY
        game.assign_teams()

        # make sure alice and eve got on different teams, but one of them got on the green team
        green_preferred_resulting_teams = {alice.team, eve.team}
        assert len(green_preferred_resulting_teams) == 2
        assert Team.GREEN in green_preferred_resulting_teams

        # sanity check that
        assert game.teams[Team.GREEN].spymaster in {alice, eve}

        # make sure someone is the pink spymaster
        pink_spymaster = game.teams[Team.PINK].spymaster

        # make sure pink spymaster is not on gray team as well
        assert pink_spymaster.team == Team.PINK
        assert pink_spymaster not in game.teams[Team.GRAY].players

        # make sure gray team has exactly 3 players
        assert len(game.teams[Team.GRAY]) == 3


def test_assign_players_gray_spymaster_preference():
    for _ in range(100):
        game = Game()

        game.join("tris")
        game.join("claire")
        game.join("bob")
        alice = game.join("alice")
        eve = game.join("eve")

        alice.spymaster_preference = True
        eve.spymaster_preference = True

        game.mode = GameMode.GRAY
        game.assign_teams()

        # make sure alice and eve are the spymasters
        assert {game.teams[Team.GREEN].spymaster, game.teams[Team.PINK].spymaster} == {alice, eve}


def test_assign_players_versus_all_team_preference():
    for _ in range(100):
        game = Game()

        tris = game.join("tris")
        claire = game.join("claire")
        bob = game.join("bob")
        alice = game.join("alice")
        eve = game.join("eve")

        tris.team = Team.GREEN
        bob.team = Team.GREEN
        claire.team = Team.PINK
        alice.team = Team.PINK
        eve.team = Team.PINK

        game.mode = GameMode.VERSUS
        game.assign_teams()

        assert tris.team == bob.team == Team.GREEN
        assert claire.team == alice.team == eve.team == Team.PINK


def test_assign_players_versus_two_spymasters():
    for _ in range(100):
        game = Game()

        tris = game.join("tris")
        claire = game.join("claire")
        game.join("bob")
        game.join("alice")
        game.join("eve")

        tris.spymaster_preference = True
        claire.spymaster_preference = True

        game.mode = GameMode.VERSUS
        game.assign_teams()

        spymaster_teams = {tris.team, claire.team}
        assert len(spymaster_teams) == 2


def test_assign_players_versus_team_preference_overrides_spymaster_preference():
    for _ in range(100):
        game = Game()

        tris = game.join("tris")
        claire = game.join("claire")
        game.join("bob")
        game.join("alice")
        game.join("eve")

        tris.spymaster_preference = True
        claire.spymaster_preference = True

        tris.team = Team.GREEN
        claire.team = Team.GREEN

        game.mode = GameMode.VERSUS
        game.assign_teams()

        assert tris.team == claire.team == Team.GREEN


def test_assign_players_versus_balanced_teams():
    for _ in range(100):
        game = Game()

        tris = game.join("tris")
        claire = game.join("claire")
        bob = game.join("bob")
        alice = game.join("alice")

        tris.team = claire.team = bob.team = Team.GREEN

        game.mode = GameMode.VERSUS
        game.assign_teams()

        assert alice.team == Team.PINK
        assert len(game.teams[Team.GREEN]) == 2
        assert len(game.teams[Team.PINK]) == 2


def test_assign_words():
    game = Game()

    game.join("tris")
    game.join("claire")
    game.join("bob")

    game.assign_words()

    assert len(game.words[Team.GREEN]) == 9
    assert len(game.words[Team.PINK]) == 8
    assert len(game.words[Team.GRAY]) == 7
    assert game.assassin is not None


def test_start_game():
    game = Game()

    game.join("tris")
    game.join("claire")
    game.join("bob")

    game.mode = GameMode.GRAY
    game.start_game()

    assert game.teams[Team.GREEN].spymaster is not None
    assert game.teams[Team.PINK].spymaster is not None
    assert len(game.teams[Team.GRAY].guessers) > 0

    assert game.words[Team.GREEN]
    assert game.words[Team.PINK]
    assert game.words[Team.GRAY]
    assert game.assassin is not None


def test_start_game_not_enough_players():
    game = Game()

    game.join("tris")
    game.join("claire")

    with pytest.raises(InvalidGameState):
        game.start_game()


def test_start_game_after_player_leaves():
    game = Game()

    game.join("tris")
    game.join("claire")
    game.join("bob")
    game.leave("bob")

    with pytest.raises(InvalidGameState):
        game.start_game()


def test_midgame_join_forced_gray():
    game = Game()

    game.join("tris")
    game.join("claire")
    game.join("bob")

    game.start_game()

    alice = game.join("alice")
    assert alice.team == Team.GRAY

    eve = game.join("eve", team=Team.GREEN)
    assert eve.team == Team.GRAY


def test_midgame_join_gray_in_versus():
    game = Game()

    game.join("tris")
    game.join("claire")
    game.join("bob")
    game.join("alice")

    game.mode = GameMode.VERSUS
    game.start_game()

    eve = game.join("eve", team=Team.GRAY)
    assert eve.team != Team.GRAY


def test_midgame_join_allowed_to_select_if_balanced():
    for _ in range(100):
        game = Game()

        game.join("tris")
        game.join("claire")
        game.join("bob")
        game.join("alice")

        game.start_game()

        eve = game.join("eve", team=Team.GREEN)
        assert eve.team == Team.GREEN


def test_midgame_join_forced_if_unbalanced():
    for _ in range(100):
        game = Game()

        game.join("tris", team=Team.GREEN)
        game.join("claire", team=Team.GREEN)
        game.join("bob", team=Team.GREEN)
        game.join("alice", team=Team.PINK)
        game.join("charlie", team=Team.PINK)

        game.start_game()

        eve = game.join("eve", team=Team.GREEN)
        assert eve.team == Team.PINK

    for _ in range(100):
        game = Game()

        game.join("tris", team=Team.PINK)
        game.join("claire", team=Team.PINK)
        game.join("bob", team=Team.PINK)
        game.join("alice", team=Team.GREEN)
        game.join("charlie", team=Team.GREEN)

        game.start_game()

        eve = game.join("eve", team=Team.PINK)
        assert eve.team == Team.GREEN


def test_midgame_join_assigned_if_unbalanced():
    game = Game()

    game.join("tris", team=Team.GREEN)
    game.join("claire", team=Team.GREEN)
    game.join("bob", team=Team.GREEN)
    game.join("alice", team=Team.PINK)
    game.join("charlie", team=Team.PINK)

    game.start_game()

    eve = game.join("eve")
    assert eve.team == Team.PINK

    game = Game()

    game.join("tris", team=Team.PINK)
    game.join("claire", team=Team.PINK)
    game.join("bob", team=Team.PINK)
    game.join("alice", team=Team.GREEN)
    game.join("charlie", team=Team.GREEN)

    game.start_game()

    eve = game.join("eve")
    assert eve.team == Team.GREEN


def setup_4p_game():
    game = Game()

    tris = game.join("tris", team=Team.GREEN)
    tris.spymaster_preference = True

    bob = game.join("bob", team=Team.PINK)
    bob.spymaster_preference = True

    game.join("claire", team=Team.GREEN)
    game.join("alice", team=Team.PINK)

    game.start_game()

    return game, tris


def test_hint_normal():
    game, tris = setup_4p_game()

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.GREEN

    game.hint(tris, "foo", 2)

    assert game.phase == GamePhase.GUESSING
    assert game.active_team == Team.GREEN
    assert game.current_hint == ("foo", 2)
    assert game.remaining_guesses == 3


def test_hint_from_disallowed_actors():
    game, tris = setup_4p_game()

    with pytest.raises(InvalidGameState):
        game.hint(game.players["claire"], "foo", 2)

    with pytest.raises(InvalidGameState):
        game.hint(game.players["bob"], "foo", 2)

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.GREEN


def test_hint_with_too_many_words():
    game, tris = setup_4p_game()

    with pytest.raises(InvalidGameState):
        game.hint(tris, "foo", 10)


def test_hint_is_active_word():
    game, tris = setup_4p_game()

    with pytest.raises(InvalidGameState):
        game.hint(tris, game.assassin, 1)


def test_hint_after_hint():
    game, tris = setup_4p_game()

    game.hint(tris, "foo", 1)

    assert game.phase == GamePhase.GUESSING

    with pytest.raises(InvalidGameState):
        game.hint(tris, "quux", 1)


def test_unlimited_hint():
    game, tris = setup_4p_game()

    game.hint(tris, "foo", UNLIMITED)

    assert game.current_hint == ("foo", UNLIMITED)
    assert game.remaining_guesses == UNLIMITED


def test_guess_civilian():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 4)

    word = game.words[Team.GRAY][0]
    game.guess(game.players["claire"], word)

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.PINK
    assert word not in game.all_words
    assert word not in game.remaining_words[Team.GRAY]
    assert word in game.words[Team.GRAY]


def test_guess_opposite_team():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 4)

    word = game.words[Team.PINK][0]
    game.guess(game.players["claire"], word)

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.PINK
    assert word not in game.all_words
    assert word not in game.remaining_words[Team.PINK]
    assert word in game.words[Team.PINK]


def test_guess_same_team():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 4)

    assert game.remaining_guesses == 5

    word = game.words[Team.GREEN][0]
    game.guess(game.players["claire"], word)

    assert game.phase == GamePhase.GUESSING
    assert game.active_team == Team.GREEN
    assert game.remaining_guesses == 4

    assert word not in game.all_words
    assert word not in game.remaining_words[Team.GREEN]
    assert word in game.words[Team.GREEN]

    with pytest.raises(InvalidGameState):
        game.guess(game.players["claire"], word)

    word = game.words[Team.GREEN][1]
    game.guess(game.players["claire"], word)

    assert game.remaining_guesses == 3


def test_guess_assassin():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 4)

    game.guess(game.players["claire"], game.assassin)

    assert game.phase == GamePhase.POST_GAME
    assert game.winner == Team.PINK


def test_running_out_of_guesses():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 1)

    game.guess(game.players["claire"], game.remaining_words[Team.GREEN][0])
    game.guess(game.players["claire"], game.remaining_words[Team.GREEN][0])

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.PINK


def test_stopping_guess_phase_early():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 1)

    game.guess(game.players["claire"], game.remaining_words[Team.GREEN][0])
    game.stop(game.players["claire"])

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.PINK


def test_spymaster_cannot_guess():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 1)

    with pytest.raises(InvalidGameState):
        game.guess(tris, game.remaining_words[Team.GREEN][0])

    assert game.phase == GamePhase.GUESSING
    assert game.active_team == Team.GREEN
    assert game.remaining_guesses == 2
    assert len(game.remaining_words[Team.GREEN]) == 9


def test_spymaster_cannot_stop_guessing():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 1)

    with pytest.raises(InvalidGameState):
        game.stop(tris)

    assert game.phase == GamePhase.GUESSING
    assert game.active_team == Team.GREEN


def test_cannot_guess_during_hint_phase():
    game, tris = setup_4p_game()

    with pytest.raises(InvalidGameState):
        game.guess(game.players["claire"], game.all_words[0])

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.GREEN


def test_cannot_stop_during_hint_phase():
    game, tris = setup_4p_game()

    with pytest.raises(InvalidGameState):
        game.stop(game.players["claire"])

    assert game.phase == GamePhase.HINTING
    assert game.active_team == Team.GREEN


def test_cannot_guess_for_other_team():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 1)

    with pytest.raises(InvalidGameState):
        game.guess(game.players["alice"], game.assassin)

    assert game.phase == GamePhase.GUESSING
    assert game.active_team == Team.GREEN
    assert game.remaining_guesses == 2


def test_cannot_stop_for_other_team():
    game, tris = setup_4p_game()
    game.hint(tris, "foo", 1)

    with pytest.raises(InvalidGameState):
        game.stop(game.players["alice"])

    assert game.phase == GamePhase.GUESSING
    assert game.active_team == Team.GREEN


def test_winning():
    game, tris = setup_4p_game()
    game.hint(tris, "pony", 9)

    for word in game.words[Team.GREEN]:
        game.guess(game.players["claire"], word)

    assert game.phase == GamePhase.POST_GAME
    assert game.winner == Team.GREEN


def test_winning_during_guessing_phase():
    game, tris = setup_4p_game()
    game.hint(tris, "pony", UNLIMITED)

    game.stop(game.players["claire"])
    game.hint(game.players["bob"], "pony", 7)

    for word in game.words[Team.PINK][:-1]:
        game.guess(game.players["alice"], word)

    game.stop(game.players["alice"])
    game.hint(tris, "pony", UNLIMITED)

    game.guess(game.players["claire"], game.remaining_words[Team.PINK][0])

    assert game.phase == GamePhase.POST_GAME
    assert game.winner == Team.PINK


def test_leave_during_game():
    game, tris = setup_4p_game()

    with pytest.raises(InvalidGameState):
        game.leave(tris)


def test_join_after_game():
    # the game state needs to be reset externally before new joins are accepted
    game, tris = setup_4p_game()
    game.hint(tris, "pony", 9)
    game.guess(game.players["claire"], game.assassin)

    assert game.phase == GamePhase.POST_GAME

    with pytest.raises(InvalidGameState):
        game.join("steve")


def test_start_ongoing_game():
    game, _ = setup_4p_game()

    with pytest.raises(InvalidGameState):
        game.start_game()
