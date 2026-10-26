import re,sys,json
s=open(__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'..','decoded','inner.luau'),'rb').read().decode('latin1')
site=s.index('while true do local k,R=I[b];if k>=85 then')
start=site+len('while true do local k,R=I[b];')
tok_re=re.compile(r'"(?:\\.|[^"\\])*"|\'(?:\\.|[^\'\\])*\'|[A-Za-z_][A-Za-z_0-9]*|\d+\.?\d*(?:[eE][-+]?\d+)?|\.\.\.|\.\.|==|~=|<=|>=|[^\sA-Za-z_0-9]')
toks=[]
for m in tok_re.finditer(s,start):
    toks.append((m.group(0),m.start(),m.end()))
    if len(toks)>400000: break
OPEN={'if','for','while','function'}
EXPR_PREV={'=',',','(','{','[','..','+','-','*','/','%','^','==','~=','<','>','<=','>=','return','and','or','not','in','#'}
def match_else_end(i):
    """i: index just after 'then'. Return (else_idx or None, end_idx) at depth 0."""
    stack=[]; else_i=None; j=i
    while j<len(toks):
        w=toks[j][0]
        if w=='if':
            stack.append('E' if toks[j-1][0] in EXPR_PREV else 'S')
        elif w in ('for','while','function'): stack.append('S')
        elif w=='repeat': stack.append('R')
        elif w=='until':
            while stack and stack.pop()!='R': pass
        elif w=='end':
            if not stack: return else_i,j
            stack.pop()
        elif w=='else':
            if stack:
                if stack[-1]=='E': stack.pop()
            elif else_i is None: else_i=j
        elif w=='elseif':
            if not stack and else_i is None: else_i=j
        j+=1
    raise Exception('unbalanced')
def is_cond(i):
    # if k <op> NUM then
    return toks[i][0] in('if','elseif') and toks[i+1][0]=='k' and toks[i+2][0] in('>=','<','==','~=','<=','>') and toks[i+3][0].isdigit() and toks[i+4][0]=='then'
def ev(op,cmp,n):
    n=int(n)
    return {'>=':op>=n,'<':op<n,'==':op==n,'~=':op!=n,'<=':op<=n,'>':op>n}[cmp]
def leaf(op,i):
    """i points at 'if' of a dispatch condition. return (lo,hi) token range of the handler."""
    while True:
        if not is_cond(i):
            raise Exception('not cond at %d'%i)
        cmp=toks[i+2][0]; n=toks[i+3][0]
        else_i,end_i=match_else_end(i+5)
        then_lo=i+5
        then_hi=(else_i if else_i is not None else end_i)
        if ev(op,cmp,n):
            lo,hi=then_lo,then_hi
        else:
            if else_i is None: return None
            if toks[else_i][0]=='elseif':
                i=else_i; continue
            lo,hi=else_i+1,end_i
        # descend if the chosen block starts with a dispatch cond
        if is_cond(lo) :
            # make sure the nested cond spans the whole block (tree node), else it's a handler starting with an if on k
            e2,en2=match_else_end(lo+5)
            if en2+1==hi or (toks[en2+1][0]==';' and en2+2==hi): i=lo; continue
        return lo,hi
def text(lo,hi): return s[toks[lo][1]:toks[hi-1][2]]
ops=[int(x) for x in sys.argv[1:]]
root=0
assert toks[0][0]=='if'
for op in ops:
    r=leaf(op,root)
    print('--- op',op,'---')
    print(text(*r)[:300] if r else 'None')
