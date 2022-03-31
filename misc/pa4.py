# the structure of the program is roughly as such: 
# 
# body of the program
#     |  - contains calls of main(),
#     |    as well as the extra credit
#     |    usage of open()
#     |    
#     |    at this point the text is a multiline string.
#     |
#     main()
#         |  - runs processthem() which converts the 
#         |    multiline strings into usable arrays
#         |    of words and paragraphs, as well as 
#         |    a fencepost loop of calls to printpara(). 
#         |    
#         |    also adds the section symbol as an eol
#         |    character, via being the last item in a "paragraph"
#         | 
#         |    at this point the text is a list of lists,
#         |    with each smaller list having a paragraph 
#         |    of words, and the bigger list being
#         |    all the paragraphs. 
#         | 
#         printpara()
#             |  - while loop containing repeated 
#             |    calls to getline() and printline()
#             |     
#             |    at this point the text is a simple
#             |    list of all words in a paragraph.
#             |
#             getline() 
#                 |  - returns two lists, one containing the first 
#                 |    amount of words that don't cause character count 
#                 |    overflow, and the second containing the leftovers.
#                 |             
#             |  - feeds the returned first list to printline()
#             |      
#             |    at this point, the word list will be slowly reduced while 
#             |    within printpara until there's nothing left to print.
#             | 
#             printline()
#                 |  - calls addspace() to generate final format.
#                 |  
#                 |    at this point, the list items are modified to contain 
#                 |    the appropriate amount of spacing, then transformed
#                 |    into a string and printed.
#                 |  
#                 |    success! repeat until all text is printed. 
#   <-------------



# BEGIN PROGRAM

import sys, contextlib
from io import StringIO

class Data(object):
    pass

@contextlib.contextmanager
def capture_stdout():
    old = sys.stdout
    capturer = StringIO()
    sys.stdout = capturer
    data = Data()
    yield data
    sys.stdout = old
    data.result = capturer.getvalue()

# begin imports

from random import randint

# end imports


# begin function definitions

# obscure bugfix 
def insanelyLong(coolArr, cols):
    if max(len(item[0]) for item in coolArr) >= cols: 
        for i in range(len(coolArr)-1):
            coolArr[i].remove("§")
            print("\n".join(coolArr[i]))
            print()
        coolArr[-1].remove("§")
        print("\n".join(coolArr[-1]))        
        return True

# small utility function
def stringit(line):
    return (' '.join(line))

# calls addspace for one last round of formatting, then prints the formatted string
def printline(line: list, cols: int):
    if "§" not in line:
        line = addspace(line, cols)
    else:
        line.remove("§")
    if line: # fixes a bug where the separator was its own line
        print(stringit(line))
    
# rewrote this function because i wanted to get the before and the after so that the while loop is smoother. a little over-engineered but i think maybe more robust? has the benefit of not using pop() which is a function i don't know how to use 
def getline(words: list, cols: int):
    
    # initializing vars
    inForIt = True
    finalLine = []
    indexer = 0 
    # the above is the really important variable - as the function iterates, it adds one word at a time until we hit the length limit. i started using `stringit(line)` around here, because it meant i could use string-like tests on the line while keeping it in a conveniently mutable array form. i call len() on it several times.
    
    # yay while loops
    while inForIt:
        
        #this is to make sure that we're not trying to do this on an empty array, which sometimes happens in the case of end-of-paragraph lines. finalLine at this point is just `[]` so that works out nicely
        try: 
            words[indexer]
        except IndexError:
            return finalLine, []
        
        # if the length of the string concatenated with the word i want to add is not going to cause overflow, add it in. 
        if len(stringit(finalLine) + words[indexer]) < cols:
            finalLine.append(words[indexer])
            indexer += 1
        # if adding a word WILL cause overflow, then we've already hit our target, and we end the while loop here. 
        else: 
            inForIt = False  
            
    # i could have returned words[:indexer] and words[indexer:], because the point of this code is just to get the index. finalLine is a glorified test string. it also happens to be identical to words[:indexer], so it works for the output. 
    return finalLine, words[indexer:]

# simple function: while there are words left unprinted, keep printing
# having researched pop() i could have done this without repeatedly returning the `words` list, but this is fine as-is
def printpara(words: list, cols: int): # i defined all the params so strictly because i wanted my ide to recognize the types and help with linting 
    while words: 
        line, words = getline(words, cols)
        printline(line, cols)
    return

