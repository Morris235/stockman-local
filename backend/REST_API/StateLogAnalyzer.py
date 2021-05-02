# 취득하지 못한 항목과, 보고서에 기재되지 않은 기업코드를 분석하고(일목요연하게 보여주고)
# 이것들을 다른 방식으로 취득할수 있는 코드를 여기에서 연구해야겠다.
import csv

import pandas as pd

pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)
# 0501
not_included_code_dir = "log/copy/20210501/stateReader/not_included_code/statements/code_list.txt"
filed_log_income = "log/copy/20210501/stateReader/income/filed.txt"

# 0502
no_code_fin_dir = 'log/copy/20210502/no_code_fin.txt'
no_code_income_dir = 'log/copy/20210502/no_code_income.txt'

filed_income = 'log/copy/20210502/income_filed.txt'
filed_state = 'log/copy/20210502/statements_filed.txt'


# 0430 : 759 미취득
# 0501 : 383 미취득
# 0502 : 278 미취득

# 보고서에 존재하지 않는 코드 카운트
# with open(no_code_fin_dir, mode='r') as f:
#    lines = f.readlines()
#    code = list(map(lambda s: s.strip(), lines))
#    code = pd.DataFrame(code)
#    print(code)

# 취득실패 손익항목
# 0을 null 값으로 인식하는 모양
income_filed_log = pd.read_csv(filed_income, engine='python', header=None, names=['code', 'company_nm', 'target_nm', 'type', 'curr', 'last', 'before'], sep=',', encoding='euc-kr')
income_filed_log.drop(columns=['curr', 'last', 'before'], inplace=True, axis=1)
# log.duplicated(['target_nm'], keep='first')
# log.drop_duplicates(['company_nm'], keep='first', inplace=True)
# log.drop_duplicates(['code'], keep='first', inplace=True)
print(len(income_filed_log))


state_filed_log = pd.read_csv(filed_state, engine='python', header=None, names=['code', 'company_nm', 'target_nm', 'curr', 'last', 'before'], sep=',', encoding='euc-kr')
state_filed_log.drop(columns=['curr', 'last', 'before'], inplace=True, axis=1)
# log.duplicated(['target_nm'], keep='first')
# log.drop_duplicates(['company_nm'], keep='first', inplace=True)
# log.drop_duplicates(['code'], keep='first', inplace=True)
print(len(state_filed_log))

