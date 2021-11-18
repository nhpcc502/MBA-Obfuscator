#!/usr/bin/python3

"""
poly MBA generation:
    poly = linear * linear * linear ...
add 0-equality:
    0-equality = 0 * linear
               = (part-term) * (-1*linear)
    poly = poly + 0-equality
"""

import argparse
import numpy as np
import os
import random
import re
import sys
sys.setrecursionlimit(30000)
sys.path.append("../tools")
import traceback
import z3
from lMBA_generate import complex_groundtruth
from mba_string_operation import verify_mba_unsat, expression_2_term, generate_coe_bit, addMBA, variable_list



class PolyMBAGenerator():
    """polynomial MBA expression generation, just for MBA * MBA.
    Attributes:
        vnumber1: the number of variables in the first file.
        vnumber2: the number of variables in the second file.
        MBAfile1: the file storing the MBA expression.
        MBAfile2: the another file storing the MBA expression.
        MBAdesfile: the file storing the generated MBA expression.
    """
    def __init__(self, vnumber1, vnumber2, MBAfile1=None, MBAfile2=None, MBAdesfile=None):
        if vnumber1 in [1, 2, 3, 4] and vnumber2 in [1, 2,3,4]:
            self.vnumber1 = vnumber1
            self.vnumber2 = vnumber2
        else:
            print("the value of vnumber is wrong!")
            traceback.print_stack()
            sys.exit(0)
        if not MBAfile1:
            self.MBAfile1 = "../dataset/lMBA_{vnumber}variable.dataset.sorted.txt".format(vnumber=vnumber1)
        else:
            self.MBAfile1 = MBAfile1
        self.MBAList1 = self.get_MBA(self.MBAfile1)
        if not MBAfile2:
            self.MBAfile2 = "../dataset/lMBA_{vnumber}variable.dataset.sorted.txt".format(vnumber=vnumber2)
            #self.MBAfile2 = r"pMBA_{vnumber}*{vnumber}variable.dataset.sorted.txt".format(vnumber=vnumber2)
        else:
            self.MBAfile2 = MBAfile2
        self.MBAList2 = self.get_MBA(self.MBAfile2)
        if not MBAdesfile:
            self.MBAdesfile = "../dataset/pMBA_{vnumber1}_{vnumber2}variable.dataset.txt".format(vnumber1=self.vnumber1, vnumber2=self.vnumber2)
        else:
            self.MBAdesfile = MBAdesfile
        
        return None


    def get_MBA(self, fileread):
        """read the file storing linear MBA expression. 
        Arg:
            fileread: the file storing linear MBA expression.
        Return:
            MBAList: the list of pair on complex MBA and related ground truth.
        """
        MBAList = []
        with open(fileread, "r") as fr:
            linenum = 0
            for line in fr:
                if "#" not in line:
                    line = line.strip("\n")
                    itemList = re.split(",", line)
                    cmba = itemList[0]
                    gmba = itemList[1]
                    MBAList.append([cmba, gmba])
    
        return MBAList


    def generate_pmba_dataset(self, mbanumber):
        """generate the polynomial MBA expression dataset.
        Args:
            mbanumber: the nubmer of mba expression in the dataset.
        """
        filewrite = self.MBAdesfile
        fw = open(filewrite, "w")
        print("#complex, groundtruth, z3flag, c_terms, g_terms", file=fw)
    
        #linenum = 0
        for i in range(mbanumber):
            expreList1 = random.choice(self.MBAList1)
            expreList2 = random.choice(self.MBAList2)
            (cmbaexpreList, gmbaexpreList) = self.generate_one_pMBA(expreList1, expreList2)

            #complex mba expression
            cmbaexpre = cmbaexpreList[0]
            cmbaterm = "{item1}*{item2}".format(item1=cmbaexpreList[1], item2=cmbaexpreList[2])
            #ground truth
            gmbaexpre = gmbaexpreList[0]
            gmbaterm = "{item1}*{item2}".format(item1=gmbaexpreList[1], item2=gmbaexpreList[2])

            print("z3 solving...")
            z3res = verify_mba_unsat(cmbaexpre, gmbaexpre, 2)
            print("z3 result: ", z3res)
            print(cmbaexpre, gmbaexpre, z3res, cmbaterm, gmbaterm, sep=",", file=fw, flush=True)

        fw.close()
        return None


    def generate_one_pMBA(self, expreList1, expreList2):
        """generate one poly MBA expression based on two linear MBA expressions.
        Args:
            expreList1: pair of one linear MBA expression, such as [complexMBA, groundtruth]
            expreList2: pair of another one linear MBA expression, like [complexMBA, groundtruth]
        Returns:
            cmbaexpreList: poly MBA expression, the terms of one complex MBA expression and the other one.
            gmbaexpreList: the related ground truth, the terms of one ground truth and the other one.
        """
        cmbaexpre1 = expreList1[0]
        gmbaexpre1 = expreList1[1]
        cmbaexpre2 = expreList2[0]
        gmbaexpre2 = expreList2[1]

        cmbaexpreList = self.MBA_multiply(cmbaexpre1, cmbaexpre2)
        gmbaexpreList = self.MBA_multiply(gmbaexpre1, gmbaexpre2)

        return cmbaexpreList, gmbaexpreList



    def MBA_multiply(self, mbaexpre1, mbaexpre2):
        """one MBA expression multiply the other one, must be coded in recursive version.
        Args:
            mbaexpre1: one MBA expression.
            mbaexpre2: another one MBA expression.
        Returns:
            mbaexpre: the expression of mbaexpre1 * mbaexpre2
            term1: the number of terms of one expression.
            term2: the number of terms of another one expression.
        """
        #split the expression into terms
        mbaexpre1List = expression_2_term(mbaexpre1)
        #mbaexpre1List = [item for l in mbaexpre1List for item in l ] 
        mbaexpre2List = expression_2_term(mbaexpre2)
        #mbaexpre2List = [item for l in mbaexpre2List for item in l ] 

        #split the mba term in the pair: coefficient, bitwise
        coeBitList1 = generate_coe_bit(mbaexpre1List)
        coeBitList2 = generate_coe_bit(mbaexpre2List)

        #construct the terms in the new MBA expression
        mbaexpreList = []
        for item1 in coeBitList1:
            for item2 in coeBitList2:
                coe1 = item1[0]
                bit1 = item1[1]
                coe2 = item2[0]
                bit2 = item2[1]
                coe = int(coe1) * int(coe2)
                coe = str(coe)
                bit = "{bit1}*{bit2}".format(bit1=bit1, bit2=bit2)
                if "-" in coe:
                    mbaexpre = "{coe}*{bit}".format(coe=coe, bit=bit)
                else:
                    mbaexpre = "+{coe}*{bit}".format(coe=coe, bit=bit)
                mbaexpreList.append(mbaexpre)
                
        #delete the start addition in the expression
        if "+" in mbaexpreList[0]:
            mbaexpreList[0] = mbaexpreList[0][1:]

        #construct the MBA expression
        mbaexpre = "".join(mbaexpreList)

        #check resulting expression
        oriExpre = "({expre1})*({expre2})".format(expre1=mbaexpre1, expre2=mbaexpre2)
        z3res = verify_mba_unsat(oriExpre, mbaexpre)
        if not z3res:
            print("error in function of MBA_multiply!")
            traceback.print_stack()
            sys.exit(0)

        return mbaexpre, len(mbaexpre1List), len(mbaexpre2List)


    def generate_pmba_transformation_dataset(self, mbanumber):
        """generate the polynomial MBA expression that has been added 0-equality.
        Args:
            mbanumber: the nubmer of mba expression in the dataset.
        """
        #filewrite = self.MBAdesfile + ".transformation.txt"
        fw = open(self.MBAdesfile, "w")
        print("#complex, groundtruth, z3flag, c_terms, g_terms", file=fw)
    
        #linenum = 0
        for i in range(mbanumber):
            expreList1 = random.choice(self.MBAList1)
            expreList2 = random.choice(self.MBAList2)
            (cmbaexpreList, gmbaexpreList) = self.generate_one_transform_pMBA(expreList1, expreList2)

            #complex mba expression
            cmbaexpre = cmbaexpreList[0]
            cmbaterm = "{item1}*{item2}".format(item1=cmbaexpreList[1], item2=cmbaexpreList[2])
            #ground truth
            gmbaexpre = gmbaexpreList[0]
            gmbaterm = "{item1}*{item2}".format(item1=gmbaexpreList[1], item2=gmbaexpreList[2])

            print("z3 solving...")
            z3res = verify_mba_unsat(cmbaexpre, gmbaexpre, 2)
            print("z3 result: ", z3res)
            print(cmbaexpre, gmbaexpre, z3res, cmbaterm, gmbaterm, sep=",", file=fw, flush=True)

        fw.close()
        return None


    def generate_one_transform_pMBA(self, expreList1, expreList2):
        """generate one poly MBA expression that has been added one 0-equality.
        Algorithm:
            originalPOly = expreStr1 * expreStr2
            0-equality = (-1/1 * expreStr1) * 0
                       = (-1/1 * expreStr1) * (sub-expression of expreStr2, randomly reverse the coefficient)
            newPoly = originalPoly + 0-equality
                    0-equality is suggested to be a linear MBA expression, non-linear MBA is difficulty to generate it.
        Args:
            expreList1: pair of one linear MBA expression, such as [complexMBA, groundtruth]
            expreList2: pair of another one linear MBA expression, like [complexMBA, groundtruth]
        Returns:
            cmbaexpreList: poly MBA expression, the terms of one complex MBA expression and the other one.
            gmbaexpreList: the related ground truth, the terms of one ground truth and the other one.
        """
        cmbaExpre1 = expreList1[0]
        gmbaExpre1 = expreList1[1]
        cmbaExpre2 = expreList2[0]
        gmbaExpre2 = expreList2[1]

        #original poly MBA expression
        originalcmbaExpreList = self.MBA_multiply(cmbaExpre1, cmbaExpre2)
        originalcmbaExpre = originalcmbaExpreList[0]

        cmbaExpreterm1 = expression_2_term(cmbaExpre1)
        cmbaExpreterm2 = expression_2_term(cmbaExpre2)

        #randomly reverse the sign of every term in cmbaexpre1
        for (idx, term) in enumerate(cmbaExpreterm1):
            r = random.randint(1,3)
            #not reversed
            if r % 2:
                cmbaExpreterm1[idx] = term
                continue
            #reversed
            if term[0] == "+":
                cmbaExpreterm1[idx] = "-" + term[1:]
            elif term[0] == "-":
                cmbaExpreterm1[idx] = "+" + term[1:]
            else:
                cmbaExpreterm1[idx] = "-" + term
        #construct the -1/1 * mbaexpre
        cmbaExpre1 = "".join(cmbaExpreterm1)
        if cmbaExpre1[0] == "+":
            cmbaExpre1 = cmbaExpre1[1:]

        #get part of the mbaexpre
        partterm = cmbaExpreterm2[:len(cmbaExpreterm2) // 2 + 1]
        #randomly reverse the sign of every term in cmbaexpre1
        for (idx, term) in enumerate(partterm):
            r = random.randint(1,3)
            #not reversed
            if r % 2:
                partterm[idx] = term
                continue
            #reversed
            if term[0] == "+":
                partterm[idx] = "-" + term[1:]
            elif term[0] == "-":
                partterm[idx] = "+" + term[1:]
            else:
                partterm[idx] = "-" + term
        #construct the part expression 
        partExpre ="".join(partterm) 
        if partExpre[0] == "+":
            partExpre = partExpre[1:]
        #construct a expression that equals to 0 
        groundtruth = str(0)
        zeroEquality = complex_groundtruth(groundtruth, partExpre)
        #0-equality = 0-expression * part_mbaexpre
        zeroEqualityList = self.MBA_multiply(cmbaExpre1, zeroEquality)
        zeroMBAexpre = zeroEqualityList[0]
        #newmba = orimba + 0-equality
        mbaExpre = addMBA(originalcmbaExpre, zeroMBAexpre)

        #ground truth does not to be changed
        gmbaExpreList = self.MBA_multiply(gmbaExpre1, gmbaExpre2)
        #construct cmbaExpreList
        cmbaExpreList = [mbaExpre, len(expression_2_term(mbaExpre)), 1]

        return cmbaExpreList, gmbaExpreList


    def generate_pMBA_from_zeroequality(self, groundtruth):
        """generate one poly MBA expression that has been added one 0-equality.
        Algorithm:
            originalPOly = complex(groundtruth) * complex(1)
            0-equality = (-1/1 * complex(groundtruth)) * 0
                       = (-1/1 * complex(groundtruth)) * (sub-expression of complex(1), randomly reverse the coefficient)
            newPoly = originalPoly + 0-equality
                    0-equality is suggested to be a linear MBA expression, non-linear MBA is difficulty to generate it.
        Args:
            groundtruth: a simplified expression.
        Returns:
            mbaexpre: the result poly mba expression.
        """
        cmbaExpre1 = complex_groundtruth(groundtruth)
        cmbaExpre2 = complex_groundtruth("1")

        #original poly MBA expression
        originalcmbaExpreList = self.MBA_multiply(cmbaExpre1, cmbaExpre2)
        originalcmbaExpre = originalcmbaExpreList[0]

        cmbaExpreterm1 = expression_2_term(cmbaExpre1)
        cmbaExpreterm2 = expression_2_term(cmbaExpre2)

        #randomly reverse the sign of every term in cmbaexpre1
        for (idx, term) in enumerate(cmbaExpreterm1):
            r = random.randint(1,3)
            #not reversed
            if r % 2:
                cmbaExpreterm1[idx] = term
                continue
            #reversed
            if term[0] == "+":
                cmbaExpreterm1[idx] = "-" + term[1:]
            elif term[0] == "-":
                cmbaExpreterm1[idx] = "+" + term[1:]
            else:
                cmbaExpreterm1[idx] = "-" + term
        #construct the -1/1 * mbaexpre
        cmbaExpre1 = "".join(cmbaExpreterm1)
        if cmbaExpre1[0] == "+":
            cmbaExpre1 = cmbaExpre1[1:]

        #get part of the mbaexpre
        partterm = cmbaExpreterm2[:len(cmbaExpreterm2) // 2 + 1]
        #randomly reverse the sign of every term in cmbaexpre1
        for (idx, term) in enumerate(partterm):
            r = random.randint(1,3)
            #not reversed
            if r % 2:
                partterm[idx] = term
                continue
            #reversed
            if term[0] == "+":
                partterm[idx] = "-" + term[1:]
            elif term[0] == "-":
                partterm[idx] = "+" + term[1:]
            else:
                partterm[idx] = "-" + term
        #construct the part expression 
        partExpre ="".join(partterm) 
        if partExpre[0] == "+":
            partExpre = partExpre[1:]
        #construct a expression that equals to 0 
        groundtruth = str(0)
        zeroEquality = complex_groundtruth(groundtruth, partExpre)
        #0-equality = 0-expression * part_mbaexpre
        zeroEqualityList = self.MBA_multiply(cmbaExpre1, zeroEquality)
        zeroMBAexpre = zeroEqualityList[0]
        #newmba = orimba + 0-equality
        mbaExpre = addMBA(originalcmbaExpre, zeroMBAexpre)

        # #ground truth does not to be changed
        # gmbaExpreList = self.MBA_multiply(gmbaExpre1, gmbaExpre2)
        # #construct cmbaExpreList
        # cmbaExpreList = [mbaExpre, len(expression_2_term(mbaExpre)), 1]

        return mbaExpre



def pMBA_sort_by_term(fileread=None, filewrite=None):
    """sort the poly MBA expression.
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
        expre = expre.strip()
        itemList = re.split(",", expre)
        term = eval(itemList[3])
        expreList[idx] = [expre, term]

    #the sorted key is the terms of one expression
    expreList = sorted(expreList, key=lambda x: x[1])
    
    #output the sorted expression to new file
    flag = 0
    with open(filewrite, "wt") as fw:
        print("#complex,grountruth,z3flag,complex term, groundtruth term", file=fw)
        for expre in expreList:
            MBAexpre = expre[0]
            term = expre[1]
            if not flag:
                flag = term
                print("#{term}-terms complicated expression.".format(term=term), file=fw)
            elif flag != term:
                flag = term
                print("#{term}-terms complicated expression.".format(term=term), file=fw)

            print(MBAexpre, file=fw)

    return None


def groundtruth_2_pmba(groundtruth, vnumber=2):
    """given one ground truth, construct one related complex polynomial mba expression
    Algorithm:
        groundtruth * 1.
    Args:
        groundtruth: one mba expression defined by the users.
    Returns:
        expreStr: the related complex linear mba expression.
    """
    #get the number of variable in the expression
    vnumber1 = len(variable_list(groundtruth))
    if vnumber1 < vnumber:
        vnumber1 = vnumber
    vnumber2 = vnumber
    #for more complexity, complex the groundtruth
    mbaStr1 = groundtruth
    #mbaStr1 = complex_groundtruth(groundtruth)
    mbaStr2 = complex_groundtruth("1")
    #initialize the poly MBA generator
    cmbaList1 = [mbaStr1, mbaStr1]
    cmbaList2 = [mbaStr2, mbaStr2]
    pmbaObj = PolyMBAGenerator(vnumber1, vnumber2)
    #output one poly mba expression
    #resList = pmbaObj.generate_one_transform_pMBA(cmbaList1, cmbaList2)
    #pmbaExpre = resList[0][0]
    pmbaExpre = pmbaObj.generate_pMBA_from_zeroequality(groundtruth)
    z3res = verify_mba_unsat(pmbaExpre, groundtruth, 2)
    if not z3res:
        print("error in groundtruth to poly mba expression")
        traceback.print_stack()
        sys.exit(0)

    return pmbaExpre




def high_degree_MBA_generation(vnumber1, vnumber2, degree, mbanumber=100):
    """"one MBA expression on high degree generation by recursice method.
    Args:
        vnumber1: the number of variable of the dataset.
        vnumber2: the number of variable of the dataset.
        degree: the max degree of the generated expression.
    Returns;
        None.
        However, this function generates multiple middle file.
    """
    #the original two dataset
    fileread1 = "../dataset/lMBA_{vnumber}variable.dataset.sorted.txt".format(vnumber=vnumber1)
    fileread2 = "../dataset/lMBA_{vnumber}variable.dataset.sorted.txt".format(vnumber=vnumber2)

    for i in range(2, degree+1):
        #generate i-degree mba expression
        filewrite1 = "../dataset/pMBA_{vnumber1}_{vnumber2}variable.{degree}degree.transformation.dataset.txt".format(vnumber1=vnumber1, vnumber2=vnumber2, degree=i)
        pmbaObj = PolyMBAGenerator(vnumber1, vnumber2, fileread1, fileread2, filewrite1)
        pmbaObj.generate_pmba_transformation_dataset(mbanumber)
        #pmbaObj.generate_pmba_transformation_dataset(mbanumber)
        # (fileread1 * fileread2) * fileread2 * fileread2 * ....
        fileread1 = filewrite1
        filewrite2 = "../dataset/pMBA_{vnumber1}_{vnumber2}variable.{degree}degree.transformation.dataset.sorted.txt".format(vnumber1=vnumber1, vnumber2=vnumber2, degree=i)
        pMBA_sort_by_term(filewrite1, filewrite2)
        

    return None



def sort_dataset(vnumber1, vnumber2):
    """sort the dataset of poly MBA expression.
    """
    fileread = "../dataset/pMBA_{vnumber1}_{vnumber2}variable.dataset.txt".format(vnumber1=vnumber1, vnumber2=vnumber2)
    filewrite = "../dataset/pMBA_{vnumber1}_{vnumber2}variable.dataset.sorted.txt".format(vnumber1=vnumber1, vnumber2=vnumber2)
    pMBA_sort_by_term(fileread, filewrite)

    return None


def unittest(vnumber1, vnumber2, degree=2, mbanumber=100):
    #pmbaObj = PolyMBAGenerator(vnumber1, vnumber2)
    #pmbaObj.generate_pmba_dataset(mbanumber)
    #pmbaObj.generate_pmba_transformation_dataset(mbanumber)
    #high_degree_MBA_generation(vnumber1, vnumber2, degree, mbanumber)
    groundtruthList = ["x+y", "3", "x", "(x&y)"]
    for gt in groundtruthList:
        com = groundtruth_2_pmba(gt, vnumber=2)
        z3res = verify_mba_unsat(gt, com, 2)
        print(gt, com, z3res)

    #sort_dataset(vnumber1, vnumber2)

    return None



def main(vnumber1, vnumber2, degree, mbanumber):
    unittest(vnumber1, vnumber2, degree, mbanumber)

    return None




if __name__ == "__main__":
    vnumber1 = int(sys.argv[1])
    vnumber2 = int(sys.argv[2])
    if len(sys.argv) > 3:
        degree  = int(sys.argv[3])
    else:
        degree = 2
    if len(sys.argv) > 4:
        mbanumber = int(sys.argv[4])
    else:
        mbanumber = 100
    main(vnumber1, vnumber2, degree, mbanumber)



