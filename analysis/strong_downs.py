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

f1 = m.Var()
f2 = m.Var()
f3 = m.Var()
f4 = m.Var()
f5 = m.Var()

m.Equation(f1>=0)
m.Equation(f2>=0)
m.Equation(f3>=0)
m.Equation(f4>=0)
m.Equation(f5>=0)


m.Equation(usd >= final_investment*0.2)
m.Equation(gold >= final_investment*0.2)
m.Equation(shares >= final_investment*0.2)
m.Equation(real_investment + reserve == capital)
m.Equation(usd+gold + shares == final_investment)
m.Equation(final_investment == real_investment*appeceament)

# Strong down
m.Equation(
        (usd*1.1427) +  # 14.27
        (gold*0.9385) +  # -0.725
        (shares*0.7413) -  # -25.87
        final_investment > -1*(real_investment*f1))

# Strong down
m.Equation(
        (usd*1.0474) +  # 4.74
        (gold*1.0711) +  # 7.11
        (shares*0.7988) -  # -20.11
        final_investment > -1*(real_investment*f2))

# Strong down
m.Equation(
        (usd*1.0043) +  # 0.43
        (gold*1.0032) +  # 0.32
        (shares*0.7819) -  # -21.81
        final_investment > -1*(real_investment*f3))

# Strong down
m.Equation(
        (usd*1.0462) +  # 4.62
        (gold*0.9866) +  # -1.244
        (shares*0.7437) -  # -25.63
        final_investment > -1*(real_investment*f4))

# Crisis corona
m.Equation(
        (usd*1.056) +  # 5.6
        (gold*0.966) +  # -3.4
        (shares*0.7882) -  # -21.18
        final_investment > -1*(real_investment*f5))

m.Equation(capital*0.6 == real_investment)
m.Equation(capital*0.4 == reserve)

m.Obj(f1+f2+f3+f4+f5)

m.options.IMODE = 3
m.solve(disp=False)
print(usd.value, gold.value, shares.value)
print(f1.value, f2.value, f3.value, f4.value, f5.value)
