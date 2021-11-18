#!/usr/bin/python3

"""
non-poly MBA generation:
#1: replace the variable/bitwise with one MBA expression.
#2: recursively apply MBA rules.
"""

import random
import re
import sys
sys.setrecursionlimit(30000)
sys.path.append("../tools")
from lMBA_generate import complex_groundtruth_handle, complex_groundtruth
from pMBA_generate import PolyMBAGenerator
from mba_string_operation import variable_list, verify_mba_unsat, expression_2_term


def replace_one_variable(groundtruth):
    """in the mba expression, replace one variable with one linear mba expression. 
    Args:
        groundtruth: mba expressoin.
    Returns:
        # mbaExpre: original mba expression.
        # order: the transformation method.
        # oneVar: one variable that selected from the varialbes.
        # lmbaExpre: mba expression equaling to eh oneVar.
        newmbaExpre: the output mba expression.
    """
    #for more complex MBA expression, firstly complex the groundtruth
    mbaExpre = complex_groundtruth(groundtruth)
    #get one variable
    varList = variable_list(mbaExpre)
    oneVar = varList[0]
    #replace the one variable with complex mba expression
    pmbaObj = PolyMBAGenerator(2, 2)
    pmbaExpre = pmbaObj.generate_pMBA_from_zeroequality(oneVar)
    pmbaExpre = "({mba})".format(mba=pmbaExpre)
    #lmbaExpre = complex_groundtruth_handle(oneVar, len(varList))
    #lmbaExpre = "({mba})".format(mba=lmbaExpre)

    termList = expression_2_term(mbaExpre)
    #replace the first term
    termList[0] = termList[0].replace(oneVar, pmbaExpre)
    #replace the last term
    termList[-1] = termList[-1].replace(oneVar, pmbaExpre)
    #construct the new mba expression
    newmbaExpre = "".join(termList)

    #verification
    z3res = verify_mba_unsat(mbaExpre, newmbaExpre)
    if not z3res:
        print("error in replace one variable.")
        sys.exit(0)

    return newmbaExpre
    #return [mbaExpre, 1, oneVar, lmbaExpre, newmbaExpre]



def recursively_apply(mbaExpre):
    """in the mba expression, replace the first two terms with linear_mba(x + y).
    Args:
        mbaExpre: the simple mba expressoin. 
    Returns:
        # mbaExpre: original mba expression.
        # order: the transformation method.
        # sub-expression: the first two terms of the original mba expression.
        # lmbaExpre: mba expression equaling to "x+y", x is replaced with the first term, y is replaced with the second term.
        # newmbaExpre: new mba expression.
        newmbaExpre: the output complex mba expression.
    """
    mbaExpre = complex_groundtruth(mbaExpre)
    #preprocess on the mba expression
    varList = variable_list(mbaExpre)
    termList = expression_2_term(mbaExpre)
    #transform the termList1, remain termList2
    termList1 = termList[:2]
    termList2 = termList[2:]
    remainExpre = "".join(termList2)

    #complex groundtruth: "x + y"
    groundExpre = "x+y"
    lmbaExpre = complex_groundtruth_handle(groundExpre, 2)
    #x + y = f(x,y) ==> term1 + term2 = f(term1, term2)
    expre1 = "({expre})".format(expre=termList1[0].replace("x", "a").replace("y", "b"))
    expre2 = "({expre})".format(expre=termList1[1].replace("x", "a").replace("y", "b"))
    lmbaExpre = lmbaExpre.replace("x", expre1).replace("y", expre2)
    lmbaExpre = lmbaExpre.replace("a", "x").replace("b", "y")

    #construct the new mba expression
    newmbaExpre = lmbaExpre + remainExpre 

    #verification
    z3res = verify_mba_unsat(newmbaExpre, mbaExpre)
    if not z3res:
        print("error in recursively apply.")
        sys.exit(0)

    return newmbaExpre
    #return [mbaExpre, 2, "".join(termList1), lmbaExpre, newmbaExpre]



def add_zero(groundtruth):
    """Given a groundtruth, add a MBA expression that equals to 0 to it.
    Args:
        groundtruth: the simple mba expression.
    Returns:
        mbaExpre: the output mba expression.
    Raises:
        None.
    """
    pmbaObj = PolyMBAGenerator(2, 2)
    pmbaExpre = pmbaObj.generate_pMBA_from_zeroequality("0")
    mbaExpre = complex_groundtruth(groundtruth)
    if pmbaExpre[0] == "-":
        mbaExpre += pmbaExpre
    else:
        mbaExpre += "+" + pmbaExpre

    return mbaExpre


def replace_sub_expre(groundtruth):
    """Given a groundtruth, add a MBA expression that equals to 0 to it.
    Args:
        groundtruth: the simple mba expression.
    Returns:
        mbaExpre: the output mba expression.
    Raises:
        None.
    """
    pmbaObj = PolyMBAGenerator(2, 2)
    mbaExpre = complex_groundtruth(groundtruth)
    mbaExpreterm = expression_2_term(mbaExpre)
    subExpre = mbaExpreterm[-1]
    pmbaExpre = pmbaObj.generate_pMBA_from_zeroequality(subExpre)
    mbaExpre = "".join(mbaExpreterm[:-1])

    if pmbaExpre[0] == "-":
        mbaExpre += pmbaExpre
    else:
        mbaExpre += "+" + pmbaExpre

    return mbaExpre




def generate_nonpoly_expression(mbaExpre):
    """input must be one poly mba expression, transform it into one non-poly mba expression.
    Args:
        mbaExpre: one poly mba expression.
    Returns;
        newmbaExpreList: the transformation list that transform the mba expression into non-poly mba expression..
    """
    #reandomly apple non-poly generation's method
    a = random.randint(1, 3)
    if a&1:
        return recursively_apply(mbaExpre)[-1]
    else:
        return replace_one_variable(mbaExpre)[-1]


def nonpoly_dataset_generation(fileread):
    """based on the existing dataset storing poly mba expression, generating non-poly mba expression.
    Args:
        fileread; file storing poly mba expression.
    """
    filewrite = "{file}.nonpoly.dataset.txt".format(file=fileread)
    fw = open(filewrite, "w")
    print("#original,complex,groundtruth,z3flag,transformation", file=fw)

    with open(fileread, "r") as fr:
        for line in fr:
            if "#" not in line:
                line = line.strip()
                itemList = re.split(",", line)
                originalExpre = itemList[0]
                groundExpre = itemList[1]
                transformationList = generate_nonpoly_expression(originalExpre)
                complexExpre = transformationList[-1]
                z3res = verify_mba_unsat(complexExpre, groundExpre)
                print(originalExpre, complexExpre, groundExpre, z3res, transformationList,  sep=",", file=fw)
                print(complexExpre, groundExpre, z3res) 

    fw.close()







def main(fileread):
    nonpoly_dataset_generation(fileread)



if __name__ == "__main__":
    fileread = sys.argv[1]
    main(fileread)



