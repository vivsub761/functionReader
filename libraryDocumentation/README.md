To run the file, run the updateDocumentation file on command line with the flag -f "path_to_file_with_functions", e.g. python3 updateDocumentation.py -f ./functions.py

IMPORTANT: For each function in the file in question:
    There must be at least one docstring in the function. The very first docstring MUST contain a brief description of the function. Subsequent ones do not matter to this script.
    The function should have argument annotation(s), e.g. def function(x: int, y: str)
    The function should have output annotation(s), e.g. def function(x: int, y: str) -> Tuple[int, str]
    Do not make any computations in the return statement. The return statement should simply return variable(s) without any modification
