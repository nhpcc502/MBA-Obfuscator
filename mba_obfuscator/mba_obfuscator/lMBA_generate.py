#!/usr/bin/python3

"""
linear MBA generation:
    left_bitwise_list: bitwise expressions without standard basis vector.
    right_bitwise_list: bitwise expressions on standard basis vector.
    step1: randomly generate left MBA expression,
    step2: left MBA expression is equal to right MBA expression throuth the signature vector.
    step3: construct one mba equation.
Given one simplified MBA expression:
    step1: randomly generate right MBA expression.
    step2: right MBA expression - simplified MBA expression, goes into linear MBA generation.
"""

import argparse
import numpy as np
import os
import random
import re
import sys
sys.path.append("../tools")
import traceback
import z3
from mba_string_operation import verify_mba_unsat, truthtable_term_list, truthtable_expression, combine_term, variable_list


class LinearMBAGenerator():
    """linear MBA expression generation.
    Attributes:
        vnumber: the number of variables.
        coeList: the set of coefficient existing in one mba expression 
        maxterm: the maximum number of terms contained in one mba expression.
    """
    def __init__(self, vnumber, coeList=None, maxterm=100):
        if vnumber in [1, 2, 3, 4]:
            self.vnumber = vnumber
        else:
            print("the value of vnumber is wrong!")
            traceback.print_stack()
            sys.exit(0)
        if not coeList:
            self.coeList = [1, -1]*19 + [2, -2]*13 + [3,4,5,7,11,-3,-5,-6,-7,-11]*7 
        else:
            self.coeList = coeList
        self.maxterm = maxterm
        self.standardBitList = [None] * 2**vnumber
        self.nonstandardBitList = [] 
        self.get_truthtable()

        return None


    def get_truthtable(self):
        """read the entire truth table from the related file. 
        Args:
            vnumber: the number of variables.
        """
        abspath = os.path.realpath(__file__)
        (dirpath, filename) = os.path.split(abspath)
        fileread = "{dirpath}/../dataset/{vnumber}variable_truthtable.txt".format(dirpath=dirpath, vnumber=self.vnumber)
        #check the file of truth table
        #try:
        #    with open(fileread, "r") as fr:
        #        pass
        #except:
        #    command = """ python3 -c "from truthtable_generate import exec_all; exec_all()" """
        #    os.system(command)

        with open(fileread, "r") as fr:
            linenum = 0
            for line in fr:
                if "#" not in line:
                    line = line.strip("\n")
                    itemList = re.split(",", line)
                    truthtable = itemList[0]
                    bitwiseExpre = itemList[1]
                    #discard the zero value
                    if not re.search("1", truthtable):
                        continue
                    #standard basis vector
                    elif truthtable.count("1") == 1:
                        truthtable = truthtable.strip("[]")
                        truthtableList = [int(item) for item in truthtable.split(" ")]
                        index = truthtableList.index(1)
                        self.standardBitList[index] = bitwiseExpre
                    else:
                        self.nonstandardBitList.append(bitwiseExpre)
    
        return None


    def generate_lmba_dataset(self, mbanumber):
        """generate the linear MBA expression dataset.
        Args:
            mbanumber: the nubmer of mba expression in the dataset.
        """
        leftLen = len(self.nonstandardBitList)
        filewrite = "../dataset/lMBA_" + str(vnumber) + "variable.dataset.txt"
        fw = open(filewrite, "w")
        print("#complex, groundtruth, z3flag", file=fw)
    
        #linenum = 0
        #the number of the bitwise items from 2 to self.maxterm.
        termNumberList = list(range(3, leftLen, 1))[:self.maxterm]
        #termNumberList = list(range(3, leftLen, 1))[:20]
        #termNumberList = list(range(3, leftLen, 1))[:2]
        for i in range(mbanumber):
            k = random.choice(termNumberList)
            bitExprek = random.sample(self.nonstandardBitList, k)
            coek = random.sample(self.coeList, k)
            leftExpreList = []
            #obtain the mba items of left side of the equation 
            for i in range(len(coek)):
                coe = coek[i]
                bitwiseExpre = bitExprek[i]
                if coe == 1:
                    #for the consistent format
                    leftExpreList.append(str(coe) + "*" + bitwiseExpre)
                else:
                    leftExpreList.append(str(coe) + "*" + bitwiseExpre)
            #generate the mba expression over 3 variables.
            (leftExpre, rightExpre) = self.generate_mba_expression(leftExpreList)
            print("z3 solving...")
            z3res = verify_mba_unsat(leftExpre, rightExpre, 2)
            print("z3 solved: ", z3res)
            print(leftExpre, rightExpre, z3res, sep=",", file=fw, flush=True)

        fw.close()
        return None


    def generate_mba_expression(self, leftExpreList):
        """based on the fact that left expression is equal to right expression, generate mba expression. rightBitwiseList is the bitwise expression which truth table is the standard vector.
        Args:
            leftExpreList: left expression list.
        Returns:
            (left, right): the left and right side of one mba expression.
        Raises:
            None.
        """
        #calculate the signature vector
        truthtableRes = truthtable_term_list(leftExpreList, self.vnumber)
    
        #get the entire mbaExpression = 0
        rightExpreList = []
        for index in range(2**self.vnumber):
            number = truthtableRes[index]
            if not number:
                continue
            else:
                expreStr = str(number*-1)  + "*" + self.standardBitList[index]
                leftExpreList.append(expreStr)
    
        #get one or two items as the ground truth 
        number = random.randint(1,2)
        #number = 1
        #rangdomly choice number terms
        groundTruthList = random.sample(leftExpreList, number)
        #remove the selected terms
        for idx in range(number):
            leftExpreList.remove(groundTruthList[idx])
    
        #obtain the complex mba expression.
        expreList = leftExpreList
        leftExpre = expreList[0]
        for index in range(1, len(expreList)):
            itemExpre = expreList[index]
            if itemExpre[0] == "-":
                leftExpre += itemExpre
            else:
                leftExpre +=  "+"  + itemExpre
    
        #the ground truth of mba expression.
        rightExpre = ""
        for (idx, itemExpre) in enumerate(groundTruthList):
            #split the term by "*"
            itemList = re.split("\*", itemExpre)
            if len(itemList) > 1:
                number = -1 * int(itemList[0])
                if number > 0:
                    if idx == 0:
                        rightExpre = str(number) + "*" + itemList[1]
                    else:
                        rightExpre += "+" + str(number) + "*" + itemList[1]
                else:
                    rightExpre += str(number) + "*" + itemList[1]
            elif itemExpre[0] == "-":
                rightExpre += "+" + itemExpre[1:]
            else:
                rightExpre += "-" + itemExpre
    
        lefttruthtable = truthtable_expression(leftExpre, self.vnumber)
        righttruthtable = truthtable_expression(rightExpre, self.vnumber)
        assert lefttruthtable == righttruthtable, print("error in construct mba expression.")

        return (leftExpre, rightExpre)

