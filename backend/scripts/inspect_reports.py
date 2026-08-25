import sqlite3, json
from collections import Counter

con = sqlite3.connect('db.sqlite3')
cur = con.cursor()
try:
    cur.execute('SELECT id, report_data FROM analytics_persistedreport')
except Exception as e:
    print('Query error:', e)
    raise
rows = cur.fetchall()
for id_, data in rows:
    try:
        rd = json.loads(data)
    except Exception:
        rd = data
    comp = rd.get('comprehensive_analysis') if isinstance(rd, dict) else None
    if not comp:
        continue
    print('\nReport', id_)
    for i, s in enumerate(comp):
        k = (s.get('section_key') or s.get('key') or '')
        t = s.get('title')
        print(f'  idx={i} key={k!r} title={t!r}')
    keys = [(s.get('section_key') or s.get('key') or s.get('title') or '') for s in comp]
    c = Counter(keys)
    dups = [k for k, v in c.items() if v > 1]
    if dups:
        print('  DUPLICATE KEYS:', dups)
con.close()
