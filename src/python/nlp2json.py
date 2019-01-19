import argparse
import json
import bs4
import urllib
from os.path import realpath, dirname, join

from spaCy2JSON import process as spacy_process

default_outfile = 'nlp_output.json'
here = dirname(realpath(__file__))
pipelines = {
    'spacy': spacy_process
}


def write_file(data, name):
    with open(name, 'w') as fp:
        json.dump(data, fp, sort_keys=False, indent=4)
    print('wrote to {}'.format(name))


#HTML visible text extractor
def tag_visible(element):
    if element.parent.name in ['style', 'script', 'head', 'title', 'meta', '[document]']:
        return False
    if isinstance(element, bs4.element.Comment):
        return False
    return True


def text_from_html(body):
    soup = bs.BeautifulSoup(body, 'html.parser')
    texts = soup.findAll(text=True)
    visible_texts = filter(tag_visible, texts)
    return u" ".join(t.strip() for t in visible_texts)





if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='NLP2Json')
    parser.add_argument('pipeline', type=str, help='which nlp pipeline to use')
    parser.add_argument('input_type', type=str, choices=['text', 'file', 'website'])
    parser.add_argument('input', type=str)
    args = parser.parse_args()

    if args.input_type == "text":
        print('parsing...')
        j = pipelines[args.pipeline](args.input)
        write_file(j, join(here, default_outfile))
    elif args.input_type == 'file':
        for file in args.input.split(','):
            print('parsing {}...'.format(file))
            out_file = '{}.json'.format(file)
            text = ''
            with open(join(here, file), 'r') as f:
                for line in f:
                    text += line
            j = pipelines[args.pipeline](text)
            write_file(j, join(here, out_file))
    elif args.input_type == 'website':
        print('not implemented')

    print('done')

    url_path = "https://www.google.com"
    print('Parsing html link {}'.format(url_path))

    # sauce = requests.get(url_path)
    html = urllib.request.urlopen(url_path).read()
    print(text_from_html(html))
