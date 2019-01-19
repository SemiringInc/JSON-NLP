#!/usr/bin/env python3
from collections import Counter

import spacy
import json
import datetime

# nlp = spacy.load('en_core_web_lg')
nlp = spacy.load('en')


def process(text):
    doc = nlp(text)
    j = {
        "conformsTo": 0.1,
        'source': 'SpaCy {}'.format(spacy.__version__),
        "created": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "date": datetime.datetime.now().replace(microsecond=0).isoformat(),
        "dependenciesBasic": [],
        "expressions": [],
        "text": text,
        "sentences": []
    }

    token_list = []
    lang = Counter()
    sent_lookup = {}
    token_lookup = {}

    # tokens and sentences
    token_offset = 0
    for sent_num, sent in enumerate(doc.sents):
        current_sent = {
            'id': sent_num,
            'text': sent.text,
            'tokenFrom': token_offset,
            'tokenTo': token_offset + len(sent),
            'tokens': []
        }
        sent_lookup[sent.text] = sent_num
        j['sentences'].append(current_sent)
        for token in sent:
            t = {
                'id': token_offset,
                'text': token.text,
                'lemma': token.lemma_,
                'pos': token.pos_,
                'entity': token.ent_type_,
                'entity_iob': token.ent_iob_,
                'overt': True,
                'characterOffsetBegin': token.idx,
                'characterOffsetEnd': token.idx + len(token)
            }
            lang[token.lang_] += 1
            token_lookup[(sent_num, token.i)] = token_offset
            current_sent['tokens'].append(token_offset)
            token_offset += 1
            token_list.append(t)
        current_sent['tokenFrom'] = current_sent['tokens'][0]
        current_sent['tokenTo'] = current_sent['tokens'][-1]
    j['tokenList'] = token_list

    # noun phrases
    entity_id = 0
    for chunk in doc.noun_chunks:
        sent_id = sent_lookup[chunk.sent.text]
        e = {
            'id': entity_id,
            'type': 'NP',
            'head': token_lookup[(sent_id, chunk.root.i)],
            'dep': chunk.root.dep_,
            'tokens': []
        }
        for token in chunk:
            e['tokens'].append(token_lookup[(sent_id, token.i)])
        for token in chunk.rights:
            e['tokens'].append(token_lookup[(sent_id, token.i)])
        j['expressions'].append(e)
        entity_id += 1

    # dependencies
    for sent_num, sent in enumerate(doc.sents):
        for token in sent:
            j['dependenciesBasic'].append({
                'type': token.dep_,
                'governor': token_lookup[(sent_num, token.head.i)],
                'dependent': token_lookup[(sent_num, token.i)],
            })

    j['lang'] = max(lang)

    return j


if __name__ == "__main__":
    test = "Autonomous cars from the countryside of France shift insurance liability toward manufacturers. People are afraid that they will crash."

    with open('spaCy.json', 'w') as fp:
        json.dump(process(test), fp, sort_keys=True, indent=4)
