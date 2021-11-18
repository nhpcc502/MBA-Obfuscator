#!/usr/bin/python3

"""
This file including the operation of MBA expression by the string-related operation.
"""

import numpy as np
import re
import sys
import traceback
import z3


def postfix(itemString):
    """transform infixExpre into postfixExpre
    Algorithm:
        step1: if operator, stack in;
        step2: if "(", stack in.
        step3: if variable, pop out the all continued unary operator until other operator or "("
        step4: if ")", pop out all operators until "(", then pop all continued unary operator.
        step5: goto step1.
    Arg:
        itemString: bitwise expression string persented in infix.
    Return:
        itemStr: expression string persented in postfix.
    """
    itemStr = ""
    boperatorList = ["&", "|", "^"]
    uoperator = "~"
    opeList = []

    for (idx, char) in enumerate(itemString):
         #open parenthesis, stack it
        if char == "(":
            opeList.append(char)
        #binary operatork, stack it
        elif char in boperatorList:
            opeList.append(char)
        #unary operator
        elif uoperator in char:
            opeList.append(char)
        #closed parenthesis, pop out the operator to string
        elif char == ")":
            while(opeList and opeList[-1] != "("):
                itemStr += opeList[-1]
                opeList.pop()
            if opeList and opeList[-1] != "(":
                print("error!")
                sys.exit(0)
            #open parenthesis found
            opeList.pop()
            #unary operator found before open parenthesis
            while(opeList and opeList[-1] == "~"):
                itemStr += opeList[-1]
                opeList.pop()
        #variable name found
        else:
            itemStr += char
            #top of stack is unary operator
            while(opeList and opeList[-1] in uoperator):
                itemStr += opeList[-1]
                opeList.pop()

    if len(opeList) > 1:
        print("error in function postfix!")
        sys.exit(0)
    #have one operator without parenthesis
    elif len(opeList):
        itemStr += opeList[0]

    return itemStr


def postfix_cal(itemString, vnumber=0):
    """calculate the result of the expression string.
    Args:
        itemString: bitwise expression string persented in postfix.
        vnumber: the number of variables.
    Returns:
        result: the result list of the expression string.
    Raises:
        through out SystemExit exception.
    """
    if vnumber == 1:
        x = [0,1]
    elif vnumber == 2:
        y = [0, 1] * 2
        x = [0, 0, 1, 1] 
    elif vnumber == 3:
        y = [0, 1] * 4
        x = [0, 0, 1, 1] * 2
        z = [0] * 4 + [1] * 4
    elif vnumber == 4:
        y = [0, 1] * 8
        x = [0, 0, 1, 1] * 4
        z = [0] * 4 + [1] * 4 + [0] * 4 + [1] * 4
        t = [0] * 8 + [1] * 8
    else:
        print("please passing correct argument of the number of variable:1, 2, 3, 4")
        traceback.print_stack()
        sys.exit(0)
    variableList = ["x", "y", "z", "t"]
    binaryOperator = ["&", "|", "^"]
    unaryOperator = ["~"]

    stack = []
    for c in itemString:
        if c in variableList:
            stack.insert(0, eval(c))
        elif c in unaryOperator:
            operation = stack.pop(0)
            res = np.invert(operation)
            res = res % 2
            stack.insert(0, res)
        elif c in binaryOperator:
            operation1 = stack.pop(0)
            operation2 = stack.pop(0)
            if c == "&":
                res = np.bitwise_and(operation1, operation2)
                stack.insert(0, res)
            elif c == "|":
                res = np.bitwise_or(operation1, operation2)
                stack.insert(0, res)
            elif c == "^":
                res = np.bitwise_xor(operation1, operation2)
                stack.insert(0, res)

    if len(stack) > 1:
        print("error in function of postfix_cal!")
    else:
        result = stack[0]
        if isinstance(result, list):
            pass
        else:
            result = result.tolist()

        return result



def verify_mba_unsat(leftExpre, rightExpre, bitnumber=2):
    """check the relaion whether the left expression is euqal to the right expression.
    Args:
        leftExpre: left expression.
        rightExpre: right expression.
        bitnumber: the number of the bits of the variable.
    Returns:
        True: equation.
        False: unequal.
    Raises:
        None.
    """
    x,y,z,t,a,b,c,d,e,f = z3.BitVecs("x y z t a b c d e f", bitnumber)

    leftEval = eval(leftExpre)
    rightEval = eval(rightExpre)

    solver = z3.Solver()
    solver.add(leftEval != rightEval)
    result = solver.check()

    if str(result) != "unsat":
        return False
    else:
        return True



