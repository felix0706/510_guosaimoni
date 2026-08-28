import glob, zipfile, xml.etree.ElementTree as ET
from collections import defaultdict

NS = {'m': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
path = [p for p in glob.glob('数据/*.xlsx') if '~$' not in p][0]
with zipfile.ZipFile(path) as z:
    root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    ss = [''.join(t.text or '' for t in si.findall('.//m:t', NS)) for si in root.findall('m:si', NS)]
    sh = ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows = []
    for row in sh.findall('.//m:row', NS):
        vals = []
        for c in row.findall('m:c', NS):
            v = c.find('m:v', NS)
            vals.append(ss[int(v.text)] if c.attrib.get('t') == 's' else float(v.text) if v is not None else None)
        rows.append(vals)

data = rows[2:]
data = [r for r in data if r and isinstance(r[0], float)]
names = ['热阻', '压降', '温度非均匀性']
print('样本数:', len(data))
for j, name in enumerate(names, 4):
    vals = [r[j] for r in data]
    print(name, 'min=', min(vals), 'max=', max(vals), 'mean=', sum(vals)/len(vals))
for col, label in [(1, '针肋宽度比'), (2, '歧管深高比'), (3, '针肋排数')]:
    print('\n', label)
    groups = defaultdict(list)
    for r in data: groups[r[col]].append(r)
    for x, rs in sorted(groups.items()):
        print(x, 'n=',len(rs), 'means=', [round(sum(r[j] for r in rs)/len(rs),6) for j in range(4,7)])
best = min(data, key=lambda r: sum(r[j] for j in range(4,7)))
print('\n简单和最优行:', best)

# Pearson correlations as a compact monotonicity check
def corr(xs, ys):
    mx, my = sum(xs)/len(xs), sum(ys)/len(ys)
    a = sum((x-mx)*(y-my) for x,y in zip(xs,ys))
    b = (sum((x-mx)**2 for x in xs)*sum((y-my)**2 for y in ys))**0.5
    return a/b
for col, label in [(1,'宽度比'),(2,'深高比'),(3,'排数')]:
    print('corr',label,[round(corr([r[col] for r in data],[r[j] for r in data]),4) for j in range(4,7)])
