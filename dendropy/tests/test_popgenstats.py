#! /usr/bin/env python

############################################################################
##  test_tree_io.py
##
##  Part of the DendroPy library for phylogenetic computing.
##
##  Copyright 2008 Jeet Sukumaran and Mark T. Holder.
##
##  This program is free software; you can redistribute it and/or modify
##  it under the terms of the GNU General Public License as published by
##  the Free Software Foundation; either version 3 of the License, or
##  (at your option) any later version.
##
##  This program is distributed in the hope that it will be useful,
##  but WITHOUT ANY WARRANTY; without even the implied warranty of
##  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##  GNU General Public License for more details.
##
##  You should have received a copy of the GNU General Public License along
##  with this program. If not, see <http://www.gnu.org/licenses/>.
##
############################################################################

"""
Tests input/output of trees from files.
"""

import unittest
import StringIO
import math
from dendropy import get_logger
from dendropy import datasets


### MODULES THAT WE ARE TESTING ###
from dendropy import popgenstats
### MODULES THAT WE ARE TESTING ###


class PopGenStatsTests(unittest.TestCase):
    
    def test1(self): 

#         s1 = StringIO.StringIO("""
#     #NEXUS 
#     
#     Begin data;
#         Dimensions ntax=4 nchar=55;
#         Format datatype=dna gap=-;
#         Matrix
#     seq_1 ATATACGGGGTTA---TTAGA----AAAATGTGTGTGTGTTTTTTTTTTCATGTG
#     seq_2 ATATAC--GGATA---TTACA----AGAATCTATGTCTGCTTTCTTTTTCATGTG
#     seq_3 ATATACGGGGATA---TTATA----AGAATGTGTGTGTGTTTTTTTTTTCATGTG
#     seq_4 ATATACGGGGATA---GTAGT----AAAATGTGTGTGTGTTTTTTTTTTCATGTG
#         ;
#     End;
#     """)
#         d = datasets.Dataset()    
#         d.read(s1, "NEXUS")
#         print popgenstats.average_number_of_pairwise_differences(d.char_blocks[0],
#             ignore_uncertain=True)
#         print popgenstats.nucleotide_diversity(d.char_blocks[0], 
#             ignore_uncertain=True)
#             
#         s2 = StringIO.StringIO("""
# #NEXUS 
# 
# BEGIN TAXA;
# 	DIMENSIONS NTAX=60;
# 	TAXLABELS
#         T01
#         T02
#         T03
#         T04
#         T05
#         T06
#         T07
#         T08
#         T09
#         T10
#         T11
#         T12
#         T13
#         T14
#         T15
#         T16
#         T17
#         T18
#         T19
#         T20
#         T21
#         T22
#         T23
#         T24
#         T25
#         T26
#         T27
#         T28
#         T29
#         T30
#         T31
#         T32
#         T33
#         T34
#         T35
#         T36
#         T37
#         T38
#         T39
#         T40
#         T41
#         T42
#         T43
#         T44
#         T45
#         T46
#         T47
#         T48
#         T49
#         T50
#         T51
#         T52
#         T53
#         T54
#         T55
#         T56
#         T57
#         T58
#         T59
#         T60
# 	;	
# END;
# 
# BEGIN CHARACTERS;
# 	DIMENSIONS NCHAR=407;
# 	FORMAT DATATYPE=DNA GAP=-;
# 	MATRIX
#         T01  ATTAGCACCCAAAGCTAAGATTCTAATTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACTATCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCATCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCTTTCTCGTCCCCATGGATGACCCCCC
#         T02  ???????????????????????????????????????????TCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCCATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCATCCTTAACAGTACATGGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T03  ??????????????????????????TTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATCTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCATACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T04  ????????????????????????????????????????????????????????????????????????????????????????ACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCCCCTCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCATCCTTAACAGTACATGGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTCCTCGTCCCCATGGATGACCCCC?
#         T05  ???????????????????????????????????TTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAGCAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T06  ??????????????????????????TTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCCATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGTCA-CCCCTCACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCACGGATGACCCCC?
#         T07  ????????????????????TTCTAATTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCA??????????????????????????????ATGCTTACAAGCAAGTACAGCAATCGACCCTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T08  ??????????????????????????????????????TCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGTCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T09  ?????????????????????TCTAATTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTCACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCC??
#         T10  ??????????????????????????????AACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T11  ????????????????????????????????CTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T12  ??????????????????????????????????????????TTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCTCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAGGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T13  ????????????????????????????????????????TGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATCTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCATACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCACGGATGACCCCCC
#         T14  ??????????????????????????????????????????TTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T15  ???????????????????????????????????????????????????????????????????GTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T16  ??????????????????????????TTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T17  ????????????????????TTCTAATTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATCTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCATACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGA??????
#         T18  ????????????????????????????????????????TGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTAACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGAT????????
#         T19  ??????????????????????????????????????TCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACAGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGTCA-CCTCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCACGGATGACCCCC?
#         T20  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACAGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCCCCTCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGTCA-CCTCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCACGGATGACCCCCC
#         T21  ???????????????????????????????ACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACAGTACCATAAATACTTGACTACCTGTAGTACATAAAAACTCAAC--CCACATCAAAA-----CCCTGCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTGTCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGCACATAAAGTCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T22  ???????????????????????????????ACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCCTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T23  ?????????????????????????ATTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAGCCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCGATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTCACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T24  ????????????????????????????????????????????????????????????????????TACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGCACAGCAATCAACCCTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCC?
#         T25  ??????????????????????????????AACTATTCTCTGTTCTTTCATGGGGAAGCGGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T26  ??????????????????????????????AACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCAACATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T27  ?????????????????????????????AAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTATCCATCCTTAACAGTACATGGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T28  ???????????????????????????????????TTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATCTCGTACATTACTGCCAGCCACCATGAATATTGTACAGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAA???????????CCCCCATGCTTACAAGCAAGCACAGCGATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTGCCCATCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTTGTCCCCATGGATGAC?????
#         T29  ????????????????????????????????CTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAA????????????????????????????????????????????????????????????????????????CCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T30  ??????????????????????????????AACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAC--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCRCCCTTAACAGTACATAGCACATAAAACCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T31  ??????????????????????????????????????TCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCA???????????????CCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCATCCTTAACAGTACATGGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T32  ??????????????????????????????????????????TTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCAACATGAATATTGTACAGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAACAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTGCAGTCAAATCCTTTCTCGCCCCCATGGATGACCCCCC
#         T33  ?????????????????????????????????????????????TTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCTCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCAT????????????
#         T34  ?????????????????????????????????????????????????????????GCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACTACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCCC
#         T35  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCAACATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGAATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T36  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCCATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAACCAACCTTCAACTATCACACATCAACTGCAACTCCAAGGCCA-CCCCTTACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T37  ??????????????????????????????????????TCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAATCCAAT--CCACATCAAAA-----CCCCCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T38  ?????????????????????????????????????????????TTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGCACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCCC
#         T39  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCCC
#         T40  ????????????????????????????????????TCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCAGCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T41  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATCTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAACAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCATCCTTAACAGTACATGGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T42  ????????????????????????????????????????????????????????????????????????????????????????????ATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCATACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T43  ??????????????????????????????????????????????????????????????????????CCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCTAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGCACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCC??????????????
#         T44  ??????????????????????????????????????????????????????????????????GGTGCCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCAACATGAATATTGTACAGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAACAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAGACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTTCAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCCC
#         T45  ???????????????????????????????????TTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCC???
#         T46  ?????????????????????????????????????CTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGCACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T47  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCAGCATGAATATTGCACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGAATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCC??????????????
#         T48  ????????????????????????????????????????TGTTCTTTCATGGGGAAGCAGATTTGGGTGCCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T49  ???????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????ATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATTAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCTACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCTTTCTCGTCCCCATGGATGACCCCCC
#         T50  ????????????????????TTCTAATTTAAACTATTCTCTGTTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAACAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGG??????????
#         T51  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAACAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCATCCTTAACAGTACATGGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCCC
#         T52  ???????????????????????????????????????????????????????AAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGCACGGTACCATAAATACTTAACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCC??
#         T53  ??????????????????????????????????????????TTCTTTCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGAATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T54  ??????????????????????????????????????????????????????????????????GGTGCCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T55  ???????????????????????????????????????????????????????????????????????????????????????????????AACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCCC
#         T56  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCTCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCCC
#         T57  ???????????????????????????????????????????????????GGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATCGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAG?ATATCAACAAACCTACCCACCCTTAACAGYACATAGYACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGYCCCCATGGATGACCCCCC
#         T58  ???????????????????????????????????????????????TCATGGGGAAGCAGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATACCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGTCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGATGACCCCC?
#         T59  ??????????????????????????????????????????????????????????????????GGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCCCCTCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTCACCCACTAGGATATCAACAAACCTACCCACCCTTAACAGTACATAGTACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGTCCCCATGGAT????????
#         T60  ???????????????????????????????????????????????????????????AGATTTGGGTACCACCCAAGTATTGACTCACCCATCAACAACCGCTATGTATTTCGTACATTACTGCCAGCCACCATGAATATTGTACGGTACCATAAATACTTGACCACCTGTAGTACATAAAAACCCAAT--CCACATCAAAA-----CCTTCCCCCCATGCTTACAAGCAAGTACAGCAATCAACCTTCAACTATCACACATCAACTGCAACTCCAAAGCCA-CCCCTTACCCATTAGGATATCAACAAACCTACCCGCCCTTAACAGTACATAGCACATAAAGCCATTTACCGTACATAGCACATTACAGTCAAATCCCTTCTCGCCCCCATGGATGACCCCC?	
#     ;
# END;
# """)
#         print    
#         d = datasets.Dataset()    
#         d.read(s2, "NEXUS")
#         print popgenstats.average_number_of_pairwise_differences(d.char_blocks[0], 
#             ignore_uncertain=True)
#         print popgenstats.nucleotide_diversity(d.char_blocks[0], 
#             ignore_uncertain=True)
#         print
    
        s3 = StringIO.StringIO("""
    #NEXUS 
    
    BEGIN TAXA;
        DIMENSIONS NTAX=12;
        TAXLABELS
            Lemur_catta        	
            Homo_sapiens       	
            Pan                	
            Gorilla            	
            Pongo              	
            Hylobates          	
            Macaca_fuscata     	
            Macaca_mulatta     	
            Macaca_fascicularis	
            Macaca_sylvanus    	
            Saimiri_sciureus   	
            Tarsius_syrichta   	
        ;	
    END;
    
    BEGIN CHARACTERS;
        DIMENSIONS NCHAR=474;
        FORMAT DATATYPE=DNA GAP=-;
        MATRIX
    Lemur_catta             AAGCTTCATAGGAGCAACCATTCTAATAATCGCACATGGCCTTACATCATCCATATTATTCTGTCTAGCCAACTCTAACTACGAACGAATCCATAGCCGTACAATACTACTAGCACGAGGGATCCAAACCATTCTCCCTCTTATAGCCACCTGATGACTACTCGCCAGCCTAACTAACCTAGCCCTACCCACCTCTATCAATTTAATTGGCGAACTATTCGTCACTATAGCATCCTTCTCATGATCAAACATTACAATTATCTTAATAGGCTTAAATATGCTCATCACCGCTCTCTATTCCCTCTATATATTAACTACTACACAACGAGGAAAACTCACATATCATTCGCACAACCTAAACCCATCCTTTACACGAGAAAACACCCTTATATCCATACACATACTCCCCCTTCTCCTATTTACCTTAAACCCCAAAATTATTCTAGGACCCACGTACTGTAAATATAGTTTAAA
    Homo_sapiens            AAGCTTCACCGGCGCAGTCATTCTCATAATCGCCCACGGGCTTACATCCTCATTACTATTCTGCCTAGCAAACTCAAACTACGAACGCACTCACAGTCGCATCATAATCCTCTCTCAAGGACTTCAAACTCTACTCCCACTAATAGCTTTTTGATGACTTCTAGCAAGCCTCGCTAACCTCGCCTTACCCCCCACTATTAACCTACTGGGAGAACTCTCTGTGCTAGTAACCACGTTCTCCTGATCAAATATCACTCTCCTACTTACAGGACTCAACATACTAGTCACAGCCCTATACTCCCTCTACATATTTACCACAACACAATGGGGCTCACTCACCCACCACATTAACAACATAAAACCCTCATTCACACGAGAAAACACCCTCATGTTCATACACCTATCCCCCATTCTCCTCCTATCCCTCAACCCCGACATCATTACCGGGTTTTCCTCTTGTAAATATAGTTTAAC
    Pan                     AAGCTTCACCGGCGCAATTATCCTCATAATCGCCCACGGACTTACATCCTCATTATTATTCTGCCTAGCAAACTCAAATTATGAACGCACCCACAGTCGCATCATAATTCTCTCCCAAGGACTTCAAACTCTACTCCCACTAATAGCCTTTTGATGACTCCTAGCAAGCCTCGCTAACCTCGCCCTACCCCCTACCATTAATCTCCTAGGGGAACTCTCCGTGCTAGTAACCTCATTCTCCTGATCAAATACCACTCTCCTACTCACAGGATTCAACATACTAATCACAGCCCTGTACTCCCTCTACATGTTTACCACAACACAATGAGGCTCACTCACCCACCACATTAATAACATAAAGCCCTCATTCACACGAGAAAATACTCTCATATTTTTACACCTATCCCCCATCCTCCTTCTATCCCTCAATCCTGATATCATCACTGGATTCACCTCCTGTAAATATAGTTTAAC
    Gorilla                 AAGCTTCACCGGCGCAGTTGTTCTTATAATTGCCCACGGACTTACATCATCATTATTATTCTGCCTAGCAAACTCAAACTACGAACGAACCCACAGCCGCATCATAATTCTCTCTCAAGGACTCCAAACCCTACTCCCACTAATAGCCCTTTGATGACTTCTGGCAAGCCTCGCCAACCTCGCCTTACCCCCCACCATTAACCTACTAGGAGAGCTCTCCGTACTAGTAACCACATTCTCCTGATCAAACACCACCCTTTTACTTACAGGATCTAACATACTAATTACAGCCCTGTACTCCCTTTATATATTTACCACAACACAATGAGGCCCACTCACACACCACATCACCAACATAAAACCCTCATTTACACGAGAAAACATCCTCATATTCATGCACCTATCCCCCATCCTCCTCCTATCCCTCAACCCCGATATTATCACCGGGTTCACCTCCTGTAAATATAGTTTAAC
    Pongo                   AAGCTTCACCGGCGCAACCACCCTCATGATTGCCCATGGACTCACATCCTCCCTACTGTTCTGCCTAGCAAACTCAAACTACGAACGAACCCACAGCCGCATCATAATCCTCTCTCAAGGCCTTCAAACTCTACTCCCCCTAATAGCCCTCTGATGACTTCTAGCAAGCCTCACTAACCTTGCCCTACCACCCACCATCAACCTTCTAGGAGAACTCTCCGTACTAATAGCCATATTCTCTTGATCTAACATCACCATCCTACTAACAGGACTCAACATACTAATCACAACCCTATACTCTCTCTATATATTCACCACAACACAACGAGGTACACCCACACACCACATCAACAACATAAAACCTTCTTTCACACGCGAAAATACCCTCATGCTCATACACCTATCCCCCATCCTCCTCTTATCCCTCAACCCCAGCATCATCGCTGGGTTCGCCTACTGTAAATATAGTTTAAC
    Hylobates               AAGCTTTACAGGTGCAACCGTCCTCATAATCGCCCACGGACTAACCTCTTCCCTGCTATTCTGCCTTGCAAACTCAAACTACGAACGAACTCACAGCCGCATCATAATCCTATCTCGAGGGCTCCAAGCCTTACTCCCACTGATAGCCTTCTGATGACTCGCAGCAAGCCTCGCTAACCTCGCCCTACCCCCCACTATTAACCTCCTAGGTGAACTCTTCGTACTAATGGCCTCCTTCTCCTGGGCAAACACTACTATTACACTCACCGGGCTCAACGTACTAATCACGGCCCTATACTCCCTTTACATATTTATCATAACACAACGAGGCACACTTACACACCACATTAAAAACATAAAACCCTCACTCACACGAGAAAACATATTAATACTTATGCACCTCTTCCCCCTCCTCCTCCTAACCCTCAACCCTAACATCATTACTGGCTTTACTCCCTGTAAACATAGTTTAAT
    Macaca_fuscata          AAGCTTTTCCGGCGCAACCATCCTTATGATCGCTCACGGACTCACCTCTTCCATATATTTCTGCCTAGCCAATTCAAACTATGAACGCACTCACAACCGTACCATACTACTGTCCCGAGGACTTCAAATCCTACTTCCACTAACAGCCTTTTGATGATTAACAGCAAGCCTTACTAACCTTGCCCTACCCCCCACTATCAATCTACTAGGTGAACTCTTTGTAATCGCAACCTCATTCTCCTGATCCCATATCACCATTATGCTAACAGGACTTAACATATTAATTACGGCCCTCTACTCTCTCCACATATTCACTACAACACAACGAGGAACACTCACACATCACATAATCAACATAAAGCCCCCCTTCACACGAGAAAACACATTAATATTCATACACCTCGCTCCAATTATCCTTCTATCCCTCAACCCCAACATCATCCTGGGGTTTACCTCCTGTAGATATAGTTTAAC
    Macaca_mulatta          AAGCTTTTCTGGCGCAACCATCCTCATGATTGCTCACGGACTCACCTCTTCCATATATTTCTGCCTAGCCAATTCAAACTATGAACGCACTCACAACCGTACCATACTACTGTCCCGGGGACTTCAAATCCTACTTCCACTAACAGCTTTCTGATGATTAACAGCAAGCCTTACTAACCTTGCCCTACCCCCCACTATCAACCTACTAGGTGAACTCTTTGTAATCGCGACCTCATTCTCCTGGTCCCATATCACCATTATATTAACAGGATTTAACATACTAATTACGGCCCTCTACTCCCTCCACATATTCACCACAACACAACGAGGAGCACTCACACATCACATAATCAACATAAAACCCCCCTTCACACGAGAAAACATATTAATATTCATACACCTCGCTCCAATCATCCTCCTATCTCTCAACCCCAACATCATCCTGGGGTTTACTTCCTGTAGATATAGTTTAAC
    Macaca_fascicularis     AAGCTTCTCCGGCGCAACCACCCTTATAATCGCCCACGGGCTCACCTCTTCCATGTATTTCTGCTTGGCCAATTCAAACTATGAGCGCACTCATAACCGTACCATACTACTATCCCGAGGACTTCAAATTCTACTTCCATTGACAGCCTTCTGATGACTCACAGCAAGCCTTACTAACCTTGCCCTACCCCCCACTATTAATCTACTAGGCGAACTCTTTGTAATCACAACTTCATTTTCCTGATCCCATATCACCATTGTGTTAACGGGCCTTAATATACTAATCACAGCCCTCTACTCTCTCCACATGTTCATTACAGTACAACGAGGAACACTCACACACCACATAATCAATATAAAACCCCCCTTCACACGAGAAAACATATTAATATTCATACACCTCGCTCCAATTATCCTTCTATCTCTCAACCCCAACATCATCCTGGGGTTTACCTCCTGTAAATATAGTTTAAC
    Macaca_sylvanus         AAGCTTCTCCGGTGCAACTATCCTTATAGTTGCCCATGGACTCACCTCTTCCATATACTTCTGCTTGGCCAACTCAAACTACGAACGCACCCACAGCCGCATCATACTACTATCCCGAGGACTCCAAATCCTACTCCCACTAACAGCCTTCTGATGATTCACAGCAAGCCTTACTAATCTTGCTCTACCCTCCACTATTAATCTACTGGGCGAACTCTTCGTAATCGCAACCTCATTTTCCTGATCCCACATCACCATCATACTAACAGGACTGAACATACTAATTACAGCCCTCTACTCTCTTCACATATTCACCACAACACAACGAGGAGCGCTCACACACCACATAATTAACATAAAACCACCTTTCACACGAGAAAACATATTAATACTCATACACCTCGCTCCAATTATTCTTCTATCTCTTAACCCCAACATCATTCTAGGATTTACTTCCTGTAAATATAGTTTAAT
    Saimiri_sciureus        AAGCTTCACCGGCGCAATGATCCTAATAATCGCTCACGGGTTTACTTCGTCTATGCTATTCTGCCTAGCAAACTCAAATTACGAACGAATTCACAGCCGAACAATAACATTTACTCGAGGGCTCCAAACACTATTCCCGCTTATAGGCCTCTGATGACTCCTAGCAAATCTCGCTAACCTCGCCCTACCCACAGCTATTAATCTAGTAGGAGAATTACTCACAATCGTATCTTCCTTCTCTTGATCCAACTTTACTATTATATTCACAGGACTTAATATACTAATTACAGCACTCTACTCACTTCATATGTATGCCTCTACACAGCGAGGTCCACTTACATACAGCACCAGCAATATAAAACCAATATTTACACGAGAAAATACGCTAATATTTATACATATAACACCAATCCTCCTCCTTACCTTGAGCCCCAAGGTAATTATAGGACCCTCACCTTGTAATTATAGTTTAGC
    Tarsius_syrichta        AAGTTTCATTGGAGCCACCACTCTTATAATTGCCCATGGCCTCACCTCCTCCCTATTATTTTGCCTAGCAAATACAAACTACGAACGAGTCCACAGTCGAACAATAGCACTAGCCCGTGGCCTTCAAACCCTATTACCTCTTGCAGCAACATGATGACTCCTCGCCAGCTTAACCAACCTGGCCCTTCCCCCAACAATTAATTTAATCGGTGAACTGTCCGTAATAATAGCAGCATTTTCATGGTCACACCTAACTATTATCTTAGTAGGCCTTAACACCCTTATCACCGCCCTATATTCCCTATATATACTAATCATAACTCAACGAGGAAAATACACATATCATATCAACAATATCATGCCCCCTTTCACCCGAGAAAATACATTAATAATCATACACCTATTTCCCTTAATCCTACTATCTACCAACCCCAAAGTAATTATAGGAACCATGTACTGTAAATATAGTTTAAA
        ;
    END;
    """)
        d = datasets.Dataset()    
        d.read(s3, "NEXUS")
        assert abs(popgenstats.average_number_of_pairwise_differences(d.char_blocks[0], ignore_uncertain=True) - 111.0606) < 0.001
        assert abs(popgenstats.nucleotide_diversity(d.char_blocks[0], ignore_uncertain=True) - 0.2343) < 0.001


        

if __name__ == "__main__":
    unittest.main()        
        