# this is definitely the most overcomplicated bit
def addspace(line: list, cols: int): 
    # value of how many chars away we are from the desired amount
    neededSpaces = cols - len(stringit(line))
    # array that looks like [0, 1, 2, 3, 4,...]. used to help even out distribution.
    testArr = list(range((stringit(line)).count(" ")))
    # array of places to add the spaces
    spacesIndexArr = []
    # number of times that every single space was expanded. helps to even out distribution.
    fullSweep = 0
    
    # if no needed spaces, we skip the loop entirely
    while neededSpaces: 
        reroll = True
        # reroll is used to ensure that no word gets "landed on" before every other word gets landed on at least once. 
        while reroll: 
            # quick test to ensure that there are even slots left to fill
            if spacesIndexArr == testArr:
                spacesIndexArr = []
                fullSweep += 1
            # roll the die! randLocale is secretly rolling which *index* of the list is going to be targeted
            randLocale = randint(0, (len(line)-2))
            
            # if this number is new, then that's it! if it's not, roll it again. 
            # the case where all possible numbers are already rolled is covered by the above conditional. 
            if randLocale not in spacesIndexArr:
                spacesIndexArr.append(randLocale)
                # the sorted() function is vital because then both lists can be directly compared without issues
                spacesIndexArr = sorted(spacesIndexArr)
                reroll = False
        neededSpaces -= 1 # if we need to roll another one, then we do! it stops at zero automatically. 
        
    # brief loops to impliment the spaces, now that we've determined where to put them
    # first loop is the specific elements we rolled
    for i in range(len(spacesIndexArr)):
        line[spacesIndexArr[i]] = line[spacesIndexArr[i]] + " "
    # second loop is applying the "full sweep" rolls, so spaces can be distributed evenly as possible.
    for i in range(fullSweep):
        for z in range(len(line)):
            line[z] = line[z] + " "
    # return modified list. will be slightly different each time
    return line

# utility function to convert the multiline string into paragraphs
def processThem(file: str):
    file = file.replace("\n\n", "§") # replace \n\n with the section symbol so that the carriage return obliterator doesn't cause issues
    file = file.replace("\n", " ") # obliterate carriage returns
    coolArr = file.split("§")
    for i in range(len(coolArr)):
        coolArr[i] = coolArr[i].split()
        coolArr[i].append("§") # now that we've split the paragraphs, add the section symbol back in for use in printline()
    return coolArr



def main(fileInp: str, cols: int):
    coolArr = processThem(fileInp) # turn multiline string into list of lists
    
    if not insanelyLong(coolArr, cols): # insanelyLong() is used to 'fix' the nonissue of words longer than entire lines. hacky solution, but keeping the 'word' intact is better than slicing it at the cols value, at least in my opinion. this is also outside the scope of the assignment and was mostly done for fun.
        
        # fencepost loop that calls the rest of the functions
        for i in range(len(coolArr)-1):
            printpara(coolArr[i], cols)
            print()
        printpara(coolArr[-1], cols)
        
    return

# end function definitions

# begin const definitions

# sorry for the walls of text, lol.

GETTY = """Four score and seven years ago our fathers brought forth on this continent,
a new nation, conceived in Liberty, and dedicated to the proposition that
all men are created equal.

Now we are engaged in a great civil war, testing whether that nation, or any
nation so conceived and so dedicated, can long endure. We are met on a great
battle-field of that war. We have come to dedicate a portion of that field,
as a final resting place for those who here gave their lives that that nation
might live. It is altogether fitting and proper that we should do this.

But, in a larger sense, we can not dedicate -- we can not consecrate -- we
can not hallow -- this ground. The brave men, living and dead, who struggled
here, have consecrated it, far above our poor power to add or detract. The
world will little note, nor long remember what we say here, but it can never
forget what they did here. It is for us the living, rather, to be dedicated
here to the unfinished work which they who fought here have thus far so nobly
advanced. It is rather for us to be here dedicated to the great task
remaining before us -- that from these honored dead we take increased devotion
to that cause for which they gave the last full measure of devotion -- that we
here highly resolve that these dead shall not have died in vain -- that this
nation, under God, shall have a new birth of freedom -- and that government of
the people, by the people, for the people, shall not perish from the earth."""

FILE = '''I am typing a bit of nonsense in order to test my text
justification program. The goal is to split a file into paragraphs
using a unique separator,
and then for each paragraph, split it into lines and add spaces so the
each line prints the same length.

We are ignoring punctuation and carriage returns.
The only caveat is that if the last line only has one word in it, it
should be left justified.

The goal of the program is to be a primitive simulation of one of the
functions of a word processor, the most ubiquitous of software
applications which used to have a vibrant ecosystem of variants, but
which has collapsed into a monopoly governed by Microsoft word.
Other parts of word processing require paging files into buffers,
spell checking, display management and keyboard processing.'''

# end const definitions

# begin program body