def truthtable_term_list(termList, vnumber=0):
    """obtain the result vector based on the term list on mba expression.
    Args:
        termList: mba expression string splited by the + or - operator.
        vnumber: the number of variable.
    Returns:
        result: the result vector presenting by np.array format of the mba expression.
    Raises:
        through out SystemExit exception.
    """
    #function call error
    if not vnumber:
        print("please passing argument on the number of variable")
        traceback.print_stack()
        sys.exit(0)
    #empty expression
    if not termList:
        return [0] * 2**vnumber
    result = np.zeros((2**vnumber,), dtype=np.int)
    for item in termList:
        itemList = re.split("\*", item)
        #only bitwise expression or constant
        if len(itemList) == 1:
            bitwiseExpre = itemList[0]
            if bool(re.search("\d", bitwiseExpre)):
                #constant
                result += np.array([int(bitwiseExpre) * -1] * 2**vnumber)
            else:
                #only bitwise expression
                if bitwiseExpre[0] == "+":
                    result += np.array(truthtable_bitwise(bitwiseExpre[1:], vnumber))
                elif bitwiseExpre[0] == "-":
                    result -= np.array(truthtable_bitwise(bitwiseExpre[1:], vnumber))
                else:
                    result += np.array(truthtable_bitwise(bitwiseExpre, vnumber))
        #coefficient and bitwise
        elif len(itemList) == 2:
            coefficient = int(itemList[0])
            bitwiseExpre = itemList[1]
            result += coefficient * np.array(truthtable_bitwise(bitwiseExpre, vnumber))

    return result.tolist()


def truthtable_bitwise(bitExpre, vnumber):
    """generate the truth table of a bitwise expression.
    Args:
        bitExpre: a bitwise expression.
        vnumber: the number of variables in a expression.
    Returns:
        truthList: a truth table on a format of list.
    """
    truthList = postfix_cal(postfix(bitExpre), vnumber)

    return truthList



def truthtable_expression(expreStr, vnumber):
    """generate the truth table on a linear MBA expression.
    Args:
        expreStr: a linear MBA expression.
        vnumber: the number of variables in a expression.
    Returns:
        truthtalbeList: a truth table on a format of list.
    """
    termList = expression_2_term(expreStr)

    #truth table of bitwise expression 
    truthtableList = truthtable_term_list(termList, vnumber)

    return truthtableList
    


def expression_2_term(expreStr):
    """generate the truth table on a linear MBA expression.
    Args:
        expreStr: a linear MBA expression.
    Returns:
        termList: a list of terms on bitwise expression.
        constantList: a list of constant term of the linear MBA expression.
    """
    itemList = re.split("([\+-])", expreStr)
    item0 = itemList[0]
    termList = []
    constantList = []
    if item0 != "":
        itemList.insert(0, "")
    for (idx, item) in enumerate(itemList):
        if item == "+" or item == "-" or item == "":
            continue
        #bitwise term
        elif re.search("\w+", item):
            term = itemList[idx - 1] + itemList[idx]
            termList.append(term)
        #constant term
        elif re.search("\d+", item):
            term = itemList[idx - 1] + itemList[idx]
            constantList.append(term)
        else:
            print("This is something wrong in mba expression.")
            traceback.print_stack()
            sys.exit(0)

    return termList +  constantList


def generate_coe_bit(mbatermList):
    """split the one term into pair, [coe, bit]
    Arg:
        mbatermList: one list of terms.
    Return:
        coeBitList: one list of pair [coe, bit]
    """
    coeBitList = []
    for term in mbatermList:
        itemList = re.split("\*", term)
        maycoe= itemList[0]
        #not coefficient
        if not bool(re.search("\d", maycoe)):
            bit = itemList[0]
            bit = bit.replace("+", "")
            if "-" not in term:
                coe = 1
            else:
                coe = -1
                bit = bit.replace("-", "")
            coeBitList.append([coe, bit])
        #multi bitwise expression
        elif len(itemList) >= 2:
            #1 is for the first time synbol
            bit = term[len(maycoe)+1:]
            coeBitList.append([maycoe, bit])
        #only constant
        elif len(itemList) == 1 and bool(re.search("\d", maycoe)):
            coeValue = int(maycoe) * -1
            coeBitList.append([str(coeValue), "~(x&~x)"])
            
        else:
            print("error in function of generate_coe_bit")
            exit(0)

    return coeBitList 


