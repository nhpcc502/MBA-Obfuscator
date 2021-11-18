#!/usr/bin/python3

"""
MBA expression generation including linear, polynomial, non-polynomial.
"""

import sys
sys.path.append("../tools")
import z3

from lMBA_generate import complex_groundtruth
from mba_string_operation import verify_mba_unsat
from pMBA_generate import groundtruth_2_pmba
from nonpMBA_generate import add_zero,recursively_apply,replace_sub_expre,replace_one_variable



def mba_obfuscator(sexpre, flag="p"):
    """MBA expression generation..
    Args:
        sexpre: a simple expression.
        flag:transformation choice, must in ["l", "p", "np"].
    Returns:
        cexpre: the related complex MBA expression.
    """
       
    if flag in ["l", "p", "np_zero", "np_recur", "np_replace"]:
        pass
    else:
        print("flag wrong! pleaxe input l or p or np")

    testall = True
    if flag == "l":
        cexpre = complex_groundtruth(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        #print(sexpre, cexpre, z3res)
        if not z3res:
            testall = False
    elif flag == "p":
        cexpre = groundtruth_2_pmba(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        #print(sexpre, cexpre, z3res)
        if not z3res:
            testall = False
    elif flag == "np_zero":
        cexpre = add_zero(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        #print(sexpre, cexpre, z3res)
        if not z3res:
            testall = False
    elif flag == "np_recur":
        cexpre = recursively_apply(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        #print(sexpre, cexpre, z3res)
        if not z3res:
            testall = False
    elif flag == "np_replace":
        cexpre = replace_sub_expre(sexpre)
        z3res = verify_mba_unsat(sexpre, cexpre, 8)
        #print(sexpre, cexpre, z3res)
        if not z3res:
            testall = False
    if testall:
        pass
        #pass verification.
    else:
        print("sorry, program output a wrong expression!")


    return cexpre



def unittest( ):
    sexpre = "x+y"

    print(sexpre, mba_obfuscator(sexpre, "l"))
    print(sexpre, mba_obfuscator(sexpre, "p"))
    print(sexpre, mba_obfuscator(sexpre, "np_zero"))
    print(sexpre, mba_obfuscator(sexpre, "np_recur"))
    print(sexpre, mba_obfuscator(sexpre, "np_replace"))



    return None


if __name__ == "__main__":
    unittest()




