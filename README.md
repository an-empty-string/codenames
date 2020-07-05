# Codenames bot

This is an IRC bot for running the game Codenames.

## Pre-game commands

- Use `-j`, `-join`, `-jord`, `-jonge` to join the game.
    - If you are joining mid-game, you can specify a team you want to join like this: `-j green`.
    - The bot will try to respect your team preference but might put you on another team for balance.
- Use `-l`, `-leave` to leave the game before it starts.
- Use `-spymaster` to toggle your preference for being the spymaster.
- Use `-team green`, `-team pink`, `-team gray`, or `-team none` to specify your team preference.
    - Green and Pink can be abbreviated as `g` and `p`.
- Use `-stats` to see who is joined.
- Use `-start` to start the game.

## In-game commands

- As the spymaster, use `-c`, `-clue`, `-h`, `-hint` to enter a clue.
    - Takes the word you want to hint and a number as arguments: `-c pony 9`.
    - You may specify `0` or `unlimited` as the number.
- As a guesser, use `-g`, `-guess` to guess a word.
- As a guesser, use `-s`, `-stop` to stop guessing.
- Use `-stats` to see who is playing and what teams they are on.
- Use `-w`, `-words` to see the word list.
    - As a spymaster, this will send the word list to you in PM.
- Use `-endgame` to forcibly end the game, for example if someone has to leave.