# "I am typing" example
# with capture_stdout() as capture:
#     main(FILE,40)
# print(capture.result)

# print("\n")
# main(FILE,60)
# print("\n\n")

# # Extra credit! Rather than rewrite main, I just call open() in the body.
# try: 
#     f = open("getty.txt")
#     getty = f.read()
# except: 
#     getty = GETTY

# # Gettysburg example, loaded from file.
# main(getty,40)
# print("\n")
# main(getty,60)

# end program body


# EXAMPLE OUTPUT: 
"""
I  am typing  a bit of nonsense in order
to test my  text justification  program.
The  goal  is   to  split  a  file  into 
paragraphs using a unique separator, and
then for  each paragraph,  split it into
lines  and  add spaces so the each  line
prints the same length.

We are ignoring punctuation and carriage
returns. The only caveat is  that if the
last  line only has one word  in it,  it
should be left justified.

The  goal  of  the  program  is to  be a
primitive  simulation   of  one  of  the 
functions of a word processor,  the most
ubiquitous  of   software   applications 
which used  to have  a vibrant ecosystem
of variants,  but  which  has  collapsed
into  a monopoly  governed  by Microsoft
word.  Other  parts  of word  processing
require paging files into buffers, spell
checking,    display   management    and  
keyboard processing.


I  am typing  a  bit  of  nonsense  in order to test my text
justification program.  The  goal is to  split  a  file into
paragraphs using a  unique  separator,  and  then  for  each
paragraph, split it  into lines and  add  spaces so the each
line prints the same length.

We  are ignoring punctuation and carriage returns.  The only
caveat  is that if the last line only has one word in it, it
should be left justified.

The goal of the program  is to be  a primitive simulation of
one  of  the  functions  of  a  word   processor,  the  most 
ubiquitous  of software applications  which  used  to have a
vibrant ecosystem of variants, but  which has collapsed into
a  monopoly governed by Microsoft word. Other parts of  word
processing   require  paging   files  into   buffers,  spell 
checking, display management and keyboard processing.



Four  score  and  seven  years  ago  our
fathers brought forth on this continent,
a new nation, conceived  in Liberty, and
dedicated  to  the proposition  that all
men are created equal.

Now we are engaged in a great civil war,
testing  whether  that  nation,  or  any
nation  so conceived  and  so dedicated,
can long endure. We  are met on a  great
battle-field of  that war.  We have come
to dedicate a portion of that  field, as
a final resting place for those who here
gave their lives that that  nation might
live.  It  is   altogether  fitting  and 
proper that we should do this.

But, in  a  larger  sense,  we  can  not
dedicate --  we can not consecrate -- we
can not hallow -- this ground. The brave
men,  living  and  dead,  who  struggled
here, have consecrated it, far above our
poor power to add or detract.  The world
will little note, nor long remember what
we  say  here,  but it can  never forget
what  they  did  here. It is for  us the
living,  rather, to be dedicated here to
the   unfinished  work  which  they  who 
fought  here  have  thus  far  so  nobly
advanced. It is rather for us to be here
dedicated  to the  great  task remaining
before  us  --  that from these  honored
dead we  take increased devotion to that
cause for which they gave  the last full
measure  of  devotion --  that  we  here
highly resolve that these dead shall not
have  died in vain -- that this  nation,
under God,  shall have  a new  birth  of
freedom  --  and that government  of the
people, by the  people, for  the people,
shall not perish from the earth.


Four score and seven  years ago our fathers brought forth on
this  continent, a  new  nation, conceived  in Liberty,  and
dedicated to the proposition that all men are created equal.

Now we are engaged  in  a great civil  war, testing  whether
that nation, or  any  nation so conceived  and so dedicated,
can  long endure. We are met on a great battle-field of that
war. We have come to dedicate a portion of that field,  as a
final resting place for those who here gave their lives that
that nation might live.  It is altogether fitting and proper
that we should do this.

But,  in a larger sense,  we  can not dedicate -- we can not
consecrate  -- we can  not hallow -- this ground. The  brave
men, living and dead, who struggled  here,  have consecrated
it, far above  our  poor power to add  or detract. The world
will little note, nor long remember what we say here, but it
can never  forget  what  they  did here.  It is  for us  the
living, rather, to be  dedicated here to the unfinished work
which they who fought here have  thus far so nobly advanced.
It  is rather for us to be  here dedicated to the great task
remaining  before us -- that from these honored dead we take
increased devotion to that cause  for  which  they gave  the
last full measure of devotion -- that we here highly resolve
that  these dead shall  not  have died in vain -- that  this
nation, under God, shall have  a new birth of freedom -- and
that  government  of the  people, by  the  people,  for  the
people, shall not perish from the earth.
"""
# end