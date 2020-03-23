import os,sys
import csv
from nltk.stem import WordNetLemmatizer
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.corpus import stopwords
from collections import namedtuple
import pickle
import glob
import string

# document object
Document = namedtuple("Document", "name content sentiment location")
ADJ = ["JJ", "JJR", "JJS"]
ADV = ["RB", "RBR", "RBS"]
NOUN = ["NN", "NNS", "NNP", "NPS"]
VERB = ["VB", "VBG", "VBD", "VBN", "VBP", "VBZ"]

# this class contains basic text processing methods
# it also contains basic file processing methods, such as reading and writing
class Preprocessor():

    def __init__(self, dir):
        self.dir = dir
        self.lemmatizer = WordNetLemmatizer()


    # perform basic text processing
    def basic_preprocess(self, text):

        #step 1: lower the text
        text = text.lower()

        # step 2: sentence tokenize the text for easy processing
        # this also removes extra white spaces between sentences
        sentences = sent_tokenize(text)

        concise_sentences = []

        for s in sentences:
            # step 3: word tokenize
            # this also remove extra white spaces in a word
            words = [w for w in word_tokenize(s)]

            # step 4: remove stopwords
            stop_removed = [w for w in words if w not in set(stopwords.words('english'))]

            #step 5: remove punctuations
            punct_removed = [w for w in stop_removed if w not in string.punctuation]

            #step 6: remove digits
            digit_removed = [w for w in punct_removed if not w.isdigit()]

            # step 7: lemmatize
            stemmed = [self.lemmatizer.lemmatize(w) for w in digit_removed]

            # dot is added at the end
            # to keep structure of sentences
            ns = " ".join(stemmed) + "."

            concise_sentences.append(ns)

        return " ".join(concise_sentences)


    # this method creates a tabular file if it does not exist
    # it also adds a header for the table
    def create_tabular_file(self, file, header):
        if not os.path.isfile(file):
            with open(file, 'w', encoding='utf8', newline='') as writer:
                csvwriter = csv.writer(writer)
                csvwriter.writerow(header)

    # this method counts the number of lines in a file
    def count_lines(self, file):
        with open(file, 'r', encoding='utf8') as reader:
            return sum(1 for line in reader)


    def run(self):
        files = [os.path.basename(x) for x in glob.glob(f"{self.dir}/data/*.csv")]

        done_files = [f.strip() for f in open(f"{self.dir}/preprocessing_done.txt", 'r').readlines()] \
            if os.path.isfile(f"{self.dir}/preprocessing_done.txt") else []
        tbp_files = [f for f in files if f not in done_files]


        os.makedirs(os.path.dirname(f"{self.dir}/results/"), exist_ok=True)

        for file in tbp_files:
            documents = []

            rownum = self.count_lines(f"{self.dir}/data/{file}")

            with open(f"{self.dir}/data/{file}", 'r', encoding='utf8') as reader:
                csvreader = csv.DictReader(reader)

                rowid = 0
                for row in csvreader:

                    #put cleaned reviews in pos or neg dict
                    rating = int(row['review_star'])
                    sentiment = "pos" if rating > 30 else "neg"

                    #reflect in the dictionary which city a review comes from
                    city = row['reviewer_location'].strip().lower()
                    location = "sgp" if "singapore" in city else "non" if city == "" else "ovs"

                    text = f"{row['review_title']}. {row['review_content']}"
                    cleaned_text = self.basic_preprocess(text)

                    if not cleaned_text.isspace():
                        documents.append(Document(file, cleaned_text, sentiment, location))


                    rowid += 1.0
                    print("\r", end='')
                    print("Processing in progress",int(rowid*100/rownum),"% for",file,end='',flush=True)

            pickle.dump(documents, open(f"{self.dir}/results/{file.replace('.csv','.pickle')}", "wb"))

            with open(f"{self.dir}/preprocessing_done.txt","a",encoding="utf8") as writer:
                writer.write(f"{file}\n")

if __name__ == "__main__":
    #file_dir = sys.argv[1]
    file_dir = "tfidf_preprocess"
    ppc = Preprocessor(file_dir)
    ppc.run()