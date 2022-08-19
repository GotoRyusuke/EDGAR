# -*- coding: utf-8 -*-
'''
DESCRIPTION
-----------
A module of two matching strategies to be used in finding the starts and ends for 
different items, depending on the type of form to be parsed.

CONTENTS
--------
- <FUNC> cut_uncreadable
- <CLASS> item_detector


OTHER INFO.
-----------
- Last upate: R4/8/9(Ka)
- Author: GOTO Ryusuke 
- Contact: 
    - Email: 1155169839@link.cuhk.edu.hk (preferred)
    - WeChat: L13079237

'''
from bs4 import BeautifulSoup
import pandas as pd
import re

def cut_unreadable(content: str):
    '''
    A func to convert the content extracted directly from a form to the format
    that can be read by utf-8

    Parameters
    ----------
    content : str
        The raw content extracted directly from a form. See extract_items method
        in any module to parse a EDGAR form.

    Returns
    -------
    out_str : str
        The string that does not include any symbol, letter, or character that
        cannot be exported to a txt file(in utf-8).

    '''
    # first ecoding into ASCII, and than decode into utf-8, with all odd symbols removed
    content = content.encode('ascii', 'ignore')
    content = content.decode()
    
    # remove other meaningless symbols/words
    content = content.replace('>', '')
    
    tc = re.compile(r'(\n){0,}Table(\n|\s){0,}of(\n|\s){0,}Contents\n{0,}')
    out_str = re.sub(tc, '', content)
    
    pagenum = re.compile(r'(\n{2,}|\s+|\n\s+)([0-9]{1,2})(\n{2,}|\s+|\n\s+)')
    out_str = re.sub(pagenum, ' ', out_str)
    
    enters = re.compile(r'\n{2,}')
    out_str = re.sub(enters, ' ', out_str)

    return out_str


