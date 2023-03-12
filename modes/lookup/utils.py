#!/usr/bin/python3

import os
import bs4
import requests
import hashlib
import re
import urllib.parse

from generator import finish_processes
from googletrans import Translator as GTranslator

collection_folder=os.path.expanduser('~/.local/share/Anki2/kim/collection.media/')
header = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.97 Safari/537.36", 
  }

def save_temporarily(text, url, extension='jpg', processes=[]):
    image_name=f'{hashlib.md5(text.encode()).hexdigest()}.{extension}'
    image_path=f'{collection_folder}{image_name}'
    if os.path.isfile(image_path):
        return image_name, image_path
    image_path=f'/tmp/{image_name}'
    if not os.path.isfile(image_path):
        processes+=[('save', url, image_path)]
    return image_name, image_path

def synthesize_anki_image(text, processes=[]):
    image_name=f'{hashlib.md5(text.encode()).hexdigest()}.jpg'
    image_path=f'{collection_folder}{image_name}'
    if os.path.isfile(image_path):
        return image_name, image_path
    image_path=f'/tmp/{image_name}'
    if not os.path.isfile(image_path):
        processes+=[('generate_image', text, image_path)]
    return image_name, image_path

def synthesize_anki_sound(text, lan='en', processes=[]):
    sound_name=f'{hashlib.md5(text.encode()).hexdigest()}.wav'
    sound_path=f'{collection_folder}{sound_name}'
    if os.path.isfile(sound_path):
        return sound_name, sound_path
    sound_path=f'/tmp/{sound_name}'
    if not os.path.isfile(sound_path):
        processes+=[('generate_sound', text, sound_path, lan)]
    return sound_name, sound_path

def get_soup(word, lan):
    if lan=='en':
        url = urllib.parse.quote(f'dictionary.cambridge.org/us/dictionary/english/{word}')
        raw = requests.get('https://'+url, headers=header)
    elif lan=='de':
        url = 'https://www.wortbedeutung.info/%s/' % word
        raw = requests.get(url, headers=header)
    if raw.status_code != 200: return 
    html=raw.content
    soup=bs4.BeautifulSoup(html, 'lxml')
    return soup

def get_en_definition(word, soup):
    entries=(soup
             .find('div', class_='entry')
             .find_all('div', class_='pr entry-body__el')
             )

    notes=[]
    for entry in entries:
        uk_ipa=(entry
                .find('span', class_='uk dpron-i')
                .find('span', class_='pron dpron'))
        try:
            sound_url='https://dictionary.cambridge.org'+(
                    entry.find('span', class_='uk dpron-i')
                    .find('span', class_='daud')
                    .find('source')['src']
                    )
        except AttributeError:
            sound_url=''
        try:
            irregular=entry.find('span', class_='irreg-infls dinfls').text.strip()
        except:
            irregular=''
        try:
            grammar=entry.find('span', class_='gram dgram').text
            grammar=grammar.replace('[', '').replace(']', '').strip()
        except:
            grammar=''
        term=entry.find('span', class_=re.compile('hw .*hw')).text.strip()
        function=entry.find('span', class_='pos dpos').text.strip()

        blocks=entry.find_all('div', class_=re.compile('pr dsense.*'))

        base={
                'ipa':uk_ipa,
                'ipa_text': uk_ipa.text,
                'sound_url':sound_url,
                'sound_name': re.sub('.*/', '', sound_url),
                'function':function,
                'irregular': irregular,
                'grammar': grammar,
                'term': term,
                'image_url':'',
                'guide_word': '',
              }

        for block in blocks:
            base_guided=base.copy()
            try:
                guide_word=block.find('span', class_=re.compile('guideword .*gw')).span.text.strip()
                base_guided['guide_word']=guide_word
            except:
                pass

            try:
                image_url='https://dictionary.cambridge.org'+entry.find(
                        'div', class_='dimag')['amp-img']['src']
                base_guided['image_url']=image_url
            except:
                pass

            p_=block.find_all('div', class_=re.compile('pr phrase-block dphrase-block'))
            b_=block.find_all('div', class_='def-block ddef_block')

            for phrase in p_+b_:
                p=base_guided.copy()
                try:
                    p['term']=phrase.find('span', class_='phrase-title dphrase-title').text.strip()
                except:
                    pass

                p['meaning']=(block
                                 .find('div', class_=re.compile('def .*db'))
                                 .text
                                 .replace('\n', ' ')
                                 .replace(':', ' ')
                                 .strip())

                if p['meaning'] in [i['meaning'] for i in notes]: continue
                p['meaning_w']=re.sub(p['term']+'[^ ]*', ', this word, ', p['meaning'])

                # try:

                p['examples']=[]
                p['examples_w']=[]

                for f in phrase.find_all('div', class_='examp dexamp'):

                    f=f.text.strip()
                    p['examples']+=[f]
                    p['examples_w']+=[re.sub(f'{term}[^ ]*', ', this word, ', f)]

                tmp=block.find('div', class_='def-body ddef_b')
                tmp=tmp.find_all('div', class_='examp dexamp')
                for f in tmp:
                    f=f.text.strip()
                    if not f in p['examples']:
                        p['examples']+=[f]
                        p['examples_w']+=[re.sub(f'{term}[^ ]*', ', this word, ', f)]

                # except:
                #     pass

                notes+=[p.copy()]

    return notes

