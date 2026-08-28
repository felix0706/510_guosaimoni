import glob, zipfile, xml.etree.ElementTree as ET, math, random

NS={'m':'http://schemas.openxmlformats.org/spreadsheetml/2006/main'}
path=[p for p in glob.glob('数据/*.xlsx') if '~$' not in p][0]
with zipfile.ZipFile(path) as z:
    root=ET.fromstring(z.read('xl/sharedStrings.xml'))
    ss=[''.join(t.text or '' for t in si.findall('.//m:t',NS)) for si in root.findall('m:si',NS)]
    sh=ET.fromstring(z.read('xl/worksheets/sheet1.xml'))
    rows=[]
    for row in sh.findall('.//m:row',NS):
        vals=[]
        for c in row.findall('m:c',NS):
            v=c.find('m:v',NS)
            vals.append(ss[int(v.text)] if c.attrib.get('t')=='s' else float(v.text) if v is not None else None)
        rows.append(vals)
data=[r for r in rows[2:] if r and isinstance(r[0],float)]

def feat(r):
    x1,x2,x3=r[1:4]
    return [1,x1,x2,x3,x1*x1,x2*x2,x3*x3,x1*x2,x1*x3,x2*x3]

def solve(A,b):
    n=len(b); M=[list(map(float,A[i]))+[float(b[i])] for i in range(n)]
    for k in range(n):
        p=max(range(k,n),key=lambda i:abs(M[i][k]))
        M[k],M[p]=M[p],M[k]
        q=M[k][k]
        if abs(q)<1e-12: raise ValueError('singular')
        for j in range(k,n+1): M[k][j]/=q
        for i in range(n):
            if i==k: continue
            q=M[i][k]
            for j in range(k,n+1): M[i][j]-=q*M[k][j]
    return [M[i][n] for i in range(n)]

def fit(X,y):
    p=len(X[0]); A=[[sum(row[i]*row[j] for row in X) for j in range(p)] for i in range(p)]
    b=[sum(X[k][i]*y[k] for k in range(len(X))) for i in range(p)]
    return solve(A,b)
def pred(beta,x): return sum(a*b for a,b in zip(beta,x))
def metrics(yhat,y):
    n=len(y); my=sum(y)/n; ss=sum((v-my)**2 for v in y)
    return {'R2':1-sum((a-b)**2 for a,b in zip(yhat,y))/ss,
            'RMSE':math.sqrt(sum((a-b)**2 for a,b in zip(yhat,y))/n),
            'MAE':sum(abs(a-b) for a,b in zip(yhat,y))/n}

X=[feat(r) for r in data]
names=['热阻','压降','温度非均匀性']
for j,name in enumerate(names,4):
    y=[r[j] for r in data]; beta=fit(X,y); print('\n'+name+' 模型系数:'); print([round(v,10) for v in beta]); print('训练集',metrics([pred(beta,x) for x in X],y))
    idx=list(range(len(y))); random.Random(2026).shuffle(idx); folds=[idx[k::5] for k in range(5)]; yh=[]; yt=[]
    for test in folds:
        train=[i for i in idx if i not in test]; bt=fit([X[i] for i in train],[y[i] for i in train])
        yh += [pred(bt,X[i]) for i in test]; yt += [y[i] for i in test]
    print('5折交叉验证',metrics(yh,yt))
