import math

# Данные
G_hot = 2.0 # кг/с
Cp_hot = 1750 # Дж/кг·К
T_hot_in = 370 # К
T_hot_min = 353.2 # К (кипение бензола)

G_cold = 1.5 # кг/с
Cp_cold = 3300 # Дж/кг·К
T_cold_in = 290 # К
T_cold_max = 351.4 # К (кипение спирта)

U = 500 # Вт/м2·К

# Теплоёмкости

C_hot = G_hot * Cp_hot
C_cold = G_cold * Cp_cold
C_min = min(C_hot, C_cold)
C_max = max(C_hot, C_cold)
Cr = C_min / C_max

# Максимально допустимое тепло, чтобы горячий поток не охладился ниже T_hot_min
Q_max = C_hot * (T_hot_in - T_hot_min)

# Фактическая эффективность
epsilon = Q_max / (C_min * (T_hot_in - T_cold_in))

# Численный расчёт NTU методом подбора
def calculate_ntu(epsilon_target, Cr, tol=1e-5, max_iter=100):
ntu = 0.1
for _ in range(max_iter):
exp_term = math.exp(-ntu * (1 - Cr))
epsilon_calc = (1 - exp_term) / (1 - Cr * exp_term)
if abs(epsilon_calc - epsilon_target) &lt; tol:
return ntu
ntu += 0.01
raise Exception(&quot;NTU not converged&quot;)

NTU = calculate_ntu(epsilon, Cr)

A = NTU * C_min / U # Площадь теплообмена

# Результаты
print(f&quot;Q_max = {Q_max:.2f} W&quot;)
print(f&quot;Effectiveness (ε) = {epsilon:.4f}&quot;)
print(f&quot;NTU = {NTU:.4f}&quot;)
print(f&quot;Required area A = {A:.4f} m²&quot;)
