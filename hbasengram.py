#!/usr/bin/env/python
'''
This module provides the HBaseNgram class.

HBaseNgram supports linggle query syntax for retrieving ngrams and count from HBase.

To create HBase table for this HBaseNgram:
$ hbase shell
hbase(main):001:0> create 'web1t-ngram-cnt', {NAME => '1', VERSIONS => '1'}, {NAME => '2', VERSIONS => '1'}, {NAME => '3', VERSIONS => '1'}, {NAME => '4', VERSIONS => '1'}, {NAME => '5', VERSIONS => '1'}
'''


from pyparsing import Word, alphas, Literal, operatorPrecedence, opAssoc
from pyparsing import  Optional


from copy import deepcopy
from functools import partial
import logging
reload(logging)
import happybase
from itertools import  islice
from heapq import heapify, heapreplace, heappop
from functools import  total_ordering
import pdb


LOGGER = logging.getLogger('report')
LOGGER.setLevel(logging.INFO)
FORMATTER = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
CH = logging.StreamHandler()
CH.setFormatter(FORMATTER)
LOGGER.addHandler(CH)





class HBaseCol():
    '''
    Class for construct hbase columns
    '''
    def __init__(self, poss=None, next_pos=0):
        if poss == None:
            poss = []

        self.poss = poss
        self.next_pos = next_pos

    def __deepcopy__(self, memo):
        return HBaseCol(deepcopy(self.poss, memo), self.next_pos)
        # elif name == 'next_pos': self[2] = value

    def __str__(self):
        return str(self.next_pos) + '-' + ''.join(map(str, self.poss))


class HBaseQuery():
    '''Class for construct a hbase query'''
    def __init__(self, text = None, cols=None):
        if text == None:
            text = []
        if cols == None:
            cols = [HBaseCol()]

        self.text = text
        self.cols = cols

    def __iter__(self):
        yield self.text
        yield self.cols

    def __deepcopy__(self, memo):
        return HBaseQuery(deepcopy(self.text, memo), deepcopy(self.cols, memo))
        # elif name == 'next_pos': self[2] = value

    def rowkey(self):
        return ' '.join(self.text) + '|'

    def columns(self):
        text_length = str(len(self.text))
        return map(lambda p: text_length + ':' + str(p), self.cols)

    def __str__(self):
        return '<\'' + self.rowkey() + '\', ' +  str(self.columns()) + '>'

    def __repr__(self):
        return self.__str__()



class Alternatives():
    '''Class for parsing linggle syntax query'''
    def __init__(self, toks):
        self.alternatives = toks[0][0::2]

    def __str__(self):
        return '(' + '|'.join(map(str, self.alternatives)) + ')'

    def __iter__(self):
        for alt in self.alternatives:
            yield alt


class Query():
    '''Class for parsing linggle syntax query'''

    def __init__(self, toks):
        toks = toks[0][0::2]

        self._querys = [HBaseQuery([], [HBaseCol([], 0)])]

        LOGGER.debug('init Query: {} '.format(self._querys))
        self._maybe = False
        for gram in toks:
            LOGGER.debug('gram: {} {}'.format(str(gram), type(gram)))
            if isinstance(gram, Alternatives):
                LOGGER.debug('-> alternatives')
                if self._maybe:
                    orig_querys = deepcopy(self._querys)
                self._insert_alternatives(gram)
                if self._maybe:
                    self._querys.extend(orig_querys)
            elif gram == '_':
                LOGGER.debug('-> wildcard')
                self._insert_wildcard()
            elif gram == '*':
                LOGGER.debug('-> any wildcard')
                self._insert_any_wildcard()
            elif gram == '?':
                LOGGER.debug('-> maybe')
                self._maybe = True
                continue
            elif gram == 'STOPHERE':
                return

            else:
                LOGGER.debug('-> word')
                if self._maybe:
                    orig_querys = deepcopy(self._querys)
                self._insert_word(gram)
                if self._maybe:
                    self._querys.extend(orig_querys)
            self._maybe = False
            LOGGER.debug('result: {}'.format(str(self)))

    def _cols_step(self, cols, append=False):
        # LOGGER.debug('poss step start: {}'.format(cols))
        to_del = []
        for i, poss in enumerate(cols):
            if poss.next_pos + 1 > 5:
                to_del.append(i)
                continue
            if append:
                poss.poss.append(poss.next_pos)
            poss.next_pos += 1
            # LOGGER.debug('poss: {}'.format(poss))
        for i in reversed(to_del):
            del cols[i]

    def _insert_wildcard(self):
        for text, cols in self._querys:
            if self._maybe:
                orig_cols = deepcopy(cols)
            self._cols_step(cols)
            if self._maybe:
                cols.extend(orig_cols)

    def _insert_any_wildcard(self):
        for text, cols in self._querys:
            new_cols = deepcopy(cols)
            for offset in range(5 - len(text)):
                self._cols_step(new_cols)
                cols.extend(new_cols)
                new_cols = deepcopy(new_cols)

    def _insert_alternatives(self, alts):
        new_querys = []

        for text, cols in self._querys:
            new_cols = deepcopy(cols)
            self._cols_step(new_cols, append=True)

            for alt in alts:
                new_querys.append(
                    HBaseQuery(text + [alt], cols=deepcopy(new_cols)))
            del new_cols
        del self._querys
        self._querys = new_querys

    def _insert_word(self, word):
        for text, cols in self._querys:
            self._cols_step(cols, append=True)
            text.append(word)

    def __str__(self):
        return self.__repr__()
    def __iter__(self):
        for q in self._querys:
            yield q

    def __getitem__(self, key):
        return self._querys[key]

    def __repr__(self):
        return 'Query( ' + ', '.join(map(str, self._querys)) + ')'