def complex_groundtruth_handle(groundtruth, vnumber, partterm=None):
    """given one ground truth, construct one related complex linear mba expression
    Algorithm:
        step1: get the truth table of groundtruth.
        step2: randomly choice bitwise expression and related coefficient.
        step3: create the new truth table.
        step4: construct one equation.
    Args:
        groundtruth: one simplified mba expression defined by the users.
        partterm: the partterm must be constained in the complex MBA expression.
    Returns:
        expreStr: the related complex linear mba expression.
    """
    gtruth = truthtable_expression(groundtruth, vnumber)
    if partterm:
        ptruth = truthtable_expression(partterm, vnumber)
    else:
        ptruth = [0] * 2**vnumber

    #get standard and non-standard bitwise expression
    lmbaObj = LinearMBAGenerator(vnumber)
    sbitList = lmbaObj.standardBitList
    nsbitList = lmbaObj.nonstandardBitList

    #the number of bitwise selcted from the standard bitwise list
    cnumber = vnumber 
    coeList = random.sample(lmbaObj.coeList, cnumber)
    bitList = random.sample(nsbitList, cnumber)
    termList = []
    for i in range(cnumber):
        coe = coeList[i]
        bit = bitList[i]
        if coe > 0:
            term = "+" + str(coe) + "*" + bit
        else:
            term = str(coe) + "*" + bit
        termList.append(term)
    #get the randomly selected term expression
    cexpre = "".join(termList)
    if cexpre[0] == "+":
        cexpre = cexpre[1:]

    #the difference between ground truth and konwn expression
    ctruth = truthtable_expression(cexpre, vnumber)
    #ground truth = partterm_truth + random_truth + standard_truth
    diftruth = np.array(gtruth) - np.array(ptruth) - np.array(ctruth) 
    difList = list(diftruth)
    #construce the standard expression
    sexpreList = []
    for idx in range(2**vnumber):
        coe = difList[idx]
        if not coe:
            continue
        else:
            if coe > 0:
                term = "+" + str(coe) + "*" + sbitList[idx]
            else:
                term = str(coe) + "*" + sbitList[idx]
            sexpreList.append(term)
    sexpre = "".join(sexpreList)
    
    #construct the final complex expression
    if partterm:
        complexExpre = partterm
    else:
        complexExpre = ""
    if cexpre[0] == "-":
        complexExpre += cexpre
    else:
        complexExpre += "+" + cexpre
    #sexpre may be one null string
    if sexpre:
        if sexpre[0] == "-":
            complexExpre += sexpre
        else:
            complexExpre += "+" + sexpre
    if complexExpre[0] == "+":
        complexExpre = complexExpre[1:]

    #verification
    z3res = verify_mba_unsat(groundtruth, complexExpre)
    if not z3res:
        print("error in complex_groundtruth!")
        sys.exit(0)

    #combine like term
    complexExpre = combine_term(complexExpre)

    return complexExpre



