import fst

syms = fst.SymbolTable()
t = fst.Transducer(syms,syms)
t.add_arc(0,1,'*','*')
## Digraphs.
t.add_arc(1,2,'ae','e')
t.add_arc(1,2,'oe',chr(248))
t.add_arc(1,2,'ph','f')
t.add_arc(1,2,'qu','kv')
## 'c' conversion.
t.add_arc(1,3,'c','ts')
t.add_arc(3,2,'VP','VP')
t.add_arc(1,4,'c','k')
t.add_arc(4,2,'^VP','^VP')
## 'gu' conversion.
t.add_arc(1,5,'gu','gv')
t.add_arc(5,2,'V','V')
## 'ti' conversion.
t.add_arc(1,6,'[^stx]','[^stx]')
t.add_arc(6,5,'ti','tsi')
#t.add_arc(7,5,fst.EPSILON,fst.EPSILON)
## 'ch' conversion.
## E.g. schola.
t.add_arc(1,7,fst.EPSILON,fst.EPSILON)
t.add_arc(7,7,'C','C')
t.add_arc(7,2,'ch','k')
## E.g.echinacea.
t.add_arc(1,8,'V','V')
t.add_arc(8,9,fst.EPSILON,fst.EPSILON)
t.add_arc(9,9,'C','C')
t.add_arc(9,2,'ch','h')
## Finish.
t.add_arc(2,10,'*','*')
t[10].final = True
print t.isyms
print t.osyms
t.write('g2p.fst')
