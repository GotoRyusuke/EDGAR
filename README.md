# EDGAR
This is a project to:
- :heavy_check_mark: crawl firm statements & periodic reports from [EDGAR](https://www.sec.gov/edgar.shtml), a system constructed by SEC for firms to upload their statements & reports as well as for investors to check the operation of the firms they care;
- :heavy_check_mark: extract info about **risks** from the reports;specifically, it would be some **items** that we want to extract and analyse;
- :heavy_check_mark: train a **pharse2vec** model to get similar words for our dict at hand. It is a dict involving the conflict between Ukraine and Russia, and we want to expand that dict based on the contents of the reports filed by firms that may be affected by the conflic, and
- :heavy_check_mark: calculate some indicators using the expanded dict.

## Structure of the project
### 1.EDGAR CRAWLER
It would be not easy to crawl EDGAR without the help of a package from R called EDGAR. For the docs, check [`EDGAR` docs](https://cran.r-project.org/web/packages/edgar/index.html); for the paper introducing an example of how to use it, check [this paper](https://www.sciencedirect.com/science/article/pii/S2352711021001369) by the authors of the package. In the crawling procedure we simply use the well-packaged functions to capture overall filing info and download reports we need from EDGAR.

After the crawling is done, we define a func (check[`edgarCrawler`](./Crawling/edgarCrawler.R) for details) to help us record and export the filing info to an excel file, including firm CIK codes, filing date, file name, etc.

### 2. ITEM EXTRACTION
In this part, we develop several parser classes to extract specific items from different forms, namely:
- Item1A & Item7 under form 10-K;
- Part1 Item2 & PartII Item1A under form 10-Q, and
- Exhibit 99.1, Item2.02, Item7.01 & Item8.01 under form 8-K.

All 3 parsers utilise a class called [`matching_strategies`](./Parsers/matching_strategies.py) to match the start and end for each item. The `matching_strategies` is incorporated into each parser([`parsing8K`](./Parsers/parsing8K.py), [`parsing10K`](./Parsers/parsing10K.py), and [`parsing10Q`](./Parsers/parsing10Q.py)), and the forms saved in local dirs are parsed and the items needed are extracted and exported to txt files. Meanwhile, we add some methods to the parsers to record if the parsing and extraction is successful, as well as some dummies telling whether some words are mentioned in a certain item or not.


### 3. PHRASE2VEC
In [`trian_phrase2vec`](./Phrase2Vec/train_phrase2vec.py) we train a phrase2vec model based on the corpus constructed by merging all texts under 10-K Item1A and Item7, where a bigram transformer is adopted to recognise bigram or trigram phrases in the texts. After the training, we use [`get_similar`](./Phrase2Vec/get_similar.py) to expand our dict at hand, trying to find words or/and phrases that involve the conflict between Ukraine and Russia.

### 4. COUNTERS
In this part, we develop 2 counters to calculate word freqs in the forms we collect. The main logic is isolated to 2 classes called [`russia_counter`](./Counter/russia_counter.py) and [`russia_counter_lemma`](./Counters/russia_counter_lemma.py), and the procedures of going over all forms and calculating the word/phrase freqs are performed by [`russia_8k`](./Counter/russia_8k.py).

`russia_counter` calculates the word freq by exact words, i.e. only counting the word when it is in exactly the the form as in the dict. The `russia_counter_lemma`, however, counts the word when it has the same lemma as some words in the dict. The logic is almost the same, so you can go over only [`russia_counter_lemma`](./Counters/russia_counter_lemma.py) in detail as it has more comments to help you understand.
