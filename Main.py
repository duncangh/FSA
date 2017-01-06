import pandas as pd
import numpy as np
from Graham.Standard import Standardize as model


def run(sym):
    """

    :param sym: Enter the ticker symbol you want model data from
    :return:
    """

print(model('TSLA').make_model())


