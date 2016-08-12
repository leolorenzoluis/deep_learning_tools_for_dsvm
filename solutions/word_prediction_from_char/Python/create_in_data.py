from azure.storage.blob import BlobService
import numpy as np
import requests
import csv

AZ_KEY = "4zc1X3kvBH22tv6vhn47rJn+lIRQOJfJfPHrdHvXE/AspzhghiDYOY0W/BgKeDxgfzymPu9CMt0iFhmc7HfOwQ=="
AZ_ACC = "amazonsentimenik"
AZ_CONTAINER = "textclassificationdatasets"
ALPHABET = "abcdefghijklmnopqrstuvwxyz0123456789-,;.!?:'\"/\\|_@#$%^&*~`+ =<>()[]{}"
FEATURE_LEN = 1014 
cdict = dict((c, i + 2) for i, c in enumerate(ALPHABET)) # first index for 'other' and blank for 'padding'
print("We have %d tokens" % len(cdict))
print(cdict)

def download_file(url):
    print('downloading data')
    local_filename = url.split('/')[-1]
    blob_service = BlobService(AZ_ACC, AZ_KEY)
    file = blob_service.get_blob_to_path(AZ_CONTAINER,
                                         local_filename,
                                         local_filename,
                                         max_connections=5)
    print('saved data')

def create_features(infile, outfile):
    # Get data from windows blob
    download_file('https://amazonsentimenik.blob.core.windows.net/%s' % infile)
    with open(outfile, 'w') as outy:
        writer = csv.writer(outy, lineterminator='\n')
        writer.writerow(['class'] + ["v%d" % (d+1) for d in range(FEATURE_LEN)])
        with open(infile, 'r', encoding="utf8") as iny:
            # use summary and review columns
            reader = csv.DictReader(iny, fieldnames=['class','summary','review'])
            for r in reader:
                sample = np.ones(FEATURE_LEN+1) # initialise all as other char
                # Put characters in reverse order
                count = FEATURE_LEN
                for col in ['summary','review']:
                    for char in r[col].lower():
                        if char in cdict:
                            sample[count] = cdict[char]
                        count -= 1
                        if count == 1:
                            break
                sample[0] = int(r['class']) - 1 
                writer.writerow(sample)

                        
if __name__ == '__main__':
    create_features(infile='amazon_review_polarity_test.csv', outfile='test_char_cnn.csv')
    print("saved test")
    create_features(infile='amazon_review_polarity_train.csv', outfile='train_char_cnn.csv')
    print("saved train")