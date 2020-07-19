m = GEKKO()

capital = m.Param(value=4000)
appeceament = m.Param(value=4)

real_investment = m.Var()
final_investment = m.Var()
reserve = m.Var()
gold = m.Var()
shares = m.Var()
usd = m.Var()

f1 = m.Var()
f2 = m.Var()

m.Equation(usd >= final_investment*0.2)
m.Equation(gold >= final_investment*0.2)
m.Equation(shares >= final_investment*0.2)
m.Equation(real_investment + reserve == capital)
m.Equation(usd+gold+shares == final_investment)
m.Equation(final_investment == real_investment*appeceament)

# crisis 2000
m.Equation(
    (usd*1.3884) +
    (gold*1.1966) +
    (shares*0.5257) -
    final_investment > -1*(real_investment*f1))

# crisis 2008
m.Equation(
        (usd*1.2265) +
        (gold*1.2540) +
        (shares*0.4674) -
        final_investment > -1*(real_investment*f2))

m.Equation(capital * 0.6 == real_investment)
m.Equation(capital * 0.4 == reserve)

m.Obj(f1+f2)

m.options.IMODE = 3
m.solve(disp=False)
print(usd.value, gold.value, shares.value)
