#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Mon Sep  3 15:44:31 2018

@author: scott
"""

import numpy as np
import argparse

parser = argparse.ArgumentParser()
parser.add_argument('-f', "--InFile", required=True, help="filet output file")
parser.add_argument('-p1', "--prob1", type=float, default=0.90,
                    help="prob noIntrog")
parser.add_argument('-p2', "--prob2", type=float, default=0.95,
                    help="keep window with min prob")
args = parser.parse_args()


def clusterIntrogressedRegions(InFile, p1, p2):
    """

    """
    clustlist = []
    f = open("{}.bed".format(InFile), 'w')
    with open(InFile, 'r') as filet:
        next(filet)
        for line in filet:
            x = line.split()
            chrom = x[0]
            start = int(x[1])
            end = int(x[2])
            pred = x[4]
            noMig = float(x[5])
            mig12 = float(x[6])
            mig21 = float(x[7])
            if (1-noMig) >= p1:
                if pred == '1':
                    clustlist.append(mig12)
                    rollmean = p1
                    while rollmean >= p1:
                        line = next(filet)
                        end += int(line.split()[2])
                        clustlist.append(float(line.split()[6]))
                        rollmean = np.mean(clustlist)
                elif pred == '2':
                    clustlist.append(mig21)
                    rollmean = p1
                    while rollmean >= p1:
                        line = next(filet)
                        end += int(line.split()[2])
                        clustlist.append(float(line.split()[7]))
                        rollmean = np.mean(clustlist)
                elif pred == '0':
                    pl = [mig12, mig21]
                    ix = pl.index(max(pl)) + 6
                    clustlist.append(max(pl))
                    rollmean = p1
                    while rollmean >= p1:
                        line = next(filet)
                        end += int(line.split()[2])
                        clustlist.append(float(line.split()[ix]))
                        rollmean = np.mean(clustlist)
#                if max(clustlist) >= p2:
#                    f.write("{}\t{}\t{}\t{}\n".format(chrom, start, end, pred))
                f.write("{}\t{}\t{}\t{}\t{}\n".format(chrom, start, end, pred,
                                                      max(clustlist)))
            clustlist = []
    f.close()
    return(None)


if __name__ == "__main__":
    clusterIntrogressedRegions(args.InFile, args.prob1, args.prob2)