class item_detector:
    def __init__(self, form_type: str):
        self.form_type = form_type
                
        ## regular expressions for the second strategy
        # form 10-K
        rex_part1 = re.compile(r'(Part|PART)\s*I(\s|\n)+')
        rex_p1item1 = re.compile(r'(Item|ITEM)\s*1\.?\s*([Bb]usiness\s*[Rr]?|BUSINESS\s*R?)')
        rex_p1item1A = re.compile(r'(Item|ITEM)\s*A\s*\.?\s*([Rr]isk\s*[Ff]actors?|RISK\s*FACTORS?)')
        rex_p1item1B = re.compile(r'(Item|ITEM)\s*1\s*B\s*\.?\s*([Uu]nresolved|UNRESOLVED)')
        rex_p1item2 = re.compile(r'(Item|ITEM)\s*2\s*\.?\s*([Pp]roperties|PROPERTIES)')
        rex_p1item3 = re.compile(r'(Item|ITEM)\s*3\s*\.?\s*([Ll]egal|LEGAL)')
        rex_p1item4 = re.compile(r'(Item|ITEM)\s*4\s*\.?\s*([Mm]ine\s*[Ss]afety|MINE\s*SAFETY)')

        rex_part2 = re.compile(r'(Part|PART)\s*II(\s|\n)+')
        rex_p2item7 = re.compile(r'(Item|ITEM)\s*7\s*\.?\s*([Mm]anagement|MANAGEMENT)')
        rex_p2item7a = re.compile(r'(Item|ITEM)\s*7\s*A\s*\.?\s*([Qq]uantitative|QUANTITATIVE)')
        rex_p2item8 = re.compile(r'(Item|ITEM)\s*8\s*\.?\s*([Ff]inancial|FINANCIAL)')
        rex_p2item9a = re.compile(r'(Item|ITEM)\s*9\s*A\s*\.?\s*([Cc]ontrol|CONTROL)')

        reg10K_st2 = [rex_part1, rex_p1item1, rex_p1item1A, rex_p1item1B, rex_p1item2, rex_p1item3, rex_p1item4, rex_part2, rex_p2item7, rex_p2item7a, rex_p2item8, rex_p2item9a]
        
        # form 10-Q
        rex_p1item1 = re.compile(r'(Item|ITEM)\s*1\s*\.?\s*([Ff]inancial|FINANCIAL)')
        rex_p1item2 = re.compile(r'(Item|ITEM)\s*2\s*\.?\s*([Mm]anagement|MANAGEMENT)')
        rex_p1item3 = re.compile(r'(Item|ITEM)\s*3\s*\.?\s*([Qq]uantitative|QUANTITATIVE)')
        rex_p1item4 = re.compile(r'(Item|ITEM)\s*4\s*\.?\s*([Cc]ontrols|CONTROLS)')
        
        rex_p2item1 = re.compile(r'(Item|ITEM)\s*1\.?\s*([Ll]egal|LEGAL)\s?')
        rex_p2item1a = re.compile(r'(Item|ITEM)\s*1\s*[Aa]\.?\s*([Rr]isk|RISK)\s?')
        rex_p2i2 = re.compile(r'(Item|ITEM)\s*2\.?\s*(UNREGISTERED|[Uu]nregistered)')
        rex_p2i6 = re.compile(r'(Item|ITEM)\s*6\.?\s*([Ee]xhibits|EXHIBITS)?')
        
        reg10Q_st2 = [rex_p1item1, rex_p1item2, rex_p1item3, rex_p1item4,
            rex_p2item1, rex_p2item1a, rex_p2i2, rex_p2i6]
        
        
        # form 8-K
        rex_202 = re.compile(r'(Item|ITEM)\s*2\s*\.?0\s*2\s*\.?\s*([Rr]esults\s*[Oo]f|RESULTS\s*OF)')
        rex_501 = re.compile(r'(Item|ITEM)\s*5\s*\.?0\s*2\s*\.?\s*([Dd]eparture|DEPARTURE)')
        rex_507 = re.compile(r'(Item|ITEM)\s*5\s*\.?0\s*7\s*\.?\s*([Ss]ubmission|SUBMISSION)')
        rex_701 = re.compile(r'(Item|ITEM)\s*7\s*\.?0\s*1\s*\.?\s*([Rr]egulation|REGULATION)')
        rex_801 = re.compile(r'(Item|ITEM)\s*8\s*\.?0\s*1\s*([Oo]ther\s*[Ee]vents?\s*\.*|OTHER\s*EVENTS?\s*)')
        rex_901 = re.compile(r'(Item|ITEM)\s*9\s*\.?0\s*1\s*([Ff]inancial\s*[Ss]tatements?\s*\.*|FINANCIAL\s*STATEMENTS?\s*\.?)')
        
        reg8K_st2 = [rex_202, rex_501, rex_507, rex_701, rex_801, rex_901]
        
        # a dict of regular expressions for the first strategy
        form_reg_dict_st1 = {'10-K': r'>\s*"*(Item|ITEM)(\s|&#160;|&nbsp;|&#xA0;)*(1\s*A|2|3|4|5|6|7\s*A*|8|9\s*A*)\.?|>\s*(PART|Part)(\s|&#160;|&nbsp;|&#xA0;)*I{1,2}\s*\.*',
                             '10-Q': r'>\s*(Item|ITEM)(\s|&#160;|&nbsp;|&#xA0;)*<.*>\s*(1\s*A|2|3|4|5|6)\.?|>"*(Item|ITEM)(\s|&#160;|&nbsp;|&#xA0;)*(1\s*A|2|3|4|5|6)\.?|>\s*(PART|Part)(\s|&#160;|&nbsp;|&#xA0;)*I{1,2}\s*\.*',
                             '8-K': r'>\s*I[Tt][Ee][Mm](\s|&#160;|&nbsp;|&#xA0;)*((2\s*\.\s*0\s*2)|5\s*\.\s*0\s*1|5\s*\.\s*0\s*7|7\s*\.\s*0\s*1|8\s*\.\s*0\s*1|9\s*\.\s*0\s*1)'}

        
        # a dict of regular expressions for the first strategy
        form_reg_dict_st2 = {'10-K': reg10K_st2,
                             '10-Q': reg10Q_st2,
                             '8-K': reg8K_st2}
        
        # create two attributes that save the rex to be used
        self.reg_st1 = form_reg_dict_st1[form_type]
        self.reg_st2 =form_reg_dict_st2[form_type]
    
    @staticmethod
    def get_ex991(content:str):
        '''
        A static method to extract Exhibit 99.1 from an 8-K form. Work flow:
            i. find the names of all code sections that are included in a pair of <DOCUMENT> tags;         
            ii. check if there are codes under Exhibit 99.1 DOCUMENT;
            iii. if process ii is true, extract the codes under Exhibit 99.1, wash by BS4, and apply cut_unreadable.

        Parameters
        ----------
        content : str
            The XML codes of the form.

        Returns
        -------
        content_EX991: str
            The content under Exhibit 99.1.

        '''
        
        # i
        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        type_pattern = re.compile(r'<TYPE>[^\n]+')
        
        doc_start_is = [x.end() for x in doc_start_pattern.finditer(content)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(content)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(content)]
        docs_table = {}
        
        # ii
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type == 'EX-99.1':
                docs_table[doc_type] = content[doc_start:doc_end]
                break

        if 'EX-99.1' not in docs_table.keys():
            return ''
                
        # iii
        raw_EX991 = BeautifulSoup(docs_table['EX-99.1'],'lxml')
        for table in raw_EX991.find_all('table'):
            if not('\u2022' in table.get_text()):
                table.extract()
        
        content_EX991 = cut_unreadable(raw_EX991.get_text())
        return content_EX991
        
    def first_method(self, content: str):
        '''
        The first strategy. The idea is: match the XML code patterns for the items.
        Work flow:
            i. find the names of all code sections that are included in a pair of <DOCUMENT> 
            ii. check if there are codes under the form to be parsed, e.g 10-Q, DOCUMENT tag;
            iii. if ii is true, find the starts and ends for the items in that DOCUMENT
            iv. create a df to save the names, starts, and ends for the items
            v. remove all meanningless symbols from the column for the names of the items

        Parameters
        ----------
        content : str
            The XML codes of the form.

        Returns
        -------
        raw_content : str
            The XML codes under the DOCUMENT tag of the form to be parsed.
        out_tb : pandas df
            The df comprised of the names, starts, and ends of the items in the form to be parsed.

        '''
        
        # i
        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')
        type_pattern = re.compile(r'<TYPE>[^\n]+')

        doc_start_is = [x.end() for x in doc_start_pattern.finditer(content)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(content)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(content)]

        docs_table = {}
        
        # ii
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type == self.form_type:
                docs_table[doc_type] = content[doc_start:doc_end]
                break
         
        raw_content = docs_table[self.form_type]
        
        # iii
        regex = re.compile(self.reg_st1)
        matches = regex.finditer(raw_content)
        
        # iv
        out_tb = pd.DataFrame([(x.group(), x.start(), x.end()) for x in matches])
        
        if out_tb.size == 0: return '', pd.DataFrame()
        
        out_tb.columns = ['item', 'start', 'end']
        out_tb['item'] = out_tb.item.str.lower()
        
        # v
        replace_list = ['&#160;', '&nbsp;', '&#xa0;' , '\.', '>','<']
        for symbol in replace_list:
            out_tb.replace(symbol, '', regex = True, inplace = True)
        
        out_tb.replace('\s', '', regex = True, inplace = True)
        out_tb = out_tb.sort_values('start', ascending = True)

        return raw_content, out_tb
       
    def second_method(self, content:str):
        '''
        The second strategy. Instead of matching the code pattern, as what we 
        did in the first strategy, now consider extracting the items needed 
        directly from the meanningful content of a form.
        
        Work flow:
            i. find the names of all code sections that are included in a pair of <DOCUMENT> 
            ii. check if there are codes under the form to be parsed, e.g 10-Q, DOCUMENT tag;
            iii. if ii is true, clean the codes under the DOCUMENT tag using BS4;
            iv. in the content cleaned by BS4, match each item directly with its title;
            v. create a df to save the item info; remove meanningless symbols.

        Parameters
        ----------
        content : str
            DESCRIPTION.

        Returns
        -------
        raw_content : str
            The meanningful content in a form
        out_tb : pandas df
            The df comprised of the names, starts, and ends of the items in the form to be parsed.

        '''
        
        # i
        doc_start_pattern = re.compile(r'<DOCUMENT>')
        doc_end_pattern = re.compile(r'</DOCUMENT>')

        type_pattern = re.compile(r'<TYPE>[^\n]+')

        doc_start_is = [x.end() for x in doc_start_pattern.finditer(content)]
        doc_end_is = [x.start() for x in doc_end_pattern.finditer(content)]
        doc_types = [x[len('<TYPE>'):] for x in type_pattern.findall(content)]

        docs_table = {}
        
        # ii
        for doc_type, doc_start, doc_end in zip(doc_types, doc_start_is, doc_end_is):
            if doc_type == self.form_type:
                docs_table[doc_type] = content[doc_start:doc_end]
                break
        
        # iii        
        if '8-K' not in docs_table.keys(): return '', pd.DataFrame()  
        raw_content = BeautifulSoup(docs_table[self.form_type], 'lxml')
        for table in raw_content.find_all('table'):
            if not('\u2022' in table.get_text()):
                table.extract()
        content = cut_unreadable(raw_content.get_text())

        
        item_name = []
        item_start = []
        item_end = []
        
        # iv
        for mt in self.reg_st2:
            matches = mt.finditer(content)
            for x in matches:
                item_name.append(x.group())
                item_start.append(x.start())
                item_end.append(x.end())
        
        # v
        out_tb = []
        out_tb.append(item_name)
        out_tb.append(item_start)
        out_tb.append(item_end)
        out_tb = pd.DataFrame(out_tb).transpose()
        out_tb.columns = ['item', 'start', 'end']
        
        symbols = ['\.','"','-','\n','\bb']
        for symbol in symbols:         
            out_tb.replace(symbol,' ',regex=True,inplace=True)
          
        if self.form_type == '8-K':
            '''
            The titles and item names in an 8-K form differs slightly from 
            that of a 10-Q or 10-K form, so process them separately.
            
            '''
            out_tb['item'] = [item[:10] for item in out_tb['item'].values]      
        else:
            out_tb['item'] = [''.join(item.split(' ')[:2]) for item in out_tb['item'].values]
        
        out_tb.replace(' ','',regex=True,inplace=True)
        out_tb = out_tb.sort_values('start', ascending = True)
        
        if out_tb.size == 0:
            return '', pd.DataFrame()
        else:
            out_tb['item'] = out_tb.item.str.lower()

        return raw_content, out_tb
    

if __name__ == '__main__':
    test_file = 'F:/EDGAR/TestReports/8-K/1000045/1000045_8-K_2022-05-10_0000950170-22-009069.txt'
    with open(test_file, 'r') as f:
        content = f.read()
    
    ms = item_detector(form_type = '8-K')
    test_docs, test_tb = ms.second_method(content)
