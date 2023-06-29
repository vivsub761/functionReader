import json
import ast
import argparse


def astUpdate(filepath):
    functionDict = {}

    with open(filepath, "rb") as f:
        file_data = f.read()
    astTree = ast.parse(file_data, filepath)
    for node in ast.walk(astTree):
        if isinstance(node, ast.FunctionDef):
            funcName = node.name
            functionDict[funcName] = {}
            docstring = ast.get_docstring(node).strip().replace("\n", " ").split()
            functionDict[funcName]["Description"] = " ".join(docstring)
            functionDict[funcName]["Input(s)"] = getExpectedArgs(node)
            functionDict[funcName]["Output(s)"] = getExpectedOutputs(node)
    
            
    return functionDict

def getExpectedOutputs(astNode):
    def returnOutputName(element):
        if isinstance(element, ast.Name):
            return element.id
        elif isinstance(element, ast.Constant):
            return element.value
        return ""
    outputs = {}
    outputNames = []
    if isinstance(astNode.body[-1].value, ast.Tuple):
        for element in astNode.body[-1].value.elts:
            outputNames.append(returnOutputName(element))
    else:
        outputNames.append(returnOutputName(astNode.body[-1].value))
    
    outputTypes = []
    if isinstance(astNode.returns, ast.Subscript):
        for element in astNode.returns.slice.elts:
            outputTypes.append(element.value.id + "." + element.attr if isinstance(element, ast.Attribute) else element.id)
    else:
        if isinstance(astNode.returns, ast.Name):
            outputTypes.append(astNode.returns.id)
        elif isinstance(astNode.returns, ast.Attribute):
            outputTypes.append(astNode.returns.value.id + "." + astNode.returns.attr)
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

