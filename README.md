# spamfilter

usage: spamfilter.py [-h] [--ham HAM] [--spam SPAM] [--mail MAIL] [-o OUTPUT]
                     [-m MODEL] [-a {mi-logistic,mi-svm}] [-l LIMIT]
                     [-d DICTLIMIT] [-r RAMLIMIT]
                     {model,test}

Create a spamfilter model or apply a created filter. Create a model:
```bash
python spamfilter.py --ham ham.p --spam spam.p -o model.p model -a mi-logistic -l 5000 -d 5000
```
Test a model:
```bash
python spamfilter.py --mail mail.mbox -m model.p test -o tagged.mbox -l 10000
```

If the testing cmd takes MBOX as source then it
separates the messages into two MBOXes. If the output is provided, then it
creates tagged MBOX.

positional arguments:
  {model,test}          Set program mode

optional arguments:
  -h, --help            show this help message and exit
  --ham HAM             A file containing HAM.
  --spam SPAM           A file containing SPAM
  --mail MAIL           A file containing unsorted mail
  -o OUTPUT, --output OUTPUT
                        output file
  -m MODEL, --model MODEL
                        model file
  -a {mi-logistic,mi-svm}, --algo {mi-logistic,mi-svm}
                        Select training algorithms.
  -l LIMIT, --limit LIMIT
                        Import set limit - memory limitation
  -d DICTLIMIT, --dictLimit DICTLIMIT
                        Max dictionary size
  -r RAMLIMIT, --ramLimit RAMLIMIT
                        Set RAM limit (MB) -- OOM prevent.


Tento projekt byl podpořen studentským fakultním grantem (SFG) Matematicko-fyzikální fakulty Univerzity Karlovy.
