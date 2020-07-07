import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "MonkeyAnalysis.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()
import numpy as np
import pandas as pd

from data_interface.models import Data
from parameters.parameters import EXPORT_FOLDER, \
    GAIN, LOSS, CONTROL_CONDITIONS, SIG_STEEP, SIG_MID


def export_csv(a):
    data = dict()
    data["monkey"] = [m for m in a.monkeys]
    for cond in GAIN, LOSS:
        for param in "distortion", "risk_aversion", "precision", "side_bias":
            xs = [a.cpt_fit[m][cond][param] for m in a.monkeys]
            x = [np.mean(i) for i in xs]
            data[f"{cond}__{param}"] = x

        if cond == GAIN:
            entries = Data.objects.filter(is_gain=True, is_risky=True)
        elif cond == LOSS:
            entries = Data.objects.filter(is_loss=True, is_risky=True)
        else:
            raise ValueError
        data[f"{cond}_risky__n_trial"] = [
            entries.filter(monkey=m).count() for m in a.monkeys
        ]

    for control_condition in CONTROL_CONDITIONS:
        for param in SIG_STEEP, SIG_MID:
            data[f"{cond}__{control_condition}__{param}"] = \
                [a.control_sig_fit[m][control_condition]['fit'][param]
                 for m in a.monkeys]

    # include demographic / ranking data
    col_names = ["idname", "DS", "EloRating", "weight", "oldDS", "gender"]
    df = pd.read_excel(os.path.join('data', 'source', 'demo_ranking.xlsx'),
                       usecols=col_names,
                       sheet_name='data')

    for c in col_names[1:]:
        d = [df[df["idname"] == m][c].item() for m in a.monkeys]
        data[c] = d   # [df[df["idname"] == m][c] for m in a.monkeys]

    path_bkp = os.path.join(EXPORT_FOLDER, f"param.csv")
    df = pd.DataFrame(data=data)
    df.to_csv(path_bkp, index=False)
    print(f"CSV summary created at '{path_bkp}'")
