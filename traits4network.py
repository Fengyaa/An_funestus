#!/usr/bin/env python2
# -*- coding: utf-8 -*-
"""
Created on Tue Oct 23 19:04:26 2018
# blast
blastn -query FASTA -db ../../blasted/nt_db/nt -num_threads 10 -max_target_seqs 1 -dust no -task blastn -outfmt '6 qseqid sseqid evalue bitscore length pident qcovs sgi sacc staxids sscinames scomnames stitle' > blastn.out
# key
cut -f 1,6,7,13 blastn.out | cut -d" " -f 1-2 | sort -k1,1 -u > Locus.Key
# replace well in fasta
's/>[A-H][0-9][0-9]_/>/g'
# replace ab1 in fasta
's/\.ab1//g'
# align
mafft --auto --quiet --thread -10 --preservecase Ancoustani.IDs.CO1.fa > Ancoustani.IDs.CO1.aln
# abgd, filter lengths
~/programs_that_work/Abgd/abgd -d 0 -a ../CO1_Karama_28SEP18.clean.lab.long.aln.fa
# ITS2
~/programs_that_work/dnaclust_linux_release3/dnaclust -i ITS2_Karama_28SEP18.clean.lab.fa -l -s .964 -a |
@author: stsmall
"""

import argparse
parser = argparse.ArgumentParser()
parser.add_argument("--file", type=str, required=True)
parser.add_argument("--fx", type=str, required=True)
args = parser.parse_args()


# Sample %ID LenQ Gen Sp fastaID
def label(File):
    """
    """
    f = open("{}.label".format(File), 'w')
    sp_count = 0
    with open(File, 'r') as co1:
        line = next(co1)
        species = line.split()[4]
    with open(File, 'r') as co1:
        for line in co1:
            x = line.split()
            if x[4] == species:
                sp_count += 1
                species_count = "{}_{}".format(x[4], sp_count)
                x.append(species_count)
                f.write("{}\n".format("\t".join(x)))
            else:
                sp_count = 1
                species_count = "{}_{}".format(x[4], sp_count)
                x.append(species_count)
                f.write("{}\n".format("\t".join(x)))
                species = x[4]
    f.close()
    return(None)


def prctIDcutoff(File, cutoff):
    """
    """
    f = open("{}.prctIDcutoff".format(File), 'w')
    with open(File, 'r') as co1:
        for line in co1:
            x = line.split()
            if float(x[2]) > cutoff:
                x[3] = x[1]
                f.write("{}\n".format("\t".join(x)))
            else:
                x = line.split()
                f.write("{}\n".format("\t".join(x)))
    f.close()
    return(None)


def replaceFastaHeader(File, fasta):
    """
    """
    fastadict = {}
    with open(File, 'r') as co1:
        for line in co1:
            x = line.split()
            fastadict[x[0]] = x[-1]
    f = open("{}.rename".format(fasta), 'w')
    with open(fasta, 'r') as co1:
        for line in co1:
            if line.startswith(">"):
                x = line.strip()[1:]
                f.write(">{}\n".format(fastadict[x]))
            else:
                f.write(line)
    f.close()
    return(None)


def AddLengthsToKey(File, fastafai):
    """required samtools faidx fasta
    """
    lendict = {}
    with open(fastafai, 'r') as fai:
        for line in fai:
            x = line.split()
            length = x[1]
            lendict[x[0]] = length
    f = open("{}.lengths".format(File), 'w')
    with open(File, 'r') as co1:
        for line in co1:
            x = line.split()
            x.append(lendict[x[3]])
            f.write("{}\n".format("\t".join(x)))
    f.close()
    return(None)


def AddGroupsFromABGD(File, abgdFile):
    """
    """
    groupdict = {}
    with open(abgdFile, 'r') as group:
        for line in group:
            x = line.split()
            for i in x[4:]:
                groupdict[i] = x[1]
    f = open("{}.groups".format(File), 'w')
    with open(File, 'r') as co1:
        for line in co1:
            x = line.split()
            try:
                x.append(groupdict[x[3]])
                f.write("{}\n".format("\t".join(x)))
            except KeyError:
                x.append("NAN")
                f.write("{}\n".format("\t".join(x)))
    f.close()
    return(None)


def AddtraitsForNetwork(File, header):
    """
    cut -f2 CO1_Karama_28SEP18.clean.lab.alignment.long.log > duplist
    cut -d" " -f 1 CO1_Karama_28SEP18.clean.lab.alignment.long.phy > list
    grep -wv -f duplist list > singletons
    cat CO1_Karama_28SEP18.clean.lab.alignment.long.log singletons > log.log2
    """
    #header = ["aconitus", "barbirostris", "nitidus", "peditaeniatus", "maculatus",
     #         "tessellatus", "culicifacies", "vagus", "crawfordi", "unknown"]
    f = open("{}.traits".format(File), 'w')
    f.write("{}\n".format(",".join(header)))
    headerlist = [0] * len(header)
    sp = ''
    with open(File, 'r') as log:
        log.next()  # skip header
        for line in log:
            if line.startswith("\t"):
                spix = header.index(line.split()[0].split("_")[0])
                headerlist[spix] += 1
            else:
                if sum(headerlist) > 0:
                    f.write("{},{}\n".format(sp, ",".join(map(str, headerlist))))
                sp = line.split()[0]
                headerlist = [0] * len(header)
                headerlist[header.index(sp.split("_")[0])] += 1
    # print last one
    sp = line.split()[0]
    headerlist = [0] * len(header)
    headerlist[header.index(sp.split("_")[0])] += 1
    f.write("{},{}\n".format(sp, ",".join(map(str, headerlist))))
    f.close()
    return(None)


if __name__ == "__main__":
    File = args.file
    if args.fx == 'label':
        label(File)
    elif args.fx == 'prctIDcutoff':
        co = raw_input("Float for cutoff: ")
        prctIDcutoff(File, co)
    elif args.fx == 'replaceFastaHeader':
        fa = raw_input("Add Fasta file: ")
        replaceFastaHeader(File, fa)
    elif args.fx == 'AddLengthsToKey(File, fastafai)':
        fai = raw_input("Add fai file: ")
        AddLengthsToKey(File, fai)
    elif args.fx == 'AddGroupsFromABGD':
        abgd = raw_input("Add ABDG file: ")
        AddGroupsFromABGD(File, abgd)
    elif args.fx == 'AddtraitsForNetwork':
        header = raw_input("Add header as list")
        # make this a list
        AddtraitsForNetwork(File, header)