def complex_groundtruth(groundtruth, partterm=None):
    """given one ground truth, construct one related complex linear mba expression
    Algorithm:
        step1: get the truth table of groundtruth.
        step2: randomly choice bitwise expression and related coefficient.
        step3: create the new truth table.
        step4: construct one equation.
    Args:
        groundtruth: one simplified mba expression defined by the users.
        partterm: the partterm must be constained in the complex MBA expression.
    Returns:
        expreStr: the related complex linear mba expression.
    """
    #get the number of variable in the expression
    vnumber1 = len(variable_list(groundtruth))
    if partterm:
        vnumber2 = len(variable_list(partterm))
        vnumber = max([vnumber1, vnumber2, 2])
    else:
        vnumber = max([vnumber1, 2])

    #get the related compplexExpre
    complexExpre = complex_groundtruth_handle(groundtruth, vnumber, partterm)

    return complexExpre


def lMBA_sort_by_term(fileread=None, filewrite=None):
    """sort the linear MBA expression.
    Args:
        fileread: the original file storing linear MBA expression.
        filewrite: the file storing the sorted MBA expression.
    """
    if not fileread:
        print("Please input the file storing MBA expression.")
    if not filewrite:
        print("Please input the file storing new MBA expression.")
    
    #get all expression
    expreList = []
    with open(fileread, "rt") as fr:
        for line in fr:
            if "#" in line:
                continue
            line = line.strip()
            expreList.append(line)

    #get the number of terms in one expression
    for (idx, expre) in enumerate(expreList):
        MBAexpreList = re.split(",", expre)
        MBAexpre = MBAexpreList[0]
        itemList = re.split("[\+-]", MBAexpre) 
        itemList = [i for i in itemList if i]
        term = len(itemList)
        expreList[idx] = [expre, term]

    #the sorted key is the terms of one expression
    expreList = sorted(expreList, key=lambda x: x[1])
    
    #output the sorted expression to new file
    flag = 0
    with open(filewrite, "wt") as fw:
        print("#complex,groundtruth,z3flag", file=fw)
        for expre in expreList:
            MBAexpre = expre[0]
            term = expre[1]
            if not flag:
                flag = term
                print("#{term}-terms generated expression.".format(term=term), file=fw)
            elif flag != term:
                flag = term
                print("#{term}-terms generated expression.".format(term=term), file=fw)

            print(MBAexpre, file=fw)

    return None


def unittest(vnumber, MBAnumber=100):
    """unit test of the class.
    """
    lmbaObj = LinearMBAGenerator(vnumber)
    lmbaObj.generate_lmba_dataset(MBAnumber)

    fileread = "../dataset/lMBA_{vnumber}variable.dataset.txt".format(vnumber=vnumber)
    filewrite = "../dataset/lMBA_{vnumber}variable.dataset.sorted.txt".format(vnumber=vnumber)
    lMBA_sort_by_term(fileread, filewrite)

    #groundtruth = "x+y"
    #cexpre = complex_groundtruth(groundtruth, partterm="-3*(x^y)")
    #z3res = verify_mba_unsat(groundtruth, cexpre)
    #print(cexpre, groundtruth, z3res)

    return None



def main(vnumber, MBAnumber=100):
    unittest(vnumber, MBAnumber)

    return None


if __name__ == "__main__":
    vnumber = int(sys.argv[1])
    if len(sys.argv) > 2:
        MBAnumber = int(sys.argv[2])
        main(vnumber, MBAnumber)
    else:
        main(vnumber)



