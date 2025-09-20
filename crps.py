#! /usr/bin/env python


# Players.
PLAYER1 = 1
PLAYER2 = 2


# Choices.
ROCK = 3
PAPER = 4
SCISSORS = 5


# Outcomes.
WIN = 6
LOSE = 7
DRAW = 8


# All possible game states.
GAME_STATES = {
    (ROCK, PAPER) : LOSE,
    (ROCK, SCISSORS) : WIN,
    (ROCK, ROCK) : DRAW,
    (PAPER, SCISSORS) : LOSE,
    (PAPER, ROCK) : WIN,
    (PAPER, PAPER) : DRAW,
    (SCISSORS, ROCK) : LOSE,
    (SCISSORS, PAPER) : WIN,
    (SCISSORS, SCISSORS) : DRAW
}


class Player:
    """ Base class for a player of the game. """
    def __init__(self, name):
        self.name = name
        self.history = []


    def pick(self):
        """Return one of the three choices: ROCK, PAPER, SCISSORS."""
        raise NotImplementedError()


    def record(self, game_details):
        """Record the details of the round."""
        self.history.append(game_details)


class AlwaysRockPlayer(Player):
    """ Player who always chooses ROCK. """
    def pick(self):
        return ROCK


class RandomPlayer(Player):
    """ Player who always makes a random choice. """
    def pick(self):
        import random
        random.seed()
        return random.randint(ROCK, SCISSORS)


class RandomHistoryPlayer(Player):
    """ Player who picks at random from historical options of their opponent. """
    BEATEN_BY = {
        ROCK: PAPER,
        PAPER: SCISSORS,
        SCISSORS: ROCK
    }


    def pick(self):
        import random
        random.seed()
        total_rounds = len(self.history)
        if total_rounds == 0:    
            choice = random.randint(ROCK, SCISSORS)
        else:
            idx = random.randint(0, len(self.history) - 1)
            opponents_choice = self.history[idx][1]
            choice = self.__class__.BEATEN_BY[opponents_choice]
        return choice


class WeightedHistoryPlayer(Player):
    """ Computer player that linearly weights the past opponents choices. """
    BEATEN_BY = {
        ROCK: PAPER,
        PAPER: SCISSORS,
        SCISSORS: ROCK
    }


    def pick(self):
        import random
        random.seed()
        total_rounds = len(self.history)
        if total_rounds == 0:
            choice = random.randint(ROCK, SCISSORS)
        else:
            weighted_outcomes = [(i / total_rounds, o) for i, o in enumerate(self.history)]
            totals = { ROCK: 0, PAPER: 0, SCISSORS: 0 }
            totals[ROCK] = sum([w for (w,o) in weighted_outcomes if o[1] == ROCK])
            totals[PAPER] = sum([w for (w,o) in weighted_outcomes if o[1] == PAPER])
            totals[SCISSORS] = sum([w for (w,o) in weighted_outcomes if o[1] == SCISSORS])
            opponents_choice = max(totals, key=totals.get)
            choice = self.__class__.BEATEN_BY[opponents_choice]
        return choice


class TrigramPlayer(Player):
    """ Computer player that uses trigrams to look for patterns in the opponents choices. """
    BEATEN_BY = {
        ROCK: PAPER,
        PAPER: SCISSORS,
        SCISSORS: ROCK
    }


    def __init__(self, id):
        super().__init__(id)
        self.trigrams = {}


    def pick(self):
        import random
        random.seed()
        total_rounds = len(self.history)
        if total_rounds < 4:
            choice = random.randint(ROCK, SCISSORS)
        else:
            sequence = [x[1] for x in self.history]
            current_trigram = tuple(sequence[-4:-1])
            previous_choices = self.trigrams.get(current_trigram, [])
            if len(previous_choices) > 1:
                idx = random.randint(0, len(previous_choices) - 1)
                choice = previous_choices[idx]
            else:
                choice = previous_choices[0]
        return self.BEATEN_BY[choice]


    def record(self, game_details):
        super().record(game_details)
        round_num = len(self.history)
        if round_num > 3:
            sequence = [x[1] for x in self.history]
            trigram = tuple(sequence[-4:-1])
            choice = sequence[-1]
            targets = self.trigrams.get(trigram, [])
            targets.append(choice)
            self.trigrams[trigram] = targets


class HumanPlayer(Player):
    """ Human player at a keyboard. """
    CHAR_2_INT = { "r": ROCK, "p": PAPER, "s": SCISSORS }


    def pick(self):
        choice = ""
        while choice not in ['r', 'p', 's']:
            choice = input("(r)ock, (p)aper, or (s)cissors? ")
        return self.__class__.CHAR_2_INT[choice]


def play_round(p1, p2):
    """ Play one round of the game with the two supplied players. """
    p1_choice = p1.pick()
    p2_choice = p2.pick()
    p1_outcome = GAME_STATES[(p1_choice, p2_choice)]
    p2_outcome = GAME_STATES[(p2_choice, p1_choice)]
    p1.record((p1_choice, p2_choice, p1_outcome))
    p2.record((p2_choice, p1_choice, p2_outcome))
    winner = 0
    if p1_outcome == WIN:
        winner = PLAYER1
    elif p2_outcome == WIN:
        winner = PLAYER2
    return winner


def play_game(p1, p2, rounds=100):
    """ Play several rounds of the game, reporting statistics at the end. """
    print(f"{p1.name} vs {p2.name}")
    results = []
    for i in range(rounds):
        results.append(play_round(p1, p2))
        print(".", end="")
    p1_total = len([x for x in results if x == PLAYER1])
    p2_total = len([x for x in results if x == PLAYER2])
    no_total = len([x for x in results if x == 0])
    total = float(len(results))
    print("")
    print(f"{p1.name}: {(p1_total / total) * 100}%")
    print(f"{p2.name}: {(p2_total / total) * 100}%")
    print(f"Drawn games: {(no_total / total) * 100}%")


if __name__ == "__main__":
    p1 = HumanPlayer("1UP")
    p2 = TrigramPlayer("CPU")
    play_game(p1, p2, 10)
