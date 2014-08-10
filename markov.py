import sys, os, re, random, operator

##############################

directory_in = ""
directory_out = ""
clump_size = 2
num_words = 20000
line_width = 80

##############################

help_text = """
 This is a tool for generating output text that is
 statistically similar to input text using a Markov
 chain.

 Syntax:
 markov.py <input directory> <output directory> (-num_words <#>)

 <input directory>
     Path to a directory with at least one input text file. For example:
     C:\\data\\text

 <output directory>
     Path where the output will be stored. For example:
     C:\\data\\output

 -clump_size <#>
     Optional argument to specify how many words should be grouped
     together when building the Markov chain. For example:
     -clump_size 2

     A value of "1" will pair single adjacent words together:
     "To" -> "be"
     
     A value of "2" (default) will pair couplets of words together:
     "To be" -> "or not"
     Etc.

 -num_words <#>
     Optional argument to specify the number of output clumps
     to generate (default 20000). For example:
     -num_words 10000

"""
lead_text = """
Markov Chain Text Generator
by Justin Libby   2014
"""

#####################################################

def print_help():
    global help_text
    print help_text
    exit(0)
    
#####################################################

def parse_args(args):
    global lead_text
    global directory_in
    global directory_out
    global num_words
    global clump_size
    
    if len(args) < 2:
        print_help()

    i = 0
    while i < len(args):
        # first arg is the name of the script
        if i > 0:
            if re.match('-num_words', args[i]):
                num_words = int(args[i+1])
                i += 1
                continue
            if re.match('-clump_size', args[i]):
                clump_size = int(args[i+1])
                i += 1
                continue
            if i == 1:
                directory_in = args[i]
            if i == 2:
                directory_out = args[i]
        i += 1

    if len(directory_in) == 0:
        print "Error: missing input directory"
        exit("Error: missing input directory")
    if len(directory_out) == 0:
        print "Error: missing output directory"
        exit("Error: missing output directory")
    if not os.path.exists(directory_in):
        print "Error: input directory " + directory_in + " does not exist"
        exit("Error: input directory " + directory_in + " does not exist")
    if num_words < 0:
        print "Error: number of generated words can not be negative"
        exit("Error: number of generated words can not be negative")
             

    print lead_text
    print "Input directory = " + directory_in
    print "Output directory = " + directory_out
    print "Clump size = " + str(clump_size)
    print "Number of words to generate = " + str(num_words)       

################################

def generate_markov_table(text, num_next):
    ret = {}
    i = 0;
    print "Creating Markov table from " + str(len(text)) + " words"
    while i < len(text) - 1 - (num_next * 2):
        s = ""
        spp = ""
        for j in range(num_next):
            s += text[i + j]
            spp += text[i + j + num_next]         
            if j < num_next - 1:
                s += " "
                spp += " "
               
        # Add this instance of word (s) followed by word (spp)
        if s in ret:
            if spp in ret[s]:
                ret[s][spp] += 1
            else:
                ret[s][spp] = 1
        else:
            ret[s] = {}
            ret[s][spp] = 1
        i += 1

    # print some stats
    keys = ret.keys()
    key_freq = []
    for k in keys:
        subkeys = ret[k].keys()
        total = 0
        for sk in subkeys:
            total += ret[k][sk]
        key_freq.append([k, total])
    # sort list by the frequency (second item)
    key_freq.sort(key=operator.itemgetter(1))
    print "Most numerous keys:"
    top_keys = key_freq[(len(key_freq) - 11):(len(key_freq) - 1)]
    top_keys.reverse()
    for s in top_keys:
        print "    \"" + s[0] + "\" appears " + str(s[1]) + " times"

    return ret

################################

def get_weighted_word(tbl, parent_key):
    keys = tbl.keys()

    total = 0
    for k in tbl:
        total += tbl[k]
    # total is the total number of instances
    # we have to choose from
    if total == 1:
        # only one entry, so pick it
        return keys[0]
    else:
        rnd_idx = random.randint(0, total - 1)

    cur_idx = 0
    for k in tbl:
        for i in range(tbl[k]):
            if rnd_idx == cur_idx:
                return k
            cur_idx += 1
            
    print "Failed to get weighted output word for parent key: " + parent_key
    return ""

################################