def get_de_definition(word, soup):
    types=soup.find_all(text=re.compile('^\s*Wortart: .*'))
    defs=[]
    for h in types:
        dt={'word':word}
        defs+=[dt]
        h=h.previous
        m=re.search('Wortart: (\w+)\W*\W*\(*(\w+)*\)*', h.text.strip())
        if m is None: continue
        dt['function']=m.group(1)
        sound_url=soup.find('iframe')
        if sound_url is not None:
            dt['sound_url']=get_sound_url(sound_url['src'])
        else:
            dt['sound_url']=None
        if dt['function']=='Substantiv': 
           if m.group(2) and m.group(2)=='weiblich':
               dt['article']='die'
           elif m.group(2) and m.group(2)=='männlich':
               dt['article']='der'
           elif m.group(2) and m.group(2)=='sächlich':
               dt['article']='das'
        else:
            dt['article']=''
        if dt['function']=='Verb' and m.group(2):
            dt['grammar']=m.group(2)
        for section in h.next_siblings:
            if section.name=='h3': break
            if section.name!='h4': continue
            if type(section)==bs4.element.NavigableString: continue
            text=section.next.next.text
            if 'Silbentrennung' in section.text:
                dt['formen']=(text
                        .replace('|', '')
                        .replace('\n', '')
                        .replace('Präteritum: ', '')
                        .replace('Partizip II: ', '')
                        .replace('Positiv', '')
                        .replace('Komparativ', '')
                        .replace('Superlativ', '')
                        )
                if 'Mehrzahl' in dt['formen']:
                    tmp=dt['formen'].split(':')
                    if len(tmp)==2:
                        dt['plural']=tmp[1].strip()
                    elif 'Variante' in dt['formen']:
                        dt['plural']=' '.join(re.findall('Variante ([^,]*)[,]*', dt['formen']))
                    else:
                        dt['plural']=''
            elif 'Aussprache' in section.text:
                dt['ipa']=(re.search('\[(.*)\]', text)
                        .group(1)
                        .replace('[', '')
                        .replace(']', '')
                        )
            elif 'Bedeutung' in section.text:
                meanings_w={}
                meanings={}
                m_list=[]
                try:
                    m_list=section.next.next.find_all('dd')
                except:
                    try:
                        m_list= section.next.next.next.next.next.next.next.next.next.find_all('dd')
                    except:
                        pass
                for m in m_list:
                    tmp=re.search('(\d+)[)] (.*)', m.text)
                    if tmp is None: continue
                    meanings[tmp.group(1)]=tmp.group(2)
                    meanings_w[tmp.group(1)]=tmp.group(2).replace(word, ', dieses Wort, ')
                dt['meanings']=meanings
                dt['meanings_w']=meanings_w
            elif 'Anwendungsbeispiele' in section.text or 'Beispielsätze' in section.text:
                examples={}
                m_list=section.next.next.find_all('dd')
                counter={}
                for m in m_list:
                    tmp=re.search('(\d+)[)] (.*)', m.text)
                    if tmp is None: continue
                    num=tmp.group(1)
                    html_text=str(m)
                    unfilled_example=re.sub('<em>[^>]*>', ', dieses Wort, ', html_text)
                    unfilled_example=re.sub('<[^>]*>', '', unfilled_example)
                    unfilled_example=re.sub('\d+\)', '', unfilled_example)
                    if not num in examples: examples[num]={}
                    example=tmp.group(2)
                    if num in counter and counter[num]>1: 
                        continue
                    elif num in counter:
                        counter[num]+=1
                        examples[num]['example_2']=example
                        examples[num]['example_2_w']=unfilled_example
                    else:
                        counter[num]=0
                        examples[num]['example_1']=example
                        examples[num]['example_1_w']=unfilled_example
                dt['examples']=examples
            elif 'Konjugation' in section.text:
                kon_forms=section.next.next.find_all('dd')
                k_forms={}
                for k in kon_forms:
                    tmp=k.text.split(':')
                    k_forms[tmp[0]]=tmp[1]
                dt['konjugation']=k_forms
            elif 'Steigerungen' in section.text:
                dt['steigerungen']=text
    return defs

