import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# ====================================================================
# NAJLEPSZY MODEL: 3 HARMONICZNE (Roczna + Półroczna + 4-miesięczna) + TREND + ŚRODEK
# ====================================================================

# 1. Wczytanie i przygotowanie czasu w latach
df = pd.read_csv('daily_ice_edge.csv')
df['Date'] = pd.to_datetime(df['Date'])
t_years = (df['Date'] - df['Date'].min()).dt.days.values / 365.25
longitude_cols = [col for col in df.columns if col != 'Date']

# 2. Budowa macierzy zmiennych niezależnych (Idealny balans elastyczności)
omega = 2 * np.pi
X_all = np.column_stack([
    t_years,                      # Trend liniowy
    np.sin(omega * t_years),      # A1 (1. harmoniczna - roczna)
    np.cos(omega * t_years),      # C1 
    np.sin(2 * omega * t_years),  # A2 (2. harmoniczna - półroczna)
    np.cos(2 * omega * t_years),  # C2 
    np.sin(3 * omega * t_years),  # A3 (3. harmoniczna - 4-miesięczna)
    np.cos(3 * omega * t_years)   # C3
])

# Słownik zapobiegający fragmentacji pamięci RAM
modeled_data_dict = {'Date': df['Date']}
stats_list = []

print("Trwa obliczanie Modelu 3-Harmonicznego (Złoty Środek)...")

# 3. Pętla wyliczająca model dla każdego sektora (kąta)
for col in longitude_cols:
    y = df[col].values
    valid_mask = ~np.isnan(y)
    
    if valid_mask.sum() > 50:
        X_train = X_all[valid_mask]
        y_train = y[valid_mask]
        
        # Analityczne rozwiązanie regresji (gwarancja globalnego minimum)
        model = LinearRegression().fit(X_train, y_train)
        
        # Zapisanie idealnie dopasowanej fali do słownika
        modeled_data_dict[col] = model.predict(X_all)
        
        # Obliczenie rzetelnych statystyk na podstawie twardych danych
        y_pred_train = model.predict(X_train)
        res = y_train - y_pred_train
        r2 = model.score(X_train, y_train)
        rmse = np.sqrt(np.mean(res**2))
        mae = np.mean(np.abs(res))
        
        # Pobranie parametrów do ostatecznego wzoru
        wagi = model.coef_
        stats_list.append({
            'Kat': col, 
            'Offset': model.intercept_, 
            'Trend': wagi[0],
            'A1': wagi[1], 'C1': wagi[2], 
            'A2': wagi[3], 'C2': wagi[4], 
            'A3': wagi[5], 'C3': wagi[6],
            'R2': r2, 'RMSE': rmse, 'MAE': mae
        })
    else:
        # Zabezpieczenie przed brakiem danych
        modeled_data_dict[col] = np.full(len(df), np.nan) 

# 4. Konstrukcja końcowych tabel i eksport wyników
df_modeled = pd.DataFrame(modeled_data_dict)
df_stats = pd.DataFrame(stats_list)

# Zapis twardych dowodów na dysk
df_stats.to_csv('parametry_najlepszy_model_3_harmoniczne.csv', index=False)

print("="*60)
print(" 📊 RAPORT: MODEL ELASTYCZNY (ZWYCIĘZCA ANALIZY)")
print("="*60)
print(f"Średni współczynnik R²: {df_stats['R2'].mean():.4f}")
print(f"Średni błąd MAE:        {df_stats['MAE'].mean():.3f}°")
print(f"Średni błąd RMSE:       {df_stats['RMSE'].mean():.3f}°")
print("="*60)
print("Gotowe 'recepty' matematyczne znajdziesz w pliku 'parametry_najlepszy_model_3_harmoniczne.csv'.")
