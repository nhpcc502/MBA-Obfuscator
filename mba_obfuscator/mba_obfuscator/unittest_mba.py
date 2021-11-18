#!/usr/bin/python3

"""
unit test for MBA expression generation,
including linear, polynomial, non-polynomial.
"""

import sys
sys.path.append("../tools")
import z3

from lMBA_generate import complex_groundtruth
from mba_string_operation import verify_mba_unsat
from pMBA_generate import groundtruth_2_pmba
from nonpMBA_generate import add_zero,recursively_apply,replace_sub_expre,replace_one_variable



def unittest_groundtruth_2_complex(groundtruth=None):
    """unit test of the function of groundtruth2complex.
    Args:
        groundtruth: the ground truth.
    Returns:
        None.
    """

    if groundtruth:
        groundtruth_list = [groundtruth]
    else:
        #firstly test 2-variable MBA expression generation
        groundtruth_list =  ["x+y", "x-y", "(x&y)", "(x|y)", "(x^y)", "0", "1", "-1", "123",  "x", "~x", "y", "~y"]
        # 3 or more variable MBA expression generation testing.
        pass #I'm so lazy. :-(

    testall = True
    for ground in groundtruth_list:
        cexpre = complex_groundtruth(ground)
        z3res = verify_mba_unsat(ground, cexpre, 8)
        print(ground, cexpre, z3res)
        if not z3res:
            testall = False
    if testall:
        print("the test, linear MBA expression generatation from the ground truth, pass!")
    else:
        print("the test, linear MBA expression generatation from the ground truth, unpass!")

    testall = True
    #testing the functon of linear MBA expression generation.
    for ground in groundtruth_list:
        cexpre = groundtruth_2_pmba(ground, vnumber=2)
        z3res = verify_mba_unsat(ground, cexpre, 8)
        print(ground, cexpre, z3res)
        if not z3res:
            testall = False
    if testall:
        print("the test, poly MBA expression generatation from the ground truth, pass!")
    else:
        print("the test, poly MBA expression generatation from the ground truth, unpass!")

    testall = True
    #testing the functon of poly MBA expression generation by recursively applying "x + y" rules.
    for ground in groundtruth_list:
        cexpre = recursively_apply(ground)
        z3res = verify_mba_unsat(ground, cexpre, 8)
        print(ground, cexpre, z3res)
        if not z3res:
            testall = False
    if testall:
        print("the test, nonpoly MBA expression generatation from the ground truth(recursively apply), pass!")
    else:
        print("the test, nonpoly MBA expression generatation from the ground truth(recursively apply), unpass!")

    testall = True
    #testing the functon of non-poly MBA expression generation by replacing a variable in the expression.
    for ground in groundtruth_list:
        cexpre = replace_one_variable(ground)
        z3res = verify_mba_unsat(ground, cexpre, 8)
        print(ground, cexpre, z3res)
        if not z3res:
            testall = False
    if testall:
        print("the test, nonpoly MBA expression generatation from the ground truth(replace_one_variable), pass!")
    else:
        print("the test, nonpoly MBA expression generatation from the ground truth(replace_one_variable), unpass!")

    testall = True
    #testing the functon of non-poly MBA expression generation by adding a expression that equals 0.
    for ground in groundtruth_list:
        cexpre = add_zero(ground)
        z3res = verify_mba_unsat(ground, cexpre, 8)
        print(ground, cexpre, z3res)
        if not z3res:
            testall = False
    if testall:
        print("the test, nonpoly MBA expression generatation from the ground truth(add zero), pass!")
    else:
        print("the test, nonpoly MBA expression generatation from the ground truth(add zero), unpass!")

    testall = True
    #testing the functon of non-poly MBA expression generation by replacing the sub-expression of the original expression.
    for ground in groundtruth_list:
        cexpre = replace_sub_expre(ground)
        z3res = verify_mba_unsat(ground, cexpre, 8)
        print(ground, cexpre, z3res)
        if not z3res:
            testall = False
    if testall:
        print("the test, nonpoly MBA expression generatation from the ground truth(replace_sub_expre), pass!")
    else:
        print("the test, nonpoly MBA expression generatation from the ground truth(replace_sub_expre), unpass!")


    return None



def main( ):
    unittest_groundtruth_2_complex()

    return None


if __name__ == "__main__":
    main()




