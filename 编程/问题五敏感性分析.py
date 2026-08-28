import math, random
from importlib.machinery import SourceFileLoader

# 复用问题四脚本中的数据和代理模型定义（脚本会打印其结果）
m=SourceFileLoader('q4','编程/问题四鲁棒优化.py').load_module()
base=(.2,3.5,6)
names=['针肋宽度比','歧管深高比','针肋排数']
print('基准方案',base,'预测', [round(v,6) for v in m.pred(base)])

# 单因素局部敏感度：以一个参数的相邻水平替代基准值
for k, levels in enumerate(m.levels):
 vals=[]
 for v in levels:
  x=list(base); x[k]=v; vals.append((v,m.pred(x)))
 print('\n'+names[k])
 for v,y in vals: print(v,[round(q,6) for q in y])

# 连续小扰动蒙特卡洛：x1/x2 ±5%，x3 ±1排；输出均值、标准差、区间和阈值超标率
rng=random.Random(2026); samples=[]
for _ in range(10000):
 x=(base[0]*(1+rng.uniform(-.05,.05)),base[1]*(1+rng.uniform(-.05,.05)),base[2]+rng.uniform(-1,1))
 samples.append(m.pred(x))
print('\n蒙特卡洛 10000 次（相对扰动：x1/x2±5%，x3±1）')
for j,n in enumerate(['热阻','压降','温度非均匀性']):
 a=[s[j] for s in samples]; mu=sum(a)/len(a); sd=(sum((v-mu)**2 for v in a)/len(a))**.5
 print(n,'mean',round(mu,6),'sd',round(sd,6),'CV',round(sd/mu,4),'P5-P95',round(sorted(a)[500],6),round(sorted(a)[9499],6))

# 局部弹性：输出相对变化/相对输入变化
basey=m.pred(base)
for k,delta in enumerate([.01,.01,.1]):
 xp=list(base); xm=list(base); xp[k]+=delta; xm[k]-=delta
 yp=m.pred(xp); ym=m.pred(xm); print('弹性',names[k],[round(((yp[j]-ym[j])/(2*basey[j]))/ (delta/base[k]),4) for j in range(3)])
