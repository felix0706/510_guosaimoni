import glob, zipfile, xml.etree.ElementTree as ET
from itertools import product
NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
p=[p for p in glob.glob('数据/*.xlsx') if '~$' not in p][0]
with zipfile.ZipFile(p) as z:
 root=ET.fromstring(z.read('xl/sharedStrings.xml')); ss=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in root.findall('m:si',NS)]
 sh=ET.fromstring(z.read('xl/worksheets/sheet1.xml')); rows=[]
 for row in sh.findall('.//m:row',NS):
  vals=[]
  for c in row.findall('m:c',NS):
   v=c.find('m:v',NS); vals.append(ss[int(v.text)] if c.attrib.get('t')=='s' else float(v.text) if v is not None else None)
  rows.append(vals)
data=[r for r in rows[2:] if r and isinstance(r[0],float)]
def phi(x):
 a,b,c=x; return [1,a,b,c,a*a,b*b,c*c,a*b,a*c,b*c]
def solve(A,b):
 n=len(b); M=[A[i][:]+[b[i]] for i in range(n)]
 for k in range(n):
  q=max(range(k,n),key=lambda i:abs(M[i][k])); M[k],M[q]=M[q],M[k]; d=M[k][k]
  for j in range(k,n+1): M[k][j]/=d
  for i in range(n):
   if i!=k:
    d=M[i][k]
    for j in range(k,n+1): M[i][j]-=d*M[k][j]
 return [M[i][n] for i in range(n)]
X=[phi(r[1:4]) for r in data]; betas=[]
for col in range(4,7):
 A=[[sum(x[i]*x[j] for x in X) for j in range(10)] for i in range(10)]
 b=[sum(X[k][i]*data[k][col] for k in range(len(data))) for i in range(10)]
 betas.append(solve(A,b))
def pred(x): return [sum(a*b for a,b in zip(bt,phi(x))) for bt in betas]
lo=[min(r[j] for r in data) for j in range(4,7)]; hi=[max(r[j] for r in data) for j in range(4,7)]
levels=[[0,.1,.15,.2,.3],[3,3.5,4,4.5],[2,4,6,8,10]]; out=[]
for x in product(*levels):
 y=pred(x); n=[(y[i]-lo[i])/(hi[i]-lo[i]) for i in range(3)]; out.append((sum(n)/3,x,y,n))
out.sort(); print('综合最优',out[0]); print('前10')
for r in out[:10]: print(round(r[0],6),r[1],[round(v,6) for v in r[2]])
pareto=[a for a in out if not any(all(b[2][i]<=a[2][i] for i in range(3)) and any(b[2][i]<a[2][i] for i in range(3)) for b in out)]
print('Pareto数量',len(pareto),'Pareto中评分最优',min(pareto,key=lambda r:r[0]))
