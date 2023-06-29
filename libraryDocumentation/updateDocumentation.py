import json
import ast
import argparse


def astUpdate(filepath):
    # stores results
    functionDict = {}

    # read file data into variable
    with open(filepath, "rb") as f:
        file_data = f.read()
    # create abstract snytax tree from read data
    astTree = ast.parse(file_data, filepath)
    for node in ast.walk(astTree):
        # check if the node corresponds to a function
        if isinstance(node, ast.FunctionDef):
            # populate json
            functionDict[node.name] = {}
            docstring = ast.get_docstring(node).strip().replace("\n", " ").split()
            functionDict[node.name]["Description"] = " ".join(docstring)
            functionDict[node.name]["Input(s)"] = getExpectedArgs(node)
            functionDict[node.name]["Output(s)"] = getExpectedOutputs(node)
    
            
    return functionDict

def getExpectedOutputs(astNode):
    def returnOutputName(element):
        # This checks if the return value is a constant or a variable and returns the appropriate value
        if isinstance(element, ast.Name):
            return element.id
        elif isinstance(element, ast.Constant):
            return element.value
        return ""
    outputs = {}
    outputNames = []
    # if the last line is a tuple, then there are multiple return values
    if isinstance(astNode.body[-1].value, ast.Tuple):
        # iterate through each return value and add the variable name
        for element in astNode.body[-1].value.elts:
            outputNames.append(returnOutputName(element))
    else:
        # otherwise there is only one return value, just add it
        outputNames.append(returnOutputName(astNode.body[-1].value))
    
    outputTypes = []

    # gets returns types as string
    ret = ast.unparse(astNode.returns).strip()
    # if ret starts with tuple, there are multiple 
    if ret.startswith("Tuple"):
        # remove the 'Tuple[' from the beginning and the ']' from the end
        res = ret[6:-1].split(",")
        # split and remove spaces to get individual types
        outputTypes = [s.strip() for s in res]
    else:
        outputTypes = [ret]

    # if isinstance(astNode.returns, ast.Subscript):
    #     # iterate through each return type 
    #     for element in astNode.returns.slice.elts:
    #         # have to do some string addition here if the element is an attribute
    #         outputTypes.append(element.value.id + "." + element.attr if isinstance(element, ast.Attribute) else element.id)
    # else:
    #     outputTypes.append(astNode.returns.value.id + "." + astNode.returns.attr if isinstance(astNode.returns, ast.Attribute) else astNode.returns.id)
    
    # add output names and types to json and return it
    for outName, outType in zip(outputNames, outputTypes):
        outputs[outName] = outType
    return outputs

            
    
    

def getExpectedArgs(astNode):
    args = {}
    for arg in astNode.args.args:
        if not arg.annotation:
            print("No hint for expected input type. Please add it and try again")
            return {}
        args[arg.arg] = ast.unparse(arg.annotation).strip()
    return args


parser = argparse.ArgumentParser(description="Takes in a file of functions and returns a json object that describes them in the following format {'function_name': {'Description': text, 'Inputs': {'nameOfInput': 'typeofInput',...}, 'Outputs': {'nameOfOutput': 'typeofOutput',....}}, ...}")
parser.add_argument("-f", "--targetFile", help = "Filepath to file containing functions")
args = parser.parse_args()
if not args.targetFile:
    print("Please input path to file with functions when running this file with the flag -f")
    exit()
res = astUpdate(args.targetFile)
with open("documentation.json", "w") as f:
    json.dump(res, f)

