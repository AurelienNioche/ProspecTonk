import os
import numpy as np
import math
import matplotlib.pyplot as plt

from .subplot import history_control
from .subplot import precision
from .subplot import probability_distortion
from .subplot import utility
from .subplot import control
from .subplot import risk_sig_fit
from .subplot import control_sigmoid
from .subplot import history_best_param
# from .subplot import info
from .subplot import best_param_distrib
from .subplot import LLS_BIC_distrib

from plot.tools.tools import add_letter

from parameters.parameters import CONTROL_CONDITIONS, \
    FIG_FOLDER, GAIN, LOSS


def figure_supplementary(a):

    fig_ind(a)
    fig_control(a)
    fig_risk_sig_fit(a)
    fig_hist_param(a)


def fig_control(a):

    for control_condition in CONTROL_CONDITIONS:
        n_monkey = len(a.monkeys)
        nrows, ncols = n_monkey, 1
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                                 figsize=(2.5*ncols, 2.5*nrows))

        if LOSS not in control_condition:
            color = 'C0'
        elif GAIN not in control_condition:
            color = 'C1'
        else:
            color = 'black'
        axes = axes.flatten()

        # show_ylabel = [True, False]

        for i, m in enumerate(a.monkeys):
            add_letter(axes[i], i=i)
            control_sigmoid.plot(
                ax=axes[i], data=a.control_sig_fit[m][control_condition],
                control_condition=control_condition,
                color=color,
                show_ylabel=True,
                dot_size=50)

        fig_path = os.path.join(FIG_FOLDER, f"figure_{control_condition}.pdf")
        plt.tight_layout()
        plt.savefig(fig_path)
        print(f"Figure {fig_path} created!")


def fig_risk_sig_fit(a):

    nrows, ncols = math.ceil(len(a.monkeys)/3), 6
    fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                             figsize=(2.5*ncols, 2.5*nrows))

    axes = axes.flatten()

    colors = ['C0', 'C1']
    show_ylabel = [True, False]

    k = 0
    for i, m in enumerate(a.monkeys):
        add_letter(axes[k], i=i)
        for j, cond in enumerate((GAIN, LOSS)):
            risk_sig_fit.plot(
                ax=axes[k], data=a.risk_sig_fit[m][cond],
                color=colors[j], show_ylabel=show_ylabel[j],
                dot_size=50)
            k += 1

    for ax in axes[k:]:
        ax.set_axis_off()

    fig_path = os.path.join(FIG_FOLDER, "figure_risk_sig_fit.pdf")
    plt.tight_layout()
    plt.savefig(fig_path)
    print(f"Figure {fig_path} created!")


def fig_ind(a):

    colors = ['C0', 'C1']
    # show_ylabel = [True, False]

    for j, cond in enumerate((GAIN, LOSS)):
        nrows, ncols = math.ceil(len(a.monkeys)/2), 6
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                                 figsize=(2.5 * ncols, 2.5 * nrows))

        axes = axes.flatten()
        k = 0
        for i, m in enumerate(a.monkeys):
            add_letter(axes[k], i=i)
            data = {'class_model': a.class_model,
                    'cond': cond}
            for param in ("risk_aversion", "distortion",
                          "precision", "side_bias"):
                data[param] = a.cpt_fit[m][cond][param]

            utility.plot(ax=axes[k], data=data, color=colors[j])
            probability_distortion.plot(
                ax=axes[k+1], data=data, color=colors[j])
            precision.plot(ax=axes[k+2], data=data, color=colors[j])
            k += 3

        for ax in axes[k:]:
            ax.set_axis_off()

        fig_path = os.path.join(FIG_FOLDER, f"fig_ind_{cond}.pdf")
        plt.tight_layout()
        plt.savefig(fig_path)
        print(f"Figure {fig_path} created!")


def fig_hist_param(a):

    colors = ['C0', 'C1']
    # show_ylabel = [True, False]

    for j, cond in enumerate((GAIN, LOSS)):
        nrows, ncols = len(a.monkeys), 4
        fig, axes = plt.subplots(nrows=nrows, ncols=ncols,
                                 figsize=(2.5 * ncols, 2.5 * nrows))

        axes = axes.flatten()
        k = 0
        for i, m in enumerate(a.monkeys):
            add_letter(axes[k], i=i)
            for param in ("risk_aversion", "distortion",
                          "precision", "side_bias"):
                data = a.cpt_fit[m][cond][param]
                regress = a.hist_best_param_data[m][cond][param]

                history_best_param.plot(axes=axes[k],
                                        data=data,
                                        regress=regress,
                                        color=colors[j])
                k += 1

        for ax in axes[k:]:
            ax.set_axis_off()

        fig_path = os.path.join(FIG_FOLDER, f"fig_ind_{cond}.pdf")
        plt.tight_layout()
        plt.savefig(fig_path)
        print(f"Figure {fig_path} created!")