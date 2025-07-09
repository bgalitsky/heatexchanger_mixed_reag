# heat_exchanger_model.py

from dataclasses import dataclass
from typing import List
import math
import tkinter as tk
from tkinter import ttk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

@dataclass
class ComponentData:
    name: str
    share: float
    T_b: float     # Boiling point [K]
    C_f: float     # Specific heat capacity (liquid) [kJ/kg·K]
    C_p: float     # Specific heat capacity (vapor) [kJ/kg·K]
    r_f: float     # Latent heat of vaporization [kJ/kg]

@dataclass
class InOutData:
    T_in_cold: float = 300.0
    T_in_hot: float = 420.0
    T_out_cold: float = 350.0
    T_out_hot: float = 360.0
    g_cold: float = 1.0
    g_hot: float = 1.0
    P_cold: float = 0.0
    P_hot: float = 0.0
    Sigma: float = 0.0
    K: float = 0.0
    Q: float = 0.0
    W_cold: float = 0.0
    W_hot: float = 0.0
    A: float = 0.0
    B: float = 0.0

stoffe = {
    "Water": ComponentData("Water", 1.0, 373.0, 4.2, 2.0, 2260.0),
    "Ethanol": ComponentData("Ethanol", 1.0, 351.5, 2.44, 1.42, 846.0),
    "Nitrogen": ComponentData("Nitrogen", 1.0, 77.4, 2.04, 1.04, 200.0),
}

def calculate_Cf(components: List[ComponentData], T: float) -> float:
    return sum(c.share * (c.C_f if T < c.T_b else c.C_p) for c in components)

def calculate_Q(F: InOutData, cold_components: List[ComponentData]) -> float:
    Cf_cold = calculate_Cf(cold_components, F.T_in_cold)
    F.W_cold = F.g_cold * Cf_cold
    F.Q = round((F.T_in_hot - F.T_out_hot) * F.W_cold, 5)
    return F.Q

def calculate_T_out_hot(F: InOutData, hot_components: List[ComponentData]) -> float:
    Cf_hot = calculate_Cf(hot_components, F.T_in_hot)
    F.W_hot = F.g_hot * Cf_hot
    F.T_out_hot = round(F.T_in_hot - (F.Q / F.W_hot), 5)
    return F.T_out_hot

def calculate_sigma(F: InOutData) -> float:
    if all(t > 0 for t in [F.T_in_hot, F.T_out_hot, F.T_in_cold, F.T_out_cold]):
        F.Sigma = round(
            F.W_hot * math.log(F.T_out_hot / F.T_in_hot) +
            F.W_cold * math.log(F.T_out_cold / F.T_in_cold), 5)
    return F.Sigma

def schema1(F: InOutData):
    F.Q = round(F.K * (F.T_out_hot - F.T_out_cold), 5)
    if (F.T_in_hot - F.T_in_cold) > (F.B * F.Q):
        F.K = round(F.Q / (F.T_out_hot - F.T_out_cold), 5)

# GUI
class HeatExchangerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Heat Exchanger Calculator")

        labels = ["T_in_cold", "T_out_cold", "T_in_hot", "T_out_hot", "g_cold", "g_hot"]
        self.entries = {}
        defaults = {
            "T_in_cold": "300",
            "T_out_cold": "350",
            "T_in_hot": "420",
            "T_out_hot": "360",
            "g_cold": "1.0",
            "g_hot": "1.0"
        }

        for i, label in enumerate(labels):
            ttk.Label(root, text=label).grid(row=i, column=0, sticky=tk.W)
            entry = ttk.Entry(root)
            entry.grid(row=i, column=1)
            entry.insert(0, defaults[label])
            self.entries[label] = entry

        ttk.Label(root, text="Cold Fluid").grid(row=0, column=2, padx=10)
        self.combo_cold = ttk.Combobox(root, values=list(stoffe.keys()), state="readonly")
        self.combo_cold.grid(row=0, column=3)
        self.combo_cold.set("Water")

        ttk.Label(root, text="Hot Fluid").grid(row=1, column=2, padx=10)
        self.combo_hot = ttk.Combobox(root, values=list(stoffe.keys()), state="readonly")
        self.combo_hot.grid(row=1, column=3)
        self.combo_hot.set("Ethanol")

        ttk.Button(root, text="Compute", command=self.compute).grid(row=6, column=0, columnspan=2)
        ttk.Button(root, text="Plot T vs Time", command=self.plot_temperatures).grid(row=6, column=2, columnspan=2)

        self.output_text = tk.Text(root, height=8, width=60)
        self.output_text.grid(row=7, column=0, columnspan=4)

    def compute(self):
        try:
            self.F = InOutData(
                T_in_cold=float(self.entries["T_in_cold"].get()),
                T_out_cold=float(self.entries["T_out_cold"].get()),
                T_in_hot=float(self.entries["T_in_hot"].get()),
                T_out_hot=float(self.entries["T_out_hot"].get()),
                g_cold=float(self.entries["g_cold"].get()),
                g_hot=float(self.entries["g_hot"].get())
            )
            cold_mix = [stoffe[self.combo_cold.get()]]
            hot_mix = [stoffe[self.combo_hot.get()]]

            calculate_Q(self.F, cold_mix)
            calculate_T_out_hot(self.F, hot_mix)
            calculate_sigma(self.F)

            self.F.A = (self.F.W_cold - self.F.W_hot) / (self.F.W_hot * self.F.W_cold)
            self.F.B = (self.F.W_cold + self.F.W_hot) / (self.F.W_hot * self.F.W_cold)

            schema1(self.F)

            output = f"Q = {self.F.Q}\nSigma = {self.F.Sigma}\nK = {self.F.K}\n"
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, output)
        except Exception as e:
            self.output_text.delete("1.0", tk.END)
            self.output_text.insert(tk.END, f"Error: {e}")

    def plot_temperatures(self):
        try:
            F = self.F
            time = list(range(11))
            T_cold = [F.T_in_cold + (F.T_out_cold - F.T_in_cold) * t / 10 for t in time]
            T_hot = [F.T_in_hot - (F.T_in_hot - F.T_out_hot) * t / 10 for t in time]

            fig, ax = plt.subplots()
            ax.plot(time, T_cold, label="Cold Stream", marker='o')
            ax.plot(time, T_hot, label="Hot Stream", marker='x')
            ax.set_xlabel("Time (arb. units)")
            ax.set_ylabel("Temperature (K)")
            ax.set_title("Temperature Profile of Streams")
            ax.legend()
            plt.grid(True)
            plt.show()

        except Exception as e:
            self.output_text.insert(tk.END, f"\nPlot Error: {e}")

if __name__ == "__main__":
    root = tk.Tk()
    app = HeatExchangerGUI(root)
    root.mainloop()
