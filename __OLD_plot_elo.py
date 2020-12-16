import os
import pandas as pd
import matplotlib.pyplot as plt
from parameters.parameters import SOURCE_FOLDER, FIG_FOLDER

data_path = os.path.join(SOURCE_FOLDER, "elo_matrix_ProspecTonk.xlsx")

print(f"Reading from '{data_path}'...", end=" ", flush=True)
df = pd.read_excel(data_path)
df.date = pd.to_datetime(df.date)
# monkeys = 'Abr', 'Ala', 'Bar', 'Ces', 'Dor', 'Nem', 'Pac', 'Yoh'
#
# fig, ax = plt.subplots()
# for m in monkeys:
#     m = m.lower()
#     ax.plot(df[m], label=m)
#
# ax.set_xlabel('time')
# ax.set_ylabel('elo rating')
# plt.legend()
# plt.savefig(os.path.join(FIG_FOLDER, "elo.pdf"))
