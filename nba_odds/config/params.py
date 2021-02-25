""" Parameters used for features and model. """


class PerParams:
    """ Parameters used for PER computation. """
    min_mp = 20
    min_sum_mp = 100
    min_games_played = 5

    good_player_per_threshold = 0.85

class LogisticRegressionParams:
    """ Model parameters """
    C = 0.75
    max_iter = 90
    multi_class = 'ovr'
    penalty = 'l1'
    solver = 'liblinear'