def combine_term(mbaExpre):
    """combining like terms of the mba expression
    Args:
        mbaExpre: the mba expression.
    Return:
        newmbaExpre: new mba expression have combined like terms.
    """
    #get pair of coefficient and bitwise on the mba expression
    termList = expression_2_term(mbaExpre)
    coeBitList = generate_coe_bit(termList)

    #firstly sort the list
    coeBitList = sorted(coeBitList, key=lambda x: x[1])
    #walk the list and combine like terms
    newcoeBitList = []
    itemList = coeBitList[0]
    for item in coeBitList[1:]:
        if item[1] != itemList[1]:
            #delete 0 term
            if itemList[0] != "0":
                newcoeBitList.append(itemList)
            itemList = item
        else:
            coe1 = itemList[0]
            coe2 = item[0]
            coe = eval(coe1) + eval(coe2)
            itemList[0] = str(coe)
    #handle the last one term
    if newcoeBitList[-1][1] != itemList[1]:
        newcoeBitList.append(itemList)
    #coefficent and bitwise expression to terms
    newtermList = []
    for item in newcoeBitList:
        coe = item[0]
        bit = item[1]
        if coe[0] == "+" or coe[0] == "-":
            term = "{coe}*{bit}".format(coe=coe, bit=bit)
        else:
            coe = "+" + coe
            term = "{coe}*{bit}".format(coe=coe, bit=bit)
        newtermList.append(term)
    #terms to expression
    newmbaExpre = "".join(newtermList) 
    if newmbaExpre[0] == "+":
        newmbaExpre = newmbaExpre[1:]
    #verification
    z3res = verify_mba_unsat(mbaExpre, newmbaExpre)
    if not z3res:
        print("error in merge_bitwise!")
        sys.exit(0)
    
    return newmbaExpre




def addMBA(mbaExpre1, mbaExpre2):
    """two mba expression addition.
    Args:
        mbaExpre1: one MBA expression.
        mbaExpre2: another one MBA expression.
    Return:
        mbaExpre: the mba expression by addition of mbaExpre1 and mbaExpre2
    """
    #get the coefficient and related bitwise 
    mbaterm1List = expression_2_term(mbaExpre1)
    coeBitList1 = generate_coe_bit(mbaterm1List)
    coeBitDict1 = {}
    for item in coeBitList1:
        coeBitDict1[item[1]] = item[0]
    mbaterm2List = expression_2_term(mbaExpre2)
    coeBitList2 = generate_coe_bit(mbaterm2List)
    coeBitDict2 = {}
    for item in coeBitList2:
        coeBitDict2[item[1]] = item[0]

    commonKey = set(coeBitDict1.keys()) & set(coeBitDict2.keys())
    for key in commonKey:
        coe1 = coeBitDict1[key]
        coe2 = coeBitDict2[key]
        res = eval(coe1) + eval(coe2)
        if not res:
            coeBitDict1.pop(key)
        else:
            coeBitDict1[key] = str(res)
        coeBitDict2.pop(key)
    #the last pair of coefficient and bitwise
    coeBitDict = coeBitDict1
    coeBitDict.update(coeBitDict2)
    termList = []
    for item in coeBitDict.items():
        term = item[1] + "*" + item[0]
        if term[0] == "-" or term[0] == "+":
            termList.append(term)
        else:
            term = "+" + term
            termList.append(term)
    #construct the mba expression
    mbaExpre = "".join(termList)
    if mbaExpre[0] == "+":
        mbaExpre = mbaExpre[1:]

    #verification
    oriExpre = ""
    if mbaExpre2[0] == "+" or mbaExpre2[0] == "-":
        oriExpre = mbaExpre1 + mbaExpre2
    else:
        oriExpre = mbaExpre1 + "+" + mbaExpre2
    z3res = verify_mba_unsat(oriExpre, mbaExpre)
    if not z3res:
        print("error in addMBA!")
        sys.exit(0)

    return mbaExpre


def variable_list(expreStr):
    """get the set of variable of expression.
    Args:
        expreStr: the mba expression string.
    Return:
        variableList: the list of variables.
    """
    varSet = set(expreStr)
    variableList = []
    for i in varSet:
        #the variable name
        if i in ["x", "y", "z", "t", "a", "b", "c", "d", "e", "f"]:
            variableList.append(i)

    return variableList










