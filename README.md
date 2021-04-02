### finegrained_datasets

This repository allows you to quickly download and process fine-grained structured sentiment datasets to a common JSON format, explained below.

We provide two scripts: get_data.sh and process_data.sh

There are some datasets which must be downloaded manually first (MPQA) and placed in the 'processed' folder before running process_data.sh.




## JSON format

Each sentence has a dictionary with the following keys and values:

* 'sent_id': unique NoReC identifier for document + paragraph + sentence which lines up with the identifiers from the document and sentence-level data, if available

* 'text': raw text

* 'opinions': list of all opinions (dictionaries) in the sentence

Each opinion in a sentence is a dictionary with the following keys and values:

* 'Source': a list of text and character offsets for the opinion holder

* 'Target': a list of text and character offsets for the opinion target

* 'Polar_expression': a list of text and character offsets for the opinion expression

* 'Polarity': sentiment label ('Negative', 'Positive')

* 'Intensity': sentiment intensity ('Standard', 'Strong', 'Slight')

* 'NOT': Whether the target is 'Not on Topic' (True, False)

* 'Target_is_general': (True, False)

* 'Type': Whether the polar expression is Evaluative (E) or Evaluative Fact Implied (EFINP)

```
{
    'sent_id': '202263-20-01',
    'text': 'Touchbetjeningen brukes også til å besvare innkomne mobilanrop , og Sennheiser skryter av å ha doble mikrofoner i øreklokkene for å kutte ned på støyen .',
    'opinions': [
                    {
                     'Source': [['Sennheiser'], ['68:78']],
                     'Target': [['øreklokkene'], ['114:125']],
                     'Polar_expression': [['skryter av å ha doble mikrofoner i øreklokkene for å kutte ned på støyen'], ['79:151']],
                     'Polarity': 'Positive',
                     'Intensity': 'Standard',
                     'NOT': False,
                     'Source_is_author': False,
                     'Target_is_general': True,
                     'Type': 'E'
                     }
                 ]
}
```

Note that a single sentence may contain several annotated opinions. At the same time, it is common for a given instance to lack one or more elements of an opinion, e.g. the holder (source). In this case, the value for that element is [[],[]].

## Importing the data

You can import the processed data (train.json, dev.json, and test.json) by using the json library in python:

```
>>> import json
>>> data = {}
>>> for name in ["train", "dev", "test"]:
        with open("{0}.json".format(name)) as infile:
            data[name] = json.load(infile)
