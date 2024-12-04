import re   # for using regular expression
import sys  # for terminating the program when error happens

''' 1- Lexical analysis: is the first phase of a compiler. 
    Its main job is to read the input source code and convert it into meaningful
    units called tokens. This is done by a component of the compiler or interpreter
    known as the lexer or lexical analyzer.The result will be a stream of tokens 
    for each line of the code. 

    2- Parsing: Once the lexical analysis is complete, the next stage is parsing. 
    The parser takes the stream of tokens produced by the lexer and builds a data
    structure known as a parse tree or syntax tree. This tree represents the 
    grammatical structure of the program.
'''

class Interpreter:

    # Class attribute for token specifications accessible to all instances
    TOKEN_SPECIFICATION = (
        ('PRINT_VAR',   r'\bPRINT\s+[a-zA-Z_][a-zA-Z_0-9]*\b'),         # Print statement
        ('INT_VAR',     r'[a-zA-Z_][a-zA-Z_0-9]*\s'),                   # Integer variable (lookahead for assignment and operations)
        ('STR_VAR',     r'[a-zA-Z_][a-zA-Z_0-9]*\s'),                   # String variable (lookahead for assignment and addition)
        ('ASSIGN',      r'(?<=\s)\=(?=\s)'),                            # Assignment operator
        ('PLUS_ASSIGN', r'(?<=\s)\+=(?=\s)'),                           # Addition assignment operator
        ('MINUS_ASSIGN',r'(?<=\s)-=(?=\s)'),                            # Subtraction assignment operator
        ('MULT_ASSIGN', r'(?<=\s)\*=(?=\s)'),                           # Multiplication assignment operator
        ('DIV_ASSIGN', r'(?<=\s)\\=(?=\s)'),                           # Division assignment operator
        ('INT_VAR_VAL', r'(?<=[\+\-\*]=)\s[a-zA-Z_][a-zA-Z_0-9]*'),     # Integer variable (lookahead for operations)
        ('STR_VAR_VAL', r'(?<=\+=)\s[a-zA-Z_][a-zA-Z_0-9]*'),           # String variable (lookahead for addition)
        ('ASS_VAL', r'(?<=\=)\s[a-zA-Z_][a-zA-Z_0-9]*'),                # variable (lookahead for assignment)
        ('NUMBER',      r'(?<=\s)-?\d+(?=\s)'),                         # Integer literal
        ('STRING',      r'"[^"]*"'),                                    # String literal, handling quotes
        ('SEMICOLON',   r'(?<=\s);'),                                   # Statement terminator
        ('WS',          r'\s+'),                                        # Whitespace
        ('NEWLN',       r'\n')
    )

    def __init__(self, file_name):
        self.file_name = file_name
        self.variables = {}
        self.line_number = 0

    def lexical_analysis(self, line):
        """
        This function uses regular expression for tokenizing. 
        There are other tools and algorithms for tokenizing such as:
        1- tool: FLexer Generators (e.g., Lex, Flex)
        2- Maximal Munch (or Longest Match) Principle
        """
        tokens = []

        # looping through all patterns
        for tok_type, tok_regex in self.TOKEN_SPECIFICATION:
            # compiling a string pattern into its actual pattern matching
            regex = re.compile(tok_regex)
            # looking for a match
            match = regex.search(line)

            if match and tok_type != 'WS' and tok_type != 'NEWLN':  # Skip whitespace and newLine
                    token = (tok_type, match.group(0).strip())  # getting the match from the line
                    tokens.append(token)

        return tokens


    def parse(self, tokens):
        '''
        Usually in parsing phase, the tokens are checked and then a data structure (usually a tree)
        will be constructed from tokens that will be send to another method, and that method actually
        translate and runs the tokens. HERE, we are combining the parsing with also executing the tokens. 
        Just to keep things simpler.
        '''
        it = iter(tokens)

        try:
            for token in it:
                if token[0] == 'PRINT_VAR':
                    try:
                        next(it)
                        next(it)
                        var_name = token[1][6:]

                        if var_name in self.variables:
                            value = self.variables[var_name]
                            if isinstance(value, str):  # Check if the value is a string
                                print(f'{var_name} = "{value}"')  # Wrap the string in quotes
                            else:
                                print(f"{var_name} = {value}")  # Print other types normally
                        else:
                            print(f"Undefined variable '{value_token[1]}' on line {self.line_number}")
                            sys.exit()
                    except StopIteration:
                        print(f"RUNTIME ERROR: {self.line_number}")
                        sys.exit();

                elif token[0] in ['INT_VAR', 'STR_VAR'] and not (token[0] == 'PRINT'):
                    var_name = token[1]
                    next(it)  # skip the next token. We will deal with the Str or Int value later
                    op_token = next(it)[1]  # Get the operator
                    value_token = next(it)  # Get the value token
                    semicolon = next(it)[1]  # Ensure semicolon

                    if value_token[0] == 'NUMBER':
                        value = int(value_token[1])
                    elif value_token[0] == 'STRING':
                        value = value_token[1][1:-1]  # getting rid of ""
                    else: 
                        '''
                        if it's not a number or string, then it's a variable, 
                        then it's one of INT_VAR_VAL or STR_VAR_VAL or ASS_VAL
                        so let's get the value of that variable. 
                        '''
                        value = self.variables[value_token[1]]
                        if value is None:
                            print(f"Undefined variable '{value_token[1]}' on line {self.line_number}")
                            sys.exit()

                    try: # for capturing the error where we add an int value to a string variable or vice versa
                        if op_token == '=':
                            self.variables[var_name] = value
                        elif op_token == '+=':
                            if var_name not in self.variables:
                                # Initialize to 0 for numeric variables and empty string for string variables
                                if isinstance(value, str):  # Check if the value is a string
                                    self.variables[var_name] = ""
                                else:
                                    self.variables[var_name] = 0
                            self.variables[var_name] += value
                        elif op_token == '-=':
                            # Default to 0 if the variable is not defined
                            if var_name not in self.variables:
                                self.variables[var_name] = 0
                            self.variables[var_name] -= value
                        elif op_token == '*=':
                            # Default to 0 if the variable is not defined
                            if var_name not in self.variables:
                                self.variables[var_name] = 0
                            self.variables[var_name] *= value
                        elif op_token == '\\=':
                            # Default to 0 if the variable is not defined
                            if var_name not in self.variables:
                                self.variables[var_name] = 0
                                
                            # checks if the division is with integers or floats only
                            if isinstance(self.variables[var_name], (int, float)) and isinstance(value, (int, float)):
                                if value != 0:
                                    self.variables[var_name] //= value  # integer division
                                else:
                                    print(f"Error: Division by zero on line {self.line_number}")
                                    sys.exit()
                            else:
                                print(f"RUNTIME ERROR: {self.line_number}")
                                sys.exit()
                    except Exception as e:
                        print(f"RUNTIME ERROR: {self.line_number}")
                        sys.exit()
        except Exception as e:
            print(f"RUNTIME ERROR: {self.line_number}")  # catches errors when parsing tokens
            sys.exit()

    def run(self, file_name = ""):
        """
        Runs the interpreter on the provided file.
        """
        if file_name == "":
            file_name = self.file_name

        self.line_number = 0

        try:
            with open(file_name, 'r') as file:
                for line in file:
                    self.line_number += 1

                    tokens = self.lexical_analysis(line)
                    self.parse(tokens)
        except FileNotFoundError:
            print(f"Error: The file '{file_name}' was not found.")
            sys.exit(1)  # Exit with an error code
        except IOError as e:
            print(f"Error: An I/O error occurred while accessing the file '{file_name}': {e}")
            sys.exit(1)  # Exit with an error code

if __name__ == "__main__":
    # Check if the filename is provided as a second argument
    if len(sys.argv) > 1:
        filename = sys.argv[1]  # Get the filename from the command line
    else:
        print("Usage: python3 zpm.py <filename>")
        sys.exit(1)  # Exit the program if no file is provided

    interpreter = Interpreter(filename);
    interpreter.run()

