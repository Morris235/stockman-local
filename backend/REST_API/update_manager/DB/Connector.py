import pymysql
# DB 보안을 위해 gitignore 에 필피 등록
conn = pymysql.connect(host='localhost', port=3306, db='STOCKS', user='root', passwd='Lsm11875**', charset='utf8', autocommit=True)
