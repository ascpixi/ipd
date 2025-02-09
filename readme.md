# Hack Club Iterated Prisoner's Dillema (IPD) runner
This repository contains a collection of scripts to run Iterated Prisoner's Dillema competitions.

## ✨ Setup
Run the following commands in a terminal **once** in order to get yourself started. Make sure to run them from the directory where you cloned the repository!

```sh
python3 -m pip install -r requirements.txt
```

> [!NOTE]
> On Windows, and on certain other platforms, you may need to use `python` instead of `python3`.

> [!IMPORTANT]
> If you're getting an error about a **externally managed environment**, you need to run the script from a *virtual environment*. Click [here](#-setup-with-a-virtual-environment) for instructions.

## 🏆 Usage
When you're done with the setup, you can make all strategies in the `solutions` directory battle against each other:

```sh
# You might need to use "python" on Windows.
python3 ./src/run.py
```

This will create a `results.json` file in the directory you're currently in. In order to view it, open the `index.html` file in `src/viewer`, or, alternatively, simply [click here](https://ascpixi.dev/ipd).

You can also view all available flags with `--help`. Some of the more interesting ones include:
- `-s`/`--solution-dir`: the directory to read solution scripts from. **(Default: `./solutions`)**
- `--no-log`: don't log individual match results - useful with a high number of `--iterations`
- `-i`/`--iterations`: the number of times we will re-run matchups to reduce effects of randomness. A higher number will yield a more accurate result at the cost of increased execution time. **(Default: 20)**

> [!WARNING]
> When running solutions from foreign sources, *always* verify that they're safe beforehand. This only concerns tournament organizers.

## 🧑‍💻 Writing strategies
A template for a strategy is as follows:

```py
class Strategy:
    def __init__(self):
        # Initialize memory fields here. This method is optional, and if you
        # don't need memory/state, you can omit it!
        self.example = True

    def move(self, self_history: list[bool], opponent_history: list[bool]):
        # Return "True" to cooperate, and "False" to defect.
        #     - self_history is the history of the moves of this strategy.
        #     - opponent_history is the history of the moves of the opponent.
        #     Both lists are guaranteed to be of equal length.
        return True
```

The `run.py` script runs strategies from `solutions` by default. Name your file something sensible (only alphanumeric characters and underscores), and drop it into that folder in order to run it alongside the default solutions.

The default solutions also serve as examples - go take a look at some of them to get a gist of how to make one yourself!

## ✨ Setup with a virtual environment
Running the script from a virtual environment is recommended, but requires some more setup. Run the following commands to get yourself started:

```sh
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

On Windows, use these commands instead:
```sh
python -m venv .venv
.venv\Scripts\activate
python -m pip install -r requirements.txt
```
