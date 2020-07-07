import numpy as np

from parameters.parameters import SAME_P, SAME_X, GAIN, LOSS, GAIN_VS_LOSS

from analysis.model_free.sigmoid_fit.sigmoid_fit import sigmoid_fit


def get_control_data(entries, **kwargs_history):

    print("Getting the control data...", end=' ', flush=True)

    data = {}
    data_sigmoid = {}
    data_history = {}
    for cond in (GAIN, LOSS):
        if cond == GAIN:
            d_cond = entries.filter(is_gain=True)
        else:
            d_cond = entries.filter(is_loss=True)

        e = d_cond.filter(is_same_p=True)
        label = f"{cond}__{SAME_P}"
        data[label] = _compute_success_rate_per_pair(e)
        data_sigmoid[label] = _fit_sigmoid(e)
        data_history[label] = _history(e, **kwargs_history)

        e = d_cond.filter(is_same_x=True)
        label = f"{cond}__{SAME_X}"
        data[label] = _compute_success_rate_per_pair(e)
        data_sigmoid[label] = _fit_sigmoid(e)
        data_history[label] = _history(e, **kwargs_history)

    e = entries.filter(is_gain_vs_loss=True)
    data[GAIN_VS_LOSS] = _compute_success_rate_per_pair(e)
    data_sigmoid[GAIN_VS_LOSS] = _fit_sigmoid(e)
    data_history[label] = _history(e, **kwargs_history)

    print("Done!")

    return data, data_sigmoid, data_history


def _compute_success_rate_per_pair(entries):

    data = []
    unq_pairs = np.unique(entries.values_list('pair_id', flat=True))

    for p_id in unq_pairs:
        d_pair = entries.filter(pair_id=p_id)
        n_success = d_pair.filter(choose_best=True).count()
        n = d_pair.count()
        success_rate = n_success / n
        data.append(success_rate)

    return data


def _history(entries, n_chunk, n_trials_per_chunk, randomize):

    parts = _get_chunks(entries, n_chunk=n_chunk,
                        n_trials_per_chunk=n_trials_per_chunk,
                        randomize=randomize)

    unq_pairs = np.unique(entries.values_list('pair_id', flat=True))

    data = []
    for pt in parts:

        data_pt = []

        for p_id in unq_pairs:
            d_pair = entries.filter(pair_id=p_id, id__in=pt)
            n_success = d_pair.filter(choose_best=True).count()
            n = d_pair.count()
            if n > 0:
                success_rate = n_success / n
                data_pt.append(success_rate)
        data.append(data_pt)
    return data


def _get_chunks(entries, n_chunk=None, n_trials_per_chunk=None,
                randomize=False):

    entries = entries.order_by("id")

    idx = np.array(entries.values_list("id", flat=True))
    n = len(idx)

    if n_chunk is None:
        assert n_trials_per_chunk is not None
        n_chunk = n // n_trials_per_chunk
        remainder = n % n_trials_per_chunk
    else:
        remainder = n % n_chunk

    # Drop the remainder
    if remainder > 0:
        idx = idx[remainder:]

    if randomize:
        np.random.shuffle(idx)

    parts = np.split(idx, n_chunk)

    # print(f'Chunk using '
    #       f'{"chronological" if not randomize else "randomized"} '
    #       f'order')
    # print(f'N trials = {n - remainder}')
    # print(f'N parts = {len(parts)} '
    #       f'(n trials per part = {int((n - remainder) / n_chunk)}, '
    #       f'remainder = {remainder})')

    return parts


def _fit_sigmoid(entries):

    x, y = [], []
    unq_pairs = np.unique(entries.values_list('pair_id', flat=True))

    for p_id in unq_pairs:
        for side in (0, 1):
            d_pair_sided = entries.filter(pair_id=p_id, is_reversed=side)

            n_choose_right = d_pair_sided.filter(c=1).count()
            n = d_pair_sided.count()
            if n > 0:
                prop = n_choose_right / n

                first_pair = d_pair_sided[0]
                ev_right_minus_ev_left = \
                    (first_pair.x1 * first_pair.p1) \
                    - (first_pair.x0 * first_pair.p0)

                x.append(ev_right_minus_ev_left)
                y.append(prop)

    try:
        fit = sigmoid_fit(x=x, y=y)
    except RuntimeError as e:
        print(e)
        fit = None

    return {'x': x, 'y': y, 'fit': fit}


# def get_control_stats(data):
#     def iqr(x):
#
#         n = len(x)
    #     perc_75, perc_25 = np.percentile(x, [75, 25])
    #
    #     # print(f'N: {n}')
    #     #
    #     # print(f'median: {np.median(x):.02f} '
    #     #       f'(IQR = {perc_25:.02f} -- {perc_75:.02f})')
    #
    #     return np.median(x), (perc_25, perc_75)

#     res = {}
#     for cd in CONTROL_CONDITIONS:
#         median, _iqr = iqr(data[cd])
#         res[cd] = {
#             'median': median,
#             'iqr': _iqr,
#         }
#
#         print(f"Condition '{cd}': n={len(data[cd])}, median={median:.2f}, "
#               f"IQR = [{_iqr[0]:.2f}, {_iqr[1]:.2f}], "
#               f"IQR comprises values <= 0.5: {_iqr[0] <=0.5}")
