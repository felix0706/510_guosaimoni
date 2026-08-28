import glob,zipfile,xml.etree.ElementTree as ET
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
levels=[[0,.1,.15,.2,.3],[3,3.5,4,4.5],[2,4,6,8,10]]
design=[]
for x in product(*levels):
 y=pred(x); z=tuple((y[i]-lo[i])/(hi[i]-lo[i]) for i in range(3)); design.append((x,y,z))
scenarios={'均衡':(1/3,1/3,1/3),'低热阻芯片':(.6,.2,.2),'低压降泵功耗':(.2,.6,.2),'高均温可靠性':(.2,.2,.6),'热阻优先':(.7,.15,.15),'压降优先':(.15,.7,.15),'均温优先':(.15,.15,.7)}
print('场景最优方案')
for name,w in scenarios.items():
 best=min(design,key=lambda d:sum(w[i]*d[2][i] for i in range(3)))
 print(name,w,best[0],[round(v,6) for v in best[1]],round(sum(w[i]*best[2][i] for i in range(3)),6))
# robust minimax over a dense weight grid (weights >= .1, sum=1)
weights=[]
for a in range(1,9):
 for b in range(1,10-a):
  c=10-a-b; weights.append((a/10,b/10,c/10))
rob=[]
for d in design:
 vals=[sum(w[i]*d[2][i] for i in range(3)) for w in weights]
 rob.append((max(vals),sum(vals)/len(vals),d,vals))
rb=min(rob,key=lambda q:(q[0],q[1]))
print('鲁棒minimax',rb[2][0],[round(v,6) for v in rb[2][1]],'max=',round(rb[0],6),'mean=',round(rb[1],6))
print('鲁棒平均排名',1+sum(sum(w[i]*d[2][i] for i in range(3))<sum(w[i]*rb[2][2][i] for i in range(3)) for w in weights for d in design)/len(weights))
