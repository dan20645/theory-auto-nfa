
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
        fileRef = open(path, "r", encoding="utf-8")
        fileCon = fileRef.read()
        
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

        # Back up and choose a different path to follow, 
        # in case the prior was not accepted
        def backtrack():
            nonlocal accepted, charIndex, currentState
            path = alternatePathsStack.pop()
            currentState = path[0]
            charIndex = path[1]
            accepted = isAccepted()

        # LOGIC

        # Loop through all the paths until we have 
        # an accepted configuration or are out of paths
        while (not accepted and (charIndex < len(inputString) or len(alternatePathsStack) > 0)):
            
            if (charIndex >= len(inputString)):
                # path exhausted, go back
                backtrack()
                continue

            nextChar = inputString[charIndex]

            # Get valid transitions for currentState + nextChar
            validTransitions = []
            for transition in self.transitionsByState[currentState]:
                if (transition[1] == nextChar or transition[1] == "ε"):
                    validTransitions.append(transition)
            numValidTransitions = len(validTransitions)

            #  Transitions? Choose one and put the rest back
            if (numValidTransitions > 0):

                chosenTransition = None

                # Carry out first non-ε transition, or ε transition if it is all we have
                for transition in validTransitions:
                    if transition[1] != "ε":
                        chosenTransition = transition
                        break
                if chosenTransition == None: chosenTransition = validTransitions[0]

                # print(f"Chosen transition: ({chosenTransition[0]}, {chosenTransition[1], {chosenTransition[2]}})")

                currentState = chosenTransition[2]
                if chosenTransition[1] != "ε":
                    charIndex += 1
                accepted = isAccepted()

                # Save remaining transitions on alternate paths stack
                for i in range(1, numValidTransitions):
                    alternatePathsStack.append(
                        (validTransitions[i][2], charIndex)
                    )
                
            # No transitions? Go back to another path
            elif (len(alternatePathsStack) > 0):
                backtrack()

            # No valid transitions despite characters remaining
            else:
                charIndex = len(inputString)

        return accepted

# ====
# MAIN
# ====

def manual():
    # Get file path as user input and open file
    fileName : str = input("Please input the file name: ")

    # Parse file contents into NFA and input tuples separately
    nfa, beta = NFA.from_file(fileName)

    # If there is no string in `beta`, prompt user for string
    if (len(beta) == 0):
        while True:
            inputString = input("Please input a string: ")
            if (inputString == ""): break
            match nfa.tryAccept(inputString):
                case True:
                    print("Accepted.")
                case False:
                    print("Rejected.")
        print("Bye bye.")
        
    # If there is strings in `beta`, go through automatically
    else:
        results = []
        for inputString in beta:
            match nfa.tryAccept(inputString):
                case True:
                    results.append("accepted")
                case False:
                    results.append("rejected")
        print("(" + ", ".join(results) + ")")

def run_tests():
    testList = open("TESTS.txt", "r").readlines()
    for line in testList:
        if line != "" and line != "\n":
            testNameResult = line.split(":")
            print(f"TEST {testNameResult[0]}:")
            nfa, beta = NFA.from_file(f"tests\\{testNameResult[0]}")
            results = []
            for inputString in beta:
                match nfa.tryAccept(inputString):
                    case True:
                        results.append("accepted")
                    case False:
                        results.append("rejected")
            strResult = "(" + ", ".join(results) + ")"
            if strResult == testNameResult[1][:-1]:
                print("\tTEST PASSED\n")
            else:
                print(f"\tTEST FAILED:\n\t\t{strResult}\n\t\t{testNameResult[1]}\n")

if __name__ == "__main__":
    print("""
1. Run automated tests
2. Run manually
(anything else). Exit

TODO: delete this intro before turning in      
    """)
    userIn = input("> ")
    match userIn:
        case "1":
            run_tests()
        case "2":
            manual()
        case _:
            pass