import os
import sys
# import regex
import re
# from pprint import pprint
import subprocess
import shutil
# import sys


def main(args):
    defaultsuffix = '-mod'
    bibname = modify_aux(args[2], suffix=defaultsuffix)
    modify_bib(bibname, suffix=defaultsuffix, runanyway=True)
    dothebibtex(args[1],
                bibname,
                args[2],
                suffix=defaultsuffix,
                runanyway=True)


def modify_aux(auxname, suffix='-mod'):
    print(f'modding {auxname} ...')
    basefname = auxname.replace('.aux', '')
    bibname = None
    auxorgname = basefname+'.aux'
    auxmodname = basefname+suffix+'.aux'

    try:
        fauxorg = open(auxorgname, 'r', encoding="utf-8")
        fauxout = open(auxmodname, 'w', encoding="utf-8")

        line = True
        while (line):
            line = fauxorg.readline()
            linstr = line.strip()

            if 'bibdata' in linstr:
                # print(linstr)
                bibname = linstr.replace(r'\bibdata{','').replace('}','')
                linstr = linstr.replace('}', suffix+'}')
                # print(linstr)

            fauxout.writelines(linstr)
            fauxout.writelines('\n')
    finally:
        fauxorg.close()
        fauxout.close()
        return bibname


def modify_bib(bibbasename, suffix='-mod', runanyway=False):
    orgfname = bibbasename+'.bib'
    outfname = bibbasename+suffix+'.bib'
    print(f'modding {orgfname} ...')

    # check the date of original and modded bib
    orgtime = os.stat(orgfname).st_mtime
    modtime = 0
    try:
        modtime = os.stat(outfname).st_mtime
    except:
        print(f'no such file: {outfname} but do we need to care?')

    if runanyway:
        orgtime = float('inf')
    # if original is newer...
    if (modtime < orgtime):  # larger is newer
        try:
            forg = open(orgfname, 'r', encoding="utf-8")
            fout = open(outfname, 'w', encoding="utf-8")

            # p = regex.compile(r'\p{Script=Han}+')
            # define the Kanji name as below
            # it may be better to use regex module...
            kanjiname = re.compile(r'[一-龥]+.,[ ,一-龥,ぁ-ん,[ァ-ン]]+')

            line = True
            while (line):
                line = forg.readline()
                linstr = line.strip()
                knamelist = kanjiname.findall(linstr)

                if all([('author' in linstr),
                        ('='      in linstr),
                        ('}'      in linstr),
                        0 < len(knamelist)
                        ]):  # if the author line contains kanji...
                    for kname in knamelist:
                        # remove ', ' from author entry
                        _kname_mod = kname.replace(', ','')
                        _kname_mod = _kname_mod.replace(',','')
                        linstr = linstr.replace(kname, _kname_mod)
                        print(f'modified \"{kname}\" to \"{_kname_mod}\"')

                fout.writelines(linstr)
                fout.writelines('\n')
        except:
            print(f'something went wrong while reading {orgfname} and writing to {outfname}')
            return 1
        finally:
            forg.close()
            fout.close()
            return 0


def dothebibtex(bibtexcommand, bibbasename, auxname, suffix='-mod', runanyway=False):
    auxbasefname = auxname.replace('.aux', '')
    auxorgname = auxbasefname+'.aux'
    auxmodname = auxbasefname+suffix+'.aux'
    
    orgfname = bibbasename+'.bib'
    outfname = bibbasename+suffix+'.bib'

    # check the date of original and modded bib
    orgtime = os.stat(orgfname).st_mtime 
    modtime = 0

    try:
        modtime = os.stat(outfname).st_mtime 
    except:
        print(f'no such file: {outfname}')

    if runanyway:
        orgtime = float('inf')
    # if original is newer...
    if (modtime < orgtime):  # larger is newer

        _bibtex = shutil.which(bibtexcommand)
        print(f'running {_bibtex} {auxmodname}')
        res = subprocess.run([_bibtex, auxmodname], stdout=subprocess.PIPE)
        print(res.stdout)

        # change the bbl file back to the neame it should be
        modbblfname = auxbasefname + suffix+'.bbl'
        orgbblfname = auxbasefname + '.bbl'
        print(f'overriding {orgbblfname} (if exists) by {modbblfname}')
        os.replace(modbblfname, orgbblfname)

        # latexmk returns harmless (but still annoying) error without the line below
        os.replace(auxbasefname + suffix+'.blg',auxbasefname + '.blg')



# exec main
if __name__ == '__main__':
    args = sys.argv
    if any([not ('bibtex' in args[1]), not ('.aux' in args[2])]):
        print('usage:  python3 pyjbibtex.py $actualbibtexprogram $auxfile')
        print('        intended for use inside latexmk')
        print('        define $bibtex like below inside your latexmkrc')
        print('sample line for latexmkrc:')
        print('        $bibtex=\'python3 path/to/your/pyjbibtex.py bibtex %O %S\'')
    main(args)
