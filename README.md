# CS3383 Non-Deterministic Finite Automata

This project contains a Python implementation of a non-deterministic finite automata (NFA), created by:
- Andrew Else 
- Cole Daniel 
- Logan Austill 
- Muhammad Munir Leghari 

## Usage

To run the program, clone the repository and navigate to the installed directory. The project requires Python 3.x to run.

On the command line, run the program with `python main.py`. You will be prompted for a relative file path for the file containing your tuple representation of the NFA.

Once provided, the program will enter one of two states, based on whether or not you provided a list of input strings (beta) in the file:
1. If beta was provided, it will run through each given input string and return a tuple containing `accepted` or `rejected`. Example:
```
Please input the file name: tests/regular_1.txt
(accepted, accepted, rejected)
```
2. If beta was not provided, you will be prompted for an input string, and the program will respond with `Accepted.` or `Rejected.`, accordingly. To quit, enter a blank response. Example:
```
Please input the file name: tests/regular_1.txt
Please input a string: 1101
Accepted.
Please input a string: 0001
Accepted.
Please input a string: 1110
Rejected.
Please input a string:
Bye bye.
```

## Implementation

The NFA system was implemented using Python 3.13 with the following IDEs:
- Python IDLE
- Visual Studio Code