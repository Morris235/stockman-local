# 취득하지 못한 항목과, 보고서에 기재되지 않은 기업코드를 분석하고(일목요연하게 보여주고)
# 이것들을 다른 방식으로 취득할수 있는 코드를 여기에서 연구해야겠다.
import csv

import pandas as pd

pd.set_option('display.width', 100000)
pd.set_option('display.max_rows', 100000)
pd.set_option('display.max_columns', 100000)

not_included_code_dir = "log/copy/20210430/log/stateReader/not_included_code/statements/code_list.txt"
filed_log_income = "log/copy/20210430/log/stateReader/income/filed.txt"

# 759개나 없었다 제길

# with open(not_included_code_dir, mode='r') as f:
#    lines = f.readlines()
#    code = list(map(lambda s: s.strip(), lines))
#    df = pd.DataFrame(code)
#    print(df)

# 0을 null 값으로 인식하는 모양
log = pd.read_csv(filed_log_income, engine='python', header=None, names=['code', 'company_nm', 'target_nm', 'value'], sep=',', encoding='euc-kr')
# log.duplicated(['target_nm'], keep='first')
# log.drop_duplicates(['target_nm'], keep='first', inplace=True)
log.drop_duplicates(['code'], keep='first', inplace=True)
print(log.code)


# df = pd.read_csv(filed_log_income, sep=',', engine='python', encoding='euc-kr')
# print(df)

# filed_dict = pd.read_csv(filed_log_income, sep='\n', engine='python', encoding='euc-kr')
# filed_dict.columns = ['dict']
# dict = filed_dict.to_dict()
# dict2 = dict.get('dict')
# dict3 = dict2.get(0)
# print(dict3.get('code'))


