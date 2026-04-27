
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
    
    def epsilonClosure(self, stateSet: set[str]) -> set[str]:
        """
        Pushes all states connected to current state by epsilon transitions
        onto a stack to track all available next states from current state
        """
        
        # Closure set to store all available states
        # Stack list to store current states available to trace through transitions
        closure = set(stateSet)
        stack = list(stateSet)
            
        # While the stack is not empty, we trace through all available states
        # Start by popping top of stack into currentState variable
        while stack:
            currentState = stack.pop()
            
            # Grabbing each symbol and state pairs for currentState
            for transition in self.transitionsByState[currentState]:
                symbol = transition[1]
                nextState = transition[2]
                
                # If epsilon transition is found and nextState is not in closure set
                # Add nextState to closure set and stack list
                if symbol == "ε" and nextState not in closure:
                    closure.add(nextState)
                    stack.append(nextState)
                            
        # Return closure set full of all available states from current state
        # Across an epsilon transition
        return closure

    def tryAccept(self, inputString: str) -> bool:
        """
        Attempt to accept an input string with the NFA\n
        Returns `True` if accepted, `False` if rejected
        """

        # print("\nTESTING STRING: ", inputString)

        # Begin by closing epsilon transitions for the start state
        currentStates = self.epsilonClosure({self.start})
        
        for char in inputString:
            nextStates = set()
            
            # Move on the current character
            for state in currentStates:
                for transition in self.transitionsByState[state]:
                    symbol = transition[1]
                    destination = transition[2]
                    
                    if symbol == char:
                        nextStates.add(destination)
            
            # Expand through epsilon transitions
            currentStates = self.epsilonClosure(nextStates)

        # Accept if ANY current state is an end state
        return any(state in self.endStates for state in currentStates)

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
