from gekko import GEKKO
m = GEKKO()

capital = m.Param(value=4000)
appeceament = m.Param(value=4)

real_investment = m.Var()
final_investment = m.Var()
reserve = m.Var()
gold = m.Var()
shares = m.Var()
usd = m.Var()

m.Equation(usd >= final_investment*0.2)
m.Equation(gold >= final_investment*0.2)
m.Equation(shares >= final_investment*0.2)
m.Equation(real_investment + reserve == capital)
m.Equation(usd+gold + shares == final_investment)
m.Equation(final_investment == real_investment*appeceament)

# Slow down
m.Equation(
        (usd*1.0570) +  # 5.70
        (gold*1.0650) +  # 6.50
        (shares*0.7951) -  # -20.49
        final_investment > -1*(real_investment*0))

# Slow down
m.Equation(
        (usd*1.1004) +  # 10.04
        (gold*0.9634) +  # -3.66
        (shares*0.8781) -  # -12.19
        final_investment > -1*(real_investment*0))

m.Equation(capital*0.6 == real_investment)
m.Equation(capital*0.4 == reserve)

m.options.IMODE = 3
m.solve(disp=False)
print(usd.value, gold.value, shares.value)