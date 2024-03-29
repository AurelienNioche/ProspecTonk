import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE",
                      "ProspecTonk.settings")
from django.core.wsgi import get_wsgi_application

application = get_wsgi_application()

from data_interface.models import Data

import numpy as np
import traceback
import warnings
import pickle
import collections

from parameters.parameters import BACKUP_FOLDER, GAIN, LOSS
from analysis.model_free import get_control_data, get_risk_sig_fit

from analysis.model_based.stats import stats_regression_best_values
from analysis.model_based.parameter_estimate import get_parameter_estimate
# , get_info_data   # , get_control_history_data


def nested_dict():
    return collections.defaultdict(nested_dict)


class Analysis:

    def __init__(self, class_model, limit_n_trial=2000,
                 limit_side_freq=0.80, **kwargs):

        self.class_model = class_model

        self.monkeys = None
        self.n_monkey = None

        # self.info_data = nested_dict()
        self.control_data = nested_dict()
        # self.control_stats = nested_dict()
        # self.freq_risk_data = nested_dict()
        self.hist_best_param_data = nested_dict()
        self.hist_control_data = nested_dict()

        self.cpt_fit = nested_dict()
        self.risk_sig_fit = nested_dict()
        self.control_sig_fit = nested_dict()

        self.limit_n_trial = limit_n_trial
        self.limit_side_freq = limit_side_freq

        self._pre_process_data(**kwargs)

    def get_monkeys(self):

        selected_monkeys = []

        monkeys = list(np.unique(Data.objects.values_list("monkey")))
        print("All monkeys:", monkeys)

        for m in monkeys:
            keep = True
            entries_m = Data.objects.filter(monkey=m)

            for cond in GAIN, LOSS:

                if cond == GAIN:
                    entries = entries_m.filter(is_gain=True)
                elif cond == LOSS:
                    entries = entries_m.filter(is_loss=True)
                else:
                    raise ValueError

                n_trial = entries.count()
                if n_trial < self.limit_n_trial:
                    print(f"Monkey '{m}' has only {n_trial} trials in condition '{cond}', "
                          f"it will not be included in the analysis")
                    keep = False

                n_right = entries.filter(c=1).count()
                prop_right = n_right / n_trial
                if not 1 - self.limit_side_freq <= prop_right <= self.limit_side_freq:
                    print(
                        f"Monkey '{m}' choose the right option {prop_right * 100:.2f}% of the time in condition '{cond}', "
                        f"it will not be included in the analysis")
                    keep = False

            if keep:
                selected_monkeys.append(m)

        print("Selected monkeys:", selected_monkeys)
        return selected_monkeys

    def _pre_process_data(self,
                          skip_exception=True,
                          monkeys=None, **kwargs):

        if monkeys in (None, 'all'):
            monkeys = self.get_monkeys()

        black_list = []

        for m in monkeys:

            try:
                self._analyse_monkey(m=m, **kwargs)

            except Exception as e:
                if skip_exception:
                    track = traceback.format_exc()
                    msg = \
                        f"\nWhile trying to pre-process the data for " \
                        f"monkey '{m}', " \
                        f"I encountered an error. " \
                        "\nHere is the error:\n\n" \
                        f"{track}\n" \
                        f"I will skip the monkey '{m}' " \
                        f"from the rest of the analysis"
                    warnings.warn(msg)
                    black_list.append(m)
                else:
                    raise e

        for m in black_list:
            monkeys.remove(m)
            # self.info_data.pop(m, None)
            self.control_data.pop(m, None)
            # self.freq_risk_data.pop(m, None)
            self.hist_best_param_data.pop(m, None)
            self.hist_control_data.pop(m, None)
            self.control_sig_fit.pop(m, None)
            self.cpt_fit.pop(m, None)
            self.risk_sig_fit.pop(m, None)

        self.monkeys = monkeys
        self.n_monkey = len(monkeys)

    def _analyse_monkey(self, m, method,
                        n_trials_per_chunk=None,
                        n_chunk=None,
                        n_trials_per_chunk_control=None,
                        n_chunk_control=None,
                        randomize_chunk_trials=False, force=True,):

        print()
        print("-" * 60 + f" {m} " + "-" * 60 + "\n")

        # for cond in (GAIN, LOSS)
        #
        # if cond == GAIN:
        #     entries = Data.objects.filter(monkey=m, is_gain=True)
        # elif cond == LOSS:
        #     entries = Data.objects.filter(monkey=m, is_loss=True)
        #
        # else:
        #     raise ValueError

        entries = Data.objects.filter(monkey=m)

        # Sort the data, run fit, etc.
        # self.info_data[m] = get_info_data(entries=entries, monkey=m)

        # Control data
        self.control_data[m], self.control_sig_fit[m], self.control_hist = \
            get_control_data(entries,
                             n_trials_per_chunk=n_trials_per_chunk_control,
                             n_chunk=n_chunk_control,
                             randomize=False)

        # # history of performance for control trials
        # self.hist_control_data[m] = \
        #     get_control_history_data(
        #         entries=entries,
        #         n_trials_per_chunk=n_trials_per_chunk_control,
        #         n_chunk=n_chunk_control)
        # self.control_stats[cond][m] = \
        #     get_control_stats(self.control_data[cond][m])

        # self.control_sigmoid_data[m] = \
        #     get_control_sigmoid_data(entries)
        # self.control_sig_fit[m] = {
        #
        # }
        #     {cd: self.control_sigmoid_data[cond][m][cd]['fit']
        #      for cd in CONTROL_CONDITIONS}

        for cond in (GAIN, LOSS):
            self.risk_sig_fit[m][cond] = get_risk_sig_fit(entries)

            self.cpt_fit[m][cond] = get_parameter_estimate(
                cond=cond,
                entries=entries,
                force=force,
                n_trials_per_chunk=n_trials_per_chunk,
                n_chunk=n_chunk,
                randomize=randomize_chunk_trials,
                class_model=self.class_model,
                method=method)

            # Stats for comparison of best parameter values
            self.hist_best_param_data[m][cond] = \
                stats_regression_best_values(
                        fit=self.cpt_fit[m][cond],
                        class_model=self.class_model)


def run(class_model, force, **kwargs):

    print("*" * 150)
    print(f"Using model '{class_model.__name__}'")
    print("*" * 150)
    print()

    bkp_file = os.path.join(BACKUP_FOLDER,
                            f"analysis_{class_model.__name__}")

    if not os.path.exists(bkp_file) or force:
        a = Analysis(class_model=class_model, force=force, **kwargs)
        pickle.dump(a, open(bkp_file, "wb"))
    else:
        a = pickle.load(open(bkp_file, "rb"))

    return a
