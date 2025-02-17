import os
import sys
import json
import time
import random
import argparse
import numpy as np

import importlib
import importlib.util

from glob import glob
from itertools import combinations
from dataclasses import dataclass
from typing import Protocol

parser = argparse.ArgumentParser()

parser.add_argument(
    "-s", "--solution-dir", default = "./solutions",
    help = "dir that holds solution submission scripts"
)

parser.add_argument(
    "--ignore-errors", action = "store_true",
    help = "if set, if a solution raises an error, it will be ignored"
)

parser.add_argument(
    "-p", "--result-path", default = "./results.json",
    help = "the path to save the results JSON file to"
)

parser.add_argument(
    "--no-log", action = "store_true",
    help = "don't log individual match results"
)

parser.add_argument(
    "-i", "--iterations", type = int, default = 20,
    help = "the number of times we will re-run matchups to reduce effects of randomness"
)

args = parser.parse_args()

# Stores a tuple of score deltas, (A, B). Can be indexed via the turns of both players,
# first B, then A.
SCORE_MATRIX = [
    # A defects         # A cooperates
    [ (1, 1),           (0, 5)         ],  # B defects
    [ (5, 0),           (3, 3)         ]   # B cooperates
]

# The maximum amount of time that a move can take, in seconds. If a solution takes
# more than this amount of time to resolve a single move, it is disqualified.
MAX_MOVE_TIME = 20 / 1000 # 20ms

# The number of times that we will re-run the matchups in order to reduce the effects
# of randomness. The greater, the better, but will take longer to compute.
REPEATS: int = args.iterations

class SolutionImpl(Protocol):
    def move(self, self_history: list[bool], opponent_history: list[bool]) -> bool:
        pass

@dataclass
class Solution:
    name: str
    impl: SolutionImpl

@dataclass
class SolutionPlaythrough:
    name: str
    history: list[bool]
    score: int

    def to_json(self):
        return {
            "name": self.name,
            "history": "".join([str(int(x)) for x in self.history])
        }

@dataclass
class Match:
    s1: SolutionPlaythrough
    s2: SolutionPlaythrough

    def to_json(self):
        return self.__dict__

solution_dir: str = args.solution_dir

def load_solution(path: str) -> Solution:
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"ipd_solution_{name}", path)

    module = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)

    if not hasattr(module, "Strategy"):
        print(f"(warn) no 'Strategy' class in file {path}; ignoring")
        del sys.modules[spec.name]
        return None

    return Solution(name = name, impl = module.Strategy)

# Import everything first
strategies: list[Solution] = []
for file in glob("*.py", root_dir = solution_dir):
    try:
        sln = load_solution(os.path.join(solution_dir, file))

        if sln is not None:
            strategies.append(sln)
    except Exception as ex:
        print(f"(warn) could not import solution {file}: {ex}")

        if not args.ignore_errors:
            raise

print(f"(info) {len(strategies)} strategies imported in total.")

# Match them against each other
matches: list[Match] = []
disqualified: list[Solution] = []

for iteration in range(REPEATS):
    if not args.no_log:
        print(f"(info) iteration #{iteration + 1}:")

    for matchup in combinations(strategies, 2):
        s1 = matchup[0]
        s2 = matchup[1]

        if s1 in disqualified or s2 in disqualified:
            continue

        # This formula is taken from Cary Huang's (carykh's) Iterated Prisoner's Dillema
        # implementation. https://github.com/carykh/PrisonersDilemmaTournament
        n = int(200 - 40 * np.log(random.random()))

        s1_history: list[bool] = []
        s2_history: list[bool] = []

        s1_total = 0
        s2_total = 0

        s1_instance: SolutionImpl = s1.impl()
        s2_instance: SolutionImpl = s2.impl()

        match_terminated = False

        def make_move(solution: Solution, instance: SolutionImpl, self_history: list[bool], opponent_history: list[bool]) -> tuple[bool, bool]:
            try:
                time_start = time.perf_counter()
                choice = bool(instance.move(self_history, opponent_history))
                time_end = time.perf_counter()

                if (time_end - time_start) > MAX_MOVE_TIME:
                    print(f"(warn)   {solution.name} disqualified (timed out, took {(time_end - time_start) * 1000:.2f}ms)")
                    disqualified.append(solution)
                    return (None, True)
                
                return (choice, False)

            except Exception as ex:
                print(f"(warn)   {solution.name} disqualified (raised exception, {ex})")
                disqualified.append(solution)

                if not args.ignore_errors:
                    raise

                return (None, True)

        for i in range(n):
            (s1_choice, s1_dq) = make_move(s1, s1_instance, s1_history, s2_history)
            if s1_dq:
                match_terminated = True
                break

            (s2_choice, s2_dq) = make_move(s2, s2_instance, s2_history, s1_history)
            if s2_dq:
                match_terminated = True
                break
            
            s1_history.append(s1_choice)
            s2_history.append(s2_choice)

            deltas = SCORE_MATRIX[s2_choice][s1_choice]
            s1_total += deltas[0]
            s2_total += deltas[1]

        s1_score = (s1_total / n) * 100
        s2_score = (s2_total / n) * 100

        if not match_terminated:
            matches.append(Match(
                SolutionPlaythrough(s1.name, s1_history, s1_score),
                SolutionPlaythrough(s2.name, s2_history, s2_score)
            ))

            if not args.no_log:
                print(f"(info)   {s1.name} (score: {s1_score:.3f}, total: {s1_total}) vs {s2.name} (score {s2_score:.3f}, total {s2_total}), n = {n}")
        else:
            print(f"(warn)   match against {s1.name} and {s2.name} was terminated early")

    if args.no_log:
        print(f"(info) iteration #{iteration + 1} finished")

print()
print("Total scores:")

global_score: int = 0
strat_scores: dict[str, int] = {}

for match in matches:
    if match.s1.name not in strat_scores:
        strat_scores[match.s1.name] = 0
    
    if match.s2.name not in strat_scores:
        strat_scores[match.s2.name] = 0

    strat_scores[match.s1.name] += match.s1.score
    strat_scores[match.s2.name] += match.s2.score

    global_score += match.s1.score + match.s2.score

strat_scores = dict(sorted(strat_scores.items(), key=lambda x: x[1], reverse=True))

leaderboard: dict[str, float] = {}
for (i, (name, score)) in enumerate(strat_scores.items()):
    leaderboard[name] = score / (len(strategies) * REPEATS)
    print(f"  #{(i + 1):<3}  {name}: {leaderboard[name]:.3f} ({score / REPEATS:.3f} total)")

# Serialize everything into JSON
unique_matches: list[Match] = []
for match in matches:
    if any(x.s1.name == match.s1.name and x.s2.name == match.s2.name for x in unique_matches):
        continue

    unique_matches.append(match)

# https://stackoverflow.com/a/38764817
def _default(self, obj):
    return getattr(obj.__class__, "to_json", _default.default)(obj)

_default.default = json.JSONEncoder().default
json.JSONEncoder.default = _default

with open(args.result_path, "w") as file:
    json.dump({
        "leaderboard": leaderboard,
        "matches": unique_matches
    }, file, separators=(',', ':'))

print()
print(f"✅ Results written to {args.result_path}! You can view them with src/viewer/index.html.")