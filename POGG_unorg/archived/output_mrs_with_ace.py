from delphin import ace
from delphin.codecs import simplemrs

# path to grammar
grammar_location = "/Users/lizcconrad/Documents/PhD/GP2/ERG_2023/erg-2023.dat"

# open sentences file
with open("sentences.txt") as sentences_file:
    sentences = sentences_file.readlines()

    # for each sentence, parse with ACE
    for s in sentences:
        with ace.ACEParser(grammar_location) as parser:
            response = parser.interact(s)
            for r in response.results():
                # decode gets the MRS object (this might be what you want for DMRS)
                mrs_object = simplemrs.decode(r['mrs'])
                # encode turns it into a string you can print
                mrs_text = simplemrs.encode(mrs_object, indent=True)
                print(mrs_text)
