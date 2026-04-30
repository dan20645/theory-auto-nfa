"""
    Python implementation of non-deterministic
    finite automata (NFA). NFAs are read from
    text files and instantiated into objects.

    Created by Group 9 in the Spring 2026 CS
    3383-002 class:
    - Andrew Else
    - Cole Daniel
    - Logan Austill
    - Muhammad Munir Leghari
    
    April 2026
"""

class NFA:
    """
    Represents a non-deterministic finite automata\n
    Takes in a list (tuple) parsed from the given format from the professor
    """
    def __init__(self, nfaTuple: list) -> 'NFA':
        """
        Instantiate the NFA
        """
        
        # Extract info from nfa 
        self.alphabet     : list = nfaTuple[0]
        self.states       : list = nfaTuple[1]
        # Current state tracked in tryAccept()
        self.start        : str  = nfaTuple[2]
        self.endStates    : list = nfaTuple[3]
        self.transitions  : list = nfaTuple[4]

        self.transitionsByState: dict[str, list] = {}
        
        # Initialize lists per state
        for state in self.states:
            self.transitionsByState[state] = []
        
        # Append relevant transitions per state
        for transition in self.transitions:
            state = transition[0]
            self.transitionsByState[state].append(transition)

    def from_file(path: str) -> tuple['NFA', list]:
        # Read content from file
        try:
            fileRef = open(path, "r", encoding="utf-8")
            fileCon = fileRef.read()
        except:
            print("Invalid file: ", path)
            exit(1)
        
        # Parse content to list
        # parsedTuple[0] -> the NFA
        # parsedTuple[1] -> the strings
        parsedTuple: list = NFA.parseTuple(fileCon)
        return NFA(parsedTuple[0]), parsedTuple[1]

    # Parse a file that contains nested tuples
    def parseTuple(tupleString: str) -> list:
        result = []

        # Clean input
        tupleString = tupleString.replace("\n", "")
        tupleString = tupleString.replace(" ", "")

        if (tupleString[0] != "("):
            print("Tuple string must begin with '('")
            exit(1)

        tupleIsClosed = False
        index = 0
        charIndex = 1

        while (not tupleIsClosed):
            # Get a character from the tuple string and match
            nextChar = tupleString[charIndex]

            match nextChar:
                case "(": 
                    # Entering a nested tuple
                    # We run through it and get the index of where it ends
                    nestedTupleEndIndex = 0
                    depth = 0

                    # Recurse until this tuple is done
                    for i in range(charIndex, len(tupleString)):
                        if tupleString[i] == "(":
                            depth += 1
                        elif tupleString[i] == ")":
                            depth -= 1
                            if (depth == 0):
                                nestedTupleEndIndex = i
                                break

                    # Parse the inside tuple based on index, and append
                    result.append(NFA.parseTuple(
                        tupleString[charIndex:nestedTupleEndIndex + 1]
                    ))
                    charIndex = nestedTupleEndIndex

                case ",":
                    index += 1

                case ")":
                    tupleIsClosed = True

                case _:
                    if (index >= len(result)):
                        result.append("")
                    result[index] += nextChar

            charIndex += 1

        return result

    def tryAccept(self, inputString: str) -> bool:
        """
        Attempt to accept an input string with the NFA\n
        Returns `True` if accepted, `False` if rejected
        """

        # print("\nTESTING STRING: ", inputString)

        # VARIABLES

        accepted = False
        charIndex = 0
        alternatePathsStack = []
        currentState = self.start
        statesSinceEpsilon = []
        validTransitions = []

        # HELPERS

        # Determine whether the current state is accepted or not
        def isAccepted():
            nonlocal charIndex, inputString, currentState, self
            # print(f"Checking acceptance at: ({currentState}, {inputString[charIndex:]})")
            # print(f"\tAvailable transitions:")
            # for transition in self.transitionsByState[currentState]:
            #     print(f"\t\t{transition}")
            # print("\n")
            return (charIndex == len(inputString) and currentState in self.endStates)

        # Get a list of transitions originating at `state` whose
        # transition character is `char`.
        def getTransitionsWithChar(state, char):
            result = []
            for transition in self.transitionsByState[state]:
                isUseless = (char == "ε" and transition[0] == transition[2])
                if (transition[1] == char and not isUseless):
                    result.append(transition)
            return result
        
        # Carries out the given transition. Returns True
        # if the resulting node has already been visited
        # since the last time a non-epsilon was completed
        def doTransition(transition):
            nonlocal accepted, charIndex, currentState, statesSinceEpsilon
            
            isEpsilonLoop = False
            currentState = transition[2]
            if transition[1] == "ε":
                statesSinceEpsilon.append(transition[0])
                if chosenTransition[2] in statesSinceEpsilon:
                    isEpsilonLoop = True
            else:
                statesSinceEpsilon.clear()
                charIndex += 1
            accepted = isAccepted()
            
            return isEpsilonLoop

        # Back up and choose a different path to follow, 
        # in case the prior was not accepted
        def backtrack():
            nonlocal accepted, charIndex, currentState
            path = alternatePathsStack.pop()
            transition = path[0]
            currentState = transition[0]
            charIndex = path[1]
            statesSinceEpsilon = path[2]
            
            isEpsilonLoop = doTransition(transition)
            if isEpsilonLoop and not accepted and len(alternatePathsStack) > 0:
                backtrack()

        # LOGIC

        # Set initial accepted state, useful for the special
        # case where the start state is accepting and
        # inputString is empty
        accepted = isAccepted()

        # Loop through all the paths until we have 
        # an accepted configuration or are out of paths
        while (not accepted):
            # Get epsilon transitions for current state
            validTransitions = getTransitionsWithChar(currentState, "ε")

            # Get nextChar and valid transitions for currentState + nextChar
            nextChar = ""
            if charIndex < len(inputString):
                nextChar = inputString[charIndex]
                validTransitions += getTransitionsWithChar(currentState, nextChar)
            numValidTransitions = len(validTransitions)

            # Transitions? Choose one and put the rest back
            if (numValidTransitions > 0):

                chosenTransition = None

                # Choose first non-ε transition, or ε transition if it is all we have
                chosenTransitionIndex = -1
                for i in range(numValidTransitions):
                    transition = validTransitions[i]
                    if transition[1] != "ε":
                        chosenTransitionIndex = i
                        break
                if chosenTransitionIndex == -1: chosenTransitionIndex = 0
                
                chosenTransition = validTransitions[chosenTransitionIndex]

                # print(f"Chosen transition: ({chosenTransition[0]}, {chosenTransition[1], {chosenTransition[2]}})")

                # Save remaining transitions on alternate paths stack
                for i in range(numValidTransitions):
                    if i != chosenTransitionIndex:
                        alternatePathsStack.append(
                            (validTransitions[i], charIndex, statesSinceEpsilon.copy())
                        )

                # Carry out chosen transition, backtracking if we have
                # completed an epsilon loop
                isEpsilonLoop = doTransition(chosenTransition)
                if isEpsilonLoop and len(alternatePathsStack) > 0:
                    backtrack()
                    continue
                
            # No transitions? Go back to another path
            elif (len(alternatePathsStack) > 0):
                backtrack()

            # No valid transitions and stack empty despite characters remaining
            else:
                break

        return accepted

# ===
# UTILITY FUNCTIONS
# ===

"""
    Parses an input string into a format suitable
    to be fed to an NFA.
    This currently returns an empty string if the
    input string == "ε", otherwise it returns the
    unmodified input string.
"""
def parseString(s: str):
    result = s
    if (s == "ε"):
        result = ""
    return result

# ====
# MAIN
# ====

def main():
    # Get file path as user input and open file
    fileName : str = input("Please input the file name: ")

    # Parse file contents into NFA and input tuples separately
    nfa, beta = NFA.from_file(fileName)

    # If there is no string in `beta`, prompt user for string
    if (len(beta) == 0):
        while True:
            inputString = input("Please input a string: ")
            if (inputString == ""): break
            parsedString = parseString(inputString)
            match nfa.tryAccept(parsedString):
                case True:
                    print("Accepted.")
                case False:
                    print("Rejected.")
        print("Bye bye.")
        
    # If there is strings in `beta`, go through automatically
    else:
        results = []
        for inputString in beta:
            parsedString = parseString(inputString)
            match nfa.tryAccept(parsedString):
                case True:
                    results.append("accepted")
                case False:
                    results.append("rejected")
        print("(" + ", ".join(results) + ")")

if __name__ == "__main__":
    main()