from analysis import analysis
from analysis.summary import summary
from plot.figure_1 import figure_1
from plot.figure_supplementary import figure_supplementary


from analysis.model_based.model import AgentSideAdditive


def main():

    a = analysis.run(
        limit_n_trial=2000,
        limit_side_freq=0.80,
        force=False,
        monkeys='all',   # ('Abr', 'Ala', )
        class_model=AgentSideAdditive,
        n_trials_per_chunk=200,
        n_trials_per_chunk_control=200,
        method='SLSQP',
        skip_exception=False
    )
    print("Monkeys selected:", a.monkeys)
    summary.export_csv(a)
    figure_1(a)
    figure_supplementary(a)


if __name__ == '__main__':
    main()
