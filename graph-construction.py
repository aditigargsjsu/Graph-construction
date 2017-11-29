

import time
start_time = time.time()
import math
import argparse

# -------------------- #
# Defining variables used in the code
# -------------------- #
number_of_documents=0
ptr=[]
ind=[]
val=[]
num_of_similarities_calculated=0
total_normalized_list=[]

# -------------------- #
# Taking the arguments as input from the CLI.
# Format to run the file is to run it as "python findsim.py -eps <eps-value> -k <k-value>"
# -------------------- #
parser = argparse.ArgumentParser(description='Process eps,k,input and output file')
parser.add_argument('-eps')
parser.add_argument('-k')
##parser.add_argument('-inputfile')
##parser.add_argument('-outputfile')
parser.add_argument('files', nargs='*')
args = parser.parse_args()

eps=float(args.eps)
k=int(args.k)
##inputfile=str(args.inputfile)
##outputfile=str(args.outputfile)
filelist = (args.files)
inputfile = filelist[0]
outputfile = filelist[1]
#print eps, k, inputfile, outputfile

# -------------------- #
# Defining functions
# -------------------- #
def find_csr_attributes(name_of_file):
    r'''Takes a term-frequency document like wiki1.csr and returns the csr matrix attributes like ptr, index, and value'''
##    nrows = len(docs)
##    idx = {}
##    tid = 0
##    nnz = 0
    global number_of_documents, ptr, val, ind, total_normalized_list
    docs = []
    with open (name_of_file, 'r') as f:
        for line in f:
            number_of_documents += 1 # Gives total number of documents in the file
            document_list = line.split()
            # -------------------- #
            # Now differentiate the term and frequency and convert it into a temp dictionary so each document becomes {term1:freq1, term2:freq2...}
            # -------------------- #
            x = len(document_list)
            y = 0
            temp_dictionary={}
            while y<x:
                temp_dictionary[int(document_list[y])]=int(document_list[y+1])
                y += 2
            #print temp_dictionary
            docs.append(temp_dictionary)
        #print docs
    # -------------------- #
    # Now each document in the file is converted as a list of dictionary and each document is defined as a term-frequency dict. Now, need to get the CSR matrix attributes        
    # -------------------- #
          
    ptr.append(0)
    i=0
    for i in range(number_of_documents):
            ptr.append(ptr[i] + len(docs[i]))
            for k in sorted(docs[i]):
                    ind.append(k)
                    val.append(docs[i][k])
                    
##            od = OrderedDict(sorted(docs[i].items()))  # This method to append to ind and val is very slow
##            for k,v in (od.items()):
##                ind.append(k)
##                val.append(v)

                    
##	print 'ptr is', ptr
##	print 'ind is', ind
##	print 'val is', val

def convert_to_normalized_document(document_id):
    r'''This function takes a document id number where originally the document is of the format {term1:freq1, term2:freq2...}
    and converts the frequencies(values) to become normalized. The document then becomes {term1:normalized_freq1, term2:normalized_freq2...}
    which is then returned'''
    global number_of_documents, ptr, val, ind, total_normalized_list
    # -------------------- #
    # taking the start and stop variables to make sure only the values of a particular document is taken
    # -------------------- #
    start_of_doc = ptr[document_id-1]
    stop_of_doc = ptr[document_id]
##    print start_of_doc
##    print stop_of_doc
    norm_freq = 0.0
    for i in range (start_of_doc,stop_of_doc):
        norm_freq +=  math.pow(val[i],2)
    norm_freq = math.sqrt(norm_freq)
    norm_freq = float("{0:.6f}".format(norm_freq))
    # -------------------- #
    # Now normalized frequency for the document is calculated which can be used to convert every frequency to be normalized
    # -------------------- #
    
    temp_dictionary = {}
    for i in range (start_of_doc,stop_of_doc):
        temp_dictionary[ind[i]] = val[i] / norm_freq
    return temp_dictionary

def cosine_similarity(d1,d2):
    r'''This function takes two document IDs as inputs and returns the cosine similarity between them.
        To do this, first the common terms between the two documents are found.
        Then Once common terms are found, their normalized frequencies are multiplied and added'''
    global num_of_similarities_calculated, total_normalized_list
    num_of_similarities_calculated += 1
    nd1 = total_normalized_list[d1-1]
    nd2 = total_normalized_list[d2-1]
    # -------------------- #
    # Calculating cosine similarities between two documents by finding the common terms between the two documents.
    # Once common terms are found, their normalized frequencies are multiplied and added.
    # -------------------- #
    common_terms=[]
    for k,v in nd1.items():
            if k in nd2:
                common_terms.append(k)
##                print common_terms
    cos_similarity = 0.0
    for i in common_terms:
        cos_similarity += (nd1[i]*nd2[i])
##    print cos_similarity
    cos_similarity = float("{0:.6f}".format(cos_similarity))
    return cos_similarity

def calculate_similarity_and_write(eps,k):
    r'''This function takes inputs of eps (minimum similarity needed based upon user input) and k (minimum number of neighbors based on user input)
        This function loops through all the documents in the given file, but skipping repeated similarity calculations becuase of the property of cosine similarity
        which states that cosine-similarity(document1, document2) is same as cosine-similarity(document2,document1)'''
    global number_of_documents
    # -------------------- #
    # Output file is opened to be written to
    # -------------------- #
    f=open(outputfile,'a+')
    # -------------------- #
    # Looping over all the documents and finding similarity with other documents, but avoiding repeatations
    # -------------------- #
    for i in range(1,number_of_documents+1):
        #print 'starting document number :'+str(i)+'at : '+str(time.time())
        temp_dictionary={}
        for j in range(i+1,number_of_documents+1):
            cos_similarity = cosine_similarity(i,j)
            if cos_similarity >=eps:
                #print i,j
                temp_dictionary[j]=cos_similarity
        #print temp_dictionary
        k_neighbors = sorted(temp_dictionary, key=temp_dictionary.get, reverse=True)[:k]
        #print k_neighbors

        
        # -------------------- #
        # If for a given document, eps and k conditions are met, then write to the file
        # -------------------- #
        if len(k_neighbors)>0:
            f.write(' ')
            for u in k_neighbors:
                f.write(str(u)+' '+str(temp_dictionary[u])+' ')
        f.write('\n')
        #print 'done with document number: '+str(i)+'at : '+str(time.time())
    f.close()

# -------------------- #
# End of defining functions
# -------------------- #



if __name__ == '__main__':
    find_csr_attributes(inputfile) # Calculate / convert input file to CSR matrix

    # -------------------- #
    # Normalizing the whole input file document in one go to prevent trying to normalize the same document twice during computing similarity.
    # total_normalized_list becomes a list of lists where each item represents one document with the frequencies L-2 normalized.
    # -------------------- #
    for p in range (1,number_of_documents+1):
        total_normalized_list.append(convert_to_normalized_document(p))
        
    calculate_similarity_and_write(eps,k) # Start knn search and write to the file.
    print ("Number of computed similarities = %s" % num_of_similarities_calculated)
    print ("Number of seconds taken = %s seconds" % ("{0:.4f}".format(time.time() - start_time)))
