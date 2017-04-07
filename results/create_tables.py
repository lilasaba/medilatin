# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import sqlite3
import tabulate
from collections import OrderedDict

class CREATE_TABLE:

    def __init__(self):
        ## Connect to database.
        self.conn = sqlite3.connect('results.sqlite')
        self.cur = self.conn.cursor()
        tabulate.LATEX_ESCAPE_RULES={}

    def query_tu_al_sl_pl(self,training_unit,am_language,speaker_language,paragraph_language):
        self.cur.execute('''SELECT id FROM TrainingUnit WHERE training_unit = ? ''', (training_unit, ))
        training_unit_id = self.cur.fetchone()[0]
        self.cur.execute('''SELECT id FROM AMLanguage WHERE am_language = ? ''', (am_language, ))
        am_language_id = self.cur.fetchone()[0]
        self.cur.execute('''SELECT id FROM SpeakerLanguage WHERE speaker_language = ? ''', (speaker_language, ))
        speaker_language_id = self.cur.fetchone()[0]
        self.cur.execute('''SELECT id FROM ParagraphLanguage WHERE paragraph_language = ? ''', (paragraph_language, ))
        paragraph_language_id = self.cur.fetchone()[0]
        self.cur.execute('''SELECT wer FROM AllResults
                WHERE am_language_id = ?
                AND training_unit_id = ?
                AND speaker_language_id = ?
                AND paragraph_language_id = ? ''', (am_language_id,training_unit_id,speaker_language_id,paragraph_language_id,))
        results = [item for sublist in self.cur.fetchall() for item in sublist]
        return results

    def calculate_average(self,inlist):
        return round(sum(inlist) / len(inlist),1)

    def write_table(self,am_language,training_unit):
        outname = '%s_%s' % (am_language.lower(),training_unit.lower())
        speaker_languages = ['CZ','HU','PL','SK']
        paragraph_languages = ['CZ','HU','PL']
        table = []
        for speaker_language in speaker_languages:
            row = []
            row.append(speaker_language)
            for paragraph_language in paragraph_languages:
                results = self.query_tu_al_sl_pl(training_unit,am_language,speaker_language,paragraph_language)
                wer = self.calculate_average(results)
                row.append(wer)

            row.append(self.calculate_average(row[1:]))
            table.append(row)
        print(table)

        ## Calculate weighted column averages.
        columns = []
        for paragraph_language in paragraph_languages:
            column = []
            for speaker_language in speaker_languages:
                results = self.query_tu_al_sl_pl(training_unit,am_language,speaker_language,paragraph_language)
                column.extend(results)
            columns.append(column)

        paragraph_averages = [n for n in map(self.calculate_average,columns)]
        last_row = ['$\sum$'] + paragraph_averages + [self.calculate_average(paragraph_averages)]
        table.append(last_row)
        table_str = tabulate.tabulate(table,headers=['Speaker','CZ','HU','PL','$\sum$'],tablefmt="latex",floatfmt=".1f")
        table_str = self.post_table(table_str)

        with open('../paper/tables/%s.tex' % outname,'w',encoding='utf-8') as outf:
            outf.write(table_str)

    def post_table(self,table):
        table = table.replace(' $\sum$  ','\hline\n $\sum$ ')
        ## If baseline table.
        table = table.replace('lrrrrr','l|rrrr|r')
        ## If g2p or usg table.
        table = table.replace('lrrrr','l|rrr|r')
        table = table.replace('\hline\n Speaker','\hline\n & \multicolumn{3}{c}{Latin Test Text} & \\\\\n\hline\n Speaker')
        table = table.replace('\hline\n AM Language','\hline\n & \multicolumn{3}{c}{Speaker} & \\\\\n\hline\n AM Language')
        return table

    def query_baseline(self,training_unit):
        results_dict = {}
        am_languages = ['CZ','HU','PL','RO']
        speaker_languages = ['CZ','HU','PL','SK']
        self.cur.execute('''SELECT id FROM TrainingUnit WHERE training_unit = ? ''', (training_unit, ))
        training_unit_id = self.cur.fetchone()[0]
        for am_language in am_languages:
            results_dict[am_language] = []
            self.cur.execute('''SELECT id FROM AMLanguage WHERE am_language = ? ''', (am_language, ))
            am_language_id = self.cur.fetchone()[0]
            for speaker_language in speaker_languages:
                self.cur.execute('''SELECT id FROM SpeakerLanguage WHERE speaker_language = ? ''', (speaker_language, ))
                speaker_language_id = self.cur.fetchone()[0]
                self.cur.execute('''SELECT wer FROM AllResults
                        WHERE am_language_id = ?
                        AND training_unit_id = ?
                        AND speaker_language_id = ? ''', (am_language_id,training_unit_id,speaker_language_id, ))

                results = [item for sublist in self.cur.fetchall() for item in sublist]
                average_wer = self.calculate_average(results)
                results_dict[am_language].append(average_wer)

        results_list = [[k,results_dict[k]] for k in results_dict.keys()]
        print(results_list)
        return results_dict

    def write_baseline_table(self,baseline_dict):
        outname = 'cz_hu_pl_ro_grapheme'
        table = []
        for am_language in baseline_dict.keys():
            wers = baseline_dict[am_language]
            row = []
            row.append(am_language)
            row.extend(wers)
            last_column = self.calculate_average(wers)
            row.append(last_column)
            table.append(row)

        table = sorted(table)

        table_str = tabulate.tabulate(table,headers=['AM Language','CZ','HU','PL','SK','$\sum$'],tablefmt="latex",floatfmt=".1f")
        table_str = self.post_table(table_str)

        with open('../paper/tables/%s.tex' % outname,'w',encoding='utf-8') as outf:
            outf.write(table_str)

