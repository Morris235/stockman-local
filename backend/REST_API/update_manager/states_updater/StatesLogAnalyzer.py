# 취득하지 못한 항목과, 보고서에 기재되지 않은 기업코드를 분석하고(일목요연하게 보여주고)
# 이것들을 다른 방식으로 취득할수 있는 코드를 여기에서 연구해야겠다.
import csv

import pandas as pd

pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)


class LogReader:
    def __init__(self):
        # 0430 : 759 미취득
        # 0501 : 383 미취득
        # 0502 : 278 미취득

        # 0501
        self.not_included_code_dir = "../../log/stateReaderFiles_copy/20210501/stateReader/not_included_code/statements/code_list.txt"
        self.filed_log_income = "log/stateReaderFiles_copy/20210501/year/income/filed.txt"

        # 0502
        self.no_code_fin_dir = '../../log/stateReaderFiles_copy/20210502/no_code_fin.txt'
        self.no_code_income_dir = '../../log/stateReaderFiles_copy/20210502/no_code_income.txt'
        self.filed_income = 'log/stateReaderFiles_copy/20210502/income_filed.txt'
        self.filed_state = 'log/stateReaderFiles_copy/20210502/statements_filed.txt'


    # 보고서에 존재하지 않는 코드 카운트
    def state_no_code(self):
        with open(self.no_code_fin_dir, mode='r') as f:
            lines = f.readlines()
            code = list(map(lambda s: s.strip(), lines))
            code = pd.DataFrame(code)
            print('재무 상태 보고서에 존재하지않는(취득못한) 기업코드 개수 : ' + str(len(code)))

    # 보고서에 존재하지 않는 코드 카운트
    def income_no_code(self):
        with open(self.no_code_income_dir, mode='r') as f:
            lines = f.readlines()
            code = list(map(lambda s: s.strip(), lines))
            code = pd.DataFrame(code)
            print('손익 보고서에 존재하지않는(취득못한) 기업코드 개수 : ' + str(len(code)))

    # 취득실패 손익항목
    # 0을 null 값으로 인식하는 모양
    def read_filed_income(self):
        income_filed_log = pd.read_csv(self.filed_income, engine='python', header=None,
                                       names=['code', 'company_nm', 'target_nm', 'type', 'curr', 'last', 'before'],
                                       sep=',',
                                       encoding='euc-kr')
        income_filed_log.drop(columns=['curr', 'last', 'before'], inplace=True, axis=1)
        # log.duplicated(['target_nm'], keep='first')
        # log.drop_duplicates(['company_nm'], keep='first', inplace=True)
        # log.drop_duplicates(['code'], keep='first', inplace=True)
        print('취득하지 못한 손익항목 개수 : ' + str(len(income_filed_log)))

    # 취득실패 재무상태 항목
    def read_filed_state(self):
        state_filed_log = pd.read_csv(self.filed_state, engine='python', header=None,
                                      names=['code', 'company_nm', 'target_nm', 'curr', 'last', 'before'], sep=',',
                                      encoding='euc-kr')
        state_filed_log.drop(columns=['curr', 'last', 'before'], inplace=True, axis=1)
        # log.duplicated(['target_nm'], keep='first')
        # log.drop_duplicates(['company_nm'], keep='first', inplace=True)
        # log.drop_duplicates(['code'], keep='first', inplace=True)
        print('취득하지 못한 재무상태 항목 개수 : ' + str(len(state_filed_log)))


if __name__ == '__main__':
    execution = LogReader()

    execution.state_no_code()
    execution.income_no_code()
    execution.read_filed_income()
    execution.read_filed_state()