def get_notes(word, lan):
    soup=get_soup(word, lan)
    if lan=='en':
        return get_en_definition(word, soup)
    elif lan=='de':
        return get_de_definition(word, soup)

def get_anki_notes(word, lan, processes=[]):
    notes=get_notes(word, lan)

    anki_notes=[]
    model_folder='Word_definition'

    if lan=='en':
        deck_folder='english::daily'
        for n in notes: 
            note = {
                'deckName': deck_folder,
                'modelName': model_folder,
                'fields': {
                    'UID': n['term']+n['meaning']+'test',
                    'IPA': str(n['ipa']), 
                    'ipa': n['ipa_text'],
                    'Word': n['term'],
                    'Word_s':'',
                    'Function': n['function'],
                    'Irregular': n['irregular'],
                    'Grammar': n['grammar'],
                    'Guide': n['guide_word'],
                    'Meaning': n['meaning'],
                    'Meaning_s': '',
                    'Meaning_w': n['meaning_w'],
                    'Meaning_w_s': '',
                    'Example I':'',
                    'Example I with placeholder':'',
                    'Example I sound':'',
                    'Example I with placeholder sound':'',
                    'Example II':'',
                    'Example II with placeholder':'',
                    'Example II sound':'',
                    'Example II with placeholder sound':'',
                    },
                }

            note['audio']=[]

            if n['sound_url']!='':
                s_n, s_p=save_temporarily(n['term'], n['sound_url'], extension='wav', processes=processes)
            else:
                s_n, s_p=synthesize_anki_sound(n['term'], processes=processes)

            note['audio']+=[{
                'path': s_p, 
                'filename': s_n,
                'fields': ['Sound', 'Word_s']
                }]

            m_name, m_path=synthesize_anki_sound(n['meaning'], processes=processes)
            note['audio']+=[
                {
                    'path': m_path,
                    'filename': m_name,
                    'fields': ['Meaning_s']
                },
                ]
            if n['meaning_w']!=n['meaning']:
                m_name, m_path=synthesize_anki_sound(n['meaning_w'], processes=processes)
            note['audio']+=[
                {
                    'path': m_path,
                    'filename': m_name,
                    'fields': ['Meaning_w_s']
                },
                ]

            if n['image_url']!='':
                image_name, image_path=save_temporarily(
                        n['meaning'], n['image_url'], processes)
                note['picture']={
                    'path' : image_path, 
                    'filename': image_name, 
                    'fields': ['Image']
                    }
            else:
                image_name, image_path=synthesize_anki_image(n['meaning'], processes)
                note['picture']={
                    'path' : image_path,
                    'filename': image_name,
                    'fields': ['Image']
                    }
            note['picture_loc']=image_path

            for i, example in enumerate(n['examples']):
                e_n, e_p=synthesize_anki_sound(example, processes=processes)
                ew_n, ew_p=synthesize_anki_sound(n['examples_w'][i], processes=processes)
                s="I"*(i+1)
                note['fields'][f'Example {s}']=example
                note['fields'][f'Example {s} with placeholder']=n['examples_w'][i]

                note['audio']+=[
                            {
                            'path': e_p,
                            'filename': e_n, 
                            'fields': [f'Example {s} sound']
                            },
                            {
                            'path': ew_p,
                            'filename': ew_n, 
                            'fields': [f'Example {s} with placeholder sound']
                            }
                            ]

            anki_notes+=[note]
    elif lan=='de':
        translator=GTranslator()
        deck_folder='german::daily'
        for dt in notes:
            if not 'meanings' in dt: continue
            for i, (key, value) in enumerate(dt['meanings'].items()):
                note = {
                    'deckName': deck_folder,
                    'modelName': model_folder,
                    'fields': {
                        'Word': word,
                        'UID': word + value + 'test',
                        'IPA': dt.get('ipa', ''),
                        'ipa': dt.get('ipa', ''),
                        'Function': dt.get('function', ''),
                        'Meaning': value,
                        'Meaning_w': dt['meanings_w'][key],
                        'Comparative': dt.get('steigerungen', ''),
                        'Gender': dt.get('article', ''),
                        'Plural': dt.get('plural', ''),
                        'Irregular': dt.get('formen', ''),
                        'Sound': dt.get('sound', ''),
                        'Grammar': dt.get('grammar', ''),
                        'Example I':'',
                        'Example I with placeholder':'',
                        'Example I sound':'',
                        'Example I with placeholder sound':'',
                        'Example II':'',
                        'Example II with placeholder':'',
                        'Example II sound':'',
                        'Example II with placeholder sound':'',
                        }
                    }

                value_en=translator.translate(value, dest='en').text
                image_name, image_path=synthesize_anki_image(value_en, processes)
                note['picture']={
                    'path' : image_path,
                    'filename': image_name,
                    'fields': ['Image']
                    }
                note['picture_loc']=image_path

                note['audio']=[]
                w_n, w_p=synthesize_anki_sound(word, 'de', processes)
                note['audio']+=[
                    {
                        'path': w_p,
                        'filename': w_n, 
                        'fields': ['Word_s', 'Sound']
                    },
                    ]

                w_n, w_p=synthesize_anki_sound(value, 'de', processes)
                note['audio']+=[
                    {
                        'path': w_p,
                        'filename': w_n, 
                        'fields': ['Meaning_s']
                    },
                    ]


                w_n, w_p=synthesize_anki_sound(dt['meanings_w'][key], 'de', processes)
                note['audio']+=[
                    {
                        'path': w_p,
                        'filename': w_n, 
                        'fields': ['Meaning_w_s']
                    }
                    ]

                if 'konjugation' in dt:
                    note['fields']['Imperative']=dt['konjugation'].get('Imperativ', '')
                    note['fields']['Conjunctive II']=dt['konjugation'].get('Konjunktiv II', '')
                    note['fields']['Help verb']=dt['konjugation'].get('Hilfsverb', '')

                
                if 'examples' in dt:
                    examples=dt['examples'][key]
                else:
                    examples=[]

                for i, example in enumerate(examples):
                    s='I'*(i+1)
                    if not f'example_{i+1}' in examples: break
                    note['fields'][f'Example {s}']=examples[f'example_{i+1}']
                    note['fields'][f'Example {s} with placeholder']=examples[f'example_{i+1}_w']

                    e_n, e_p=synthesize_anki_sound(examples[f'example_{i+1}'], 'de', processes)

                    note['audio']+=[
                                {
                                    'path': e_p, 
                                    'filename': e_n,
                                    'fields': [f'Example {s} sound']
                                },
                                ]

                    e_n, e_p=synthesize_anki_sound(examples[f'example_{i+1}_w'], 'de', processes)
                    note['audio']+=[
                                {
                                    'path': e_p, 
                                    'filename': e_n,
                                    'fields': [f'Example {s} with placeholder sound']
                                },
                                ]

                anki_notes+=[note]

    return anki_notes

def submit_to_anki(anki_notes):
    pass