if __name__ == '__main__':
    table = CREATE_TABLE()
    ## Extract HU PHONEME results.
    training_unit = 'PHONEME'
    am_language = 'HU'
    table.write_table(am_language,training_unit)
    ## Extract CZ_HU_PL_USG results.
    training_unit = 'USG'
    am_language = 'CZ_HU_PL'
    table.write_table(am_language,training_unit)
    ## Extract HU_PL_RO USG results.
    training_unit = 'USG'
    am_language = 'HU_PL_RO'
    table.write_table(am_language,training_unit)
    ## Extract CZ_PL_RO USG results.
    training_unit = 'USG'
    am_language = 'CZ_PL_RO'
    table.write_table(am_language,training_unit)
    ## Extract CZ_HU_RO USG results.
    training_unit = 'USG'
    am_language = 'CZ_HU_RO'
    table.write_table(am_language,training_unit)
    ## Extract CZ_HU_PL_RO USG results.
    training_unit = 'USG'
    am_language = 'CZ_HU_PL_RO'
    table.write_table(am_language,training_unit)
    ## Extract CZ_HUSHORT_PL_RO USG results.
    training_unit = 'USG'
    am_language = 'CZ_HUSHORT_PL_RO'
    table.write_table(am_language,training_unit)
    ## Extract CZ PHONEME results.
    training_unit = 'PHONEME'
    am_language = 'CZ'
    table.write_table(am_language,training_unit)
    ## Extract PL GRAPHEME results.
    training_unit = 'GRAPHEME'
    am_language = 'PL'
    table.write_table(am_language,training_unit)
    ## Extract CZ GRAPHEME results.
    training_unit = 'GRAPHEME'
    am_language = 'CZ'
    table.write_table(am_language,training_unit)
    ## Extract HU GRAPHEME results.
    training_unit = 'GRAPHEME'
    am_language = 'HU'
    table.write_table(am_language,training_unit)
    ## Extract Ro GRAPHEME results.
    training_unit = 'GRAPHEME'
    am_language = 'RO'
    table.write_table(am_language,training_unit)
    ## Create baseline table.
    training_unit = 'GRAPHEME'
    baseline_dict = table.query_baseline(training_unit)
    table.write_baseline_table(baseline_dict)

    table.cur.close()
    table.conn.close()