def queryparser():
    '''generate a linggle query syntax parser
    linggle query syntax -> hbase query'''
    word = Word(alphas + "'" + '.' + ',' + '.' + '<>')
    wildcard, any_wildcard, maybe = Literal('_'), Literal('*'), Literal('?')
    atom = (word | wildcard | any_wildcard | maybe)

    query = operatorPrecedence(
        atom,
        [
            ('|', 2, opAssoc.LEFT, Alternatives),
            (Optional('&', default='&'), 2, opAssoc.LEFT, Query)
        ])
    return query




@total_ordering
class Row():
    """
    Class for packing a ngram row

    `Row.ngram`: ngram as list
    `Row.ngram_len`: length of ngram
    `Row.poss`: certain word positions
    `Row.count`: ngram count
    """
    def __init__(self, ngram, ngram_len, positions, count ):
        self.ngram = ngram
        self.ngram_len = ngram_len
        self.positions = positions
        self.count = count
    def __str__(self):
        return 'Row(ngram = {}, ngram_len = {}\
, positions = {}, count = {})'.format(
            str(self.ngram), self.ngram_len, self.positions, self.count)
    def __repr__(self):
        return self.__str__()
    def __iter__ (self):
        yield self.ngram
        yield self.ngram_len
        yield self.positions
        yield self.count

    def __lt__(self, other):
        return self.count > other.count
    def __eq__(self, other):
        return self.count == other.count

    @staticmethod
    def make_from_hbase(row ):
        col, ngram = row[1].items()[0]
        ngram, count = ngram.split('\t')
        ngram = ngram.split(' ')
        count = int(count)

        _, col = col.split(':')
        ngram_len, poss = col.split('-')
        poss = map(int, list(poss))
        return Row(ngram, ngram_len, poss, count)




class HBaseNgram:
    def __init__(self, host, table):
        """
        HBaseNgram(host, table)

        return a HBaseNgram object with query() method.

        bnchb = HBaseNgram('hadoop.nlpweb.org', 'bnc-all-cnt-ngram')
        result = bnchb.query('play * ?* role', limit = 10)
        for row in result:
             print row
        """
        conn = happybase.Connection(host)
        conn.open()
        self._table = conn.table(table)

    def _merge(self, iterables):
        LOGGER.debug('iterables: {}'.format(iterables))
        h = []
        h.append
        for itnum, it in enumerate(map(iter, iterables)):
            try:
                next = it.next
                # next()
                h.append([Row.make_from_hbase(next()), itnum, next])
            except StopIteration:
                pass
        # LOGGER.debug('heap: {}'.format (h))
        heapify(h)
        # LOGGER.debug('heap: {}'.format (h))

        while True:
            try:
                while True:
                    # raises IndexError when h is empty
                    v, itnum, next = s = h[0]
                    # yield self._to_row_for_use(v)
                    yield v
                    # raises StopIteration when exhausted
                    s[0] = Row.make_from_hbase(next())
                    # restore heap condition
                    heapreplace(h, s)
                    LOGGER.debug('heap: {}'.format (h))
            except StopIteration:
                 # remove empty iterator
                heappop(h)
            except IndexError:
                return

    def _scan(self, query, limit):
        return self._table.scan(
            row_prefix=query.rowkey(),
            columns=query.columns(),
            limit=limit )


    def _to_row_for_heap(self,res):
        # LOGGER.debug('res: {}'.format(res))
        row = res[0]
        col, ngram = res[1].items()[0]
        ngram, count = ngram.split('\t')
        ngram = ngram.split(' ')
        count = int(count)
        reversed_count = (1<<(8*5)) - count

        _, col = col.split(':')
        ngram_len, poss = col.split('-')
        poss = map(int, list(poss))
        return reversed_count, count, ngram_len, ngram , poss

    def _to_row_for_use(self,res):
        reversed_count, count, ngram_len, ngram , poss = res
        return Row(ngram, ngram_len, poss, count)


    def query(self, query, limit=None):
        '''
        query(query, limit=None) -> list of Row()

        e.g.
         bnchb = HBaseNgram('hadoop.nlpweb.org', 'bnc-all-cnt-ngram')
         result = bnchb.query('play * ?* role', limit = 10)
         for row in result:
              print row
        '''

        parser = queryparser()
        query += ' STOPHERE'
        querys = parser.parseString(query)[0]
        LOGGER.debug('querys: {}'.format(querys))
        limited_scan = partial(self._scan, limit = limit)
        results = map (limited_scan, querys)
        LOGGER.debug('results: {}'.format(results))
        return islice(self._merge(results), limit)



if __name__ == '__main__':

    web1t = HBaseNgram('hadoop.nlpweb.org', 'bnc-all-cnt-ngram')
    res = web1t.query('play * ', limit = 2000)
    for row in res:
        print row
    # pdb.set_trace()
    # res = web1t.query('play * ?*', limit = 20)
    # print 'second', list(res)
