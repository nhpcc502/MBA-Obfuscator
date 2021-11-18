#!/usr/bin/python3


import re
import sys
sys.path.append("../tools")
import z3
from lMBA_generate import complex_groundtruth
from pMBA_generate import groundtruth_2_pmba
from nonpMBA_generate import generate_nonpoly_expression
from mba_string_operation import verify_mba_unsat



def linear_groundtruth_poly(lmbaFile):
    """given linear and related ground truth, generate poly MBA expression.
    Args:
        lmbaFile: File storing linear MBA expression.
    Returns:
        None.
    """
    #file storing linear, ground truth, complex expression.
    fw = "{source}.linear.ground.poly.txt".format(source=lmbaFile)
    fw = open(fw, "w")
    print("#linear,groundtruth,poly", file=fw)

    with open(lmbaFile, "r") as fr:
        for line in fr:
            if "#" not in line:
                line = line.strip()
                itemList = re.split(",", line)
                linear = itemList[0]
                groundtruth = itemList[1]
                poly = groundtruth_2_pmba(groundtruth)
                z3res = verify_mba_unsat(groundtruth, poly)
                print(linear, groundtruth, poly, z3res)
                print(linear, groundtruth, poly, sep=",", file=fw)

    return None

def linear_groundtruth_nonpoly(lmbaFile):
    """given linear and related ground truth, generate non-poly MBA expression.
    Args:
        lmbaFile: File storing linear MBA expression.
    Returns:
        None.
    """
    #file storing linear, ground truth, complex expression.
    fw = "{source}.linear.ground.nonpoly.txt".format(source=lmbaFile)
    fw = open(fw, "w")
    print("#linear,groundtruth,nonpoly", file=fw)

    with open(lmbaFile, "r") as fr:
        for line in fr:
            if "#" not in line:
                line = line.strip()
                itemList = re.split(",", line)
                linear = itemList[0]
                groundtruth = itemList[1]
                lmba = itemList[0]
                nonpoly = generate_nonpoly_expression(lmba)
                z3res = verify_mba_unsat(groundtruth, nonpoly)
                print(linear, groundtruth, nonpoly, z3res)
                print(linear, groundtruth, nonpoly, sep=",", file=fw)

    return None

def generate_lmba(mbaExpre):
    """generate linear MBA expression based on the ground truth.
    Args:
        mbaExpre: a simple linear MBA expression.
    Returns:
        newmbaExpre: a random related complex linear MBA expression.
    """
    newmbaExpre = complex_groundtruth(mbaExpre)

    return newmbaExpre


def generate_pmba(mbaExpre):
    """generate polynomial MBA expression based on the ground truth.
    Args:
        mbaExpre: a simple (linear)MBA expression.
    Returns:
        newmbaExpre: a random related complex polynomial MBA expression.
    """
    newmbaExpre = groundtruth_2_pmba(mbaExpre)

    return newmbaExpre

def generate_npmba(mbaExpre):
    """generate non-polynomial MBA expression based on the ground truth.
    Args:
        mbaExpre: a simple linear MBA expression.
    Returns:
        newmbaExpre: a random related complex non-polynomial MBA expression.
    """
    newmbaExpre = generate_nonpoly_expression(mbaExpre)

    return newmbaExpre


def unittest():
    """just for unit test.
    """
    mbaExpre = "~x"
    fw = open("{op}.txt".format(op=mbaExpre), "w")
    print("linear MBA rules")
    for i in range(200):
        newmbaExpre = generate_lmba(mbaExpre)
        z3res = verify_mba_unsat(mbaExpre, newmbaExpre)
        print(mbaExpre, newmbaExpre, sep=",", file=fw)
    fw.close()
    print("polynomial MBA rules")
    for i in range(20):
        mbaExpre = mbaExpre.replace(" ", "")
        newmbaExpre = generate_pmba(mbaExpre)
        z3res = verify_mba_unsat(mbaExpre, newmbaExpre)
        print(mbaExpre, newmbaExpre, z3res)
    print("non-polynomial MBA rules")
    for i in range(20):
        mbaExpre = mbaExpre.replace(" ", "")
        newmbaExpre = generate_npmba(mbaExpre)
        z3res = verify_mba_unsat(mbaExpre, newmbaExpre)
        print(mbaExpre, newmbaExpre, z3res)



if __name__ == "__main__":
    unittest()
    #fr = sys.argv[1]
    #linear_groundtruth_nonpoly(fr)