def generate_markov_text(tbl, num_out):
    global line_width
    
    keys = tbl.keys()
    num_keys = len(keys)
    print "Generating text from " + str(num_keys) + " source keys"
    rnd_idx = random.randint(0, num_keys - 1)
    print "Starting at random index " + str(rnd_idx)
    rnd_key = keys[rnd_idx]
    print "First word clump: " + str(rnd_key)

    ret = rnd_key
    word = rnd_key
    counter = 0
    num_random = 0
    line_count = 0
    for i in range(num_out):
        if word in tbl:
            new_word = get_weighted_word(tbl[word], word)
        else:
            new_word = keys[random.randint(0, num_keys - 1)]
            num_random += 1
           
        if len(new_word) > 0:
            word = new_word
            ret += " " + new_word
            line_count += len(new_word) + 1
        else:
            word = keys[random.randint(0, num_keys - 1)]
            num_random += 1
        # sprinkle in some new line characters
        if line_count > line_width:
            ret += "\n"
            line_count = 0
        counter += 1

    print "Had to choose " + str(num_random) + " random word clumps out of " + str(num_out) + " output word clumps"   
    return ret   

################################

def get_file_list():
    global directory_in

    ret = []
    print "Found the following input files:"
    for one_file in os.listdir(directory_in):
        if one_file.endswith(".txt"):
             print "    " + one_file
             file_name = directory_in + "\\" + one_file
             ret.append(file_name)
    return ret

################################

def read_input():
    files_in = get_file_list()

    text_in_unclean = ""
    for f in files_in:
        fi = open(f, 'r')
        text_in_unclean += fi.read() + " "
        fi.close()

    print "Characters of input text : " + str(len(text_in_unclean))

    # remove irrelevant ASCII characters
    text_in = ""
    for c in text_in_unclean:
        if ord(c) > 126:
            text_in += " "
            continue
        if ord(c) < 32:
            text_in += " "
            continue
        text_in += c
    text_in = re.sub('\n', ' ', text_in)
    text_in = re.sub('\t', ' ', text_in)
    text_in = re.sub('\.', ' ', text_in)
    text_in = re.sub(',', ' ', text_in)
    text_in = re.sub('\?', ' ', text_in)
    text_in = re.sub('!', ' ', text_in)
    text_in = re.sub('"', ' ', text_in)
    text_in = re.sub(';', ' ', text_in)
    text_in = re.sub('=', ' ', text_in)
    text_in = re.sub('~', ' ', text_in)
    text_in = re.sub('\\\\', ' ', text_in)
    text_in = re.sub('/', ' ', text_in)
    print "Characters of cleaned text : " + str(len(text_in))

    # Split out words based on whitespace
    #words = re.split('\W+', text_in)
    words = re.split(' ', text_in)

    fixed_words = []
    for word in words:
        w = word.strip()
        if not w:
            continue
        fixed_words.append(w)

    # Print out some samples of the input
    example_idx = []
    for i in range(10):
        example_idx.append(random.randint(0, len(fixed_words)))
    print "Example input words: "
    for i in example_idx:
        print "    " + fixed_words[i]

    return fixed_words

################################

def write_output(text_out):
    global directory_out
   
    file_out = directory_out + "\\" + "output.txt"
    print "Writing output to file: " + file_out
    fo = open(file_out, 'w')
    # put periods before capital letters
    # XXX - make this a post-processing step?
    text_out = re.sub(r"([A-Z][a-z])", r". \1", text_out)
    text_out = re.sub(r"( \.)", r".", text_out)
    fo.write(text_out)
    fo.close()
    
################################
    
def write_log(markov_table):
    global directory_out
    
    log_out = directory_out + "\\" + "log.txt"
    print "Writing log to file: " + log_out
    # write out statistics about the markov table
    fo = open(log_out, 'w')
    fo.write("FirstWord\tSecondWord\tFrequency\n")
    for k in markov_table:
        for s in markov_table[k]:
            fo.write(k + "\t" + s + "\t" + str(markov_table[k][s]) + "\n")
    fo.close()    

##################################

parse_args(sys.argv)
word_array_in = read_input()
markov_table = generate_markov_table(word_array_in, clump_size)
text_out = generate_markov_text(markov_table, num_words)
write_output(text_out)
write_log(markov_table)
