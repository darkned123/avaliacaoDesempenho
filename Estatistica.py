
import statistics as st
import scipy as sp
import scipy.stats
import numpy as np


class Estatistica:

    def uti_link_p(self, tempo_fila, temp_env):
        tempo_totalP = 0
        for k in tempo_fila:
            tempo_totalP += k

        return tempo_totalP / temp_env

        # tempo medio de resposta

    def tempo_medio_resp(self, tempoTotal):
        tempo = 0
        for i in tempoTotal:
            tempo += i

        self.tmresp = tempo / len(tempoTotal)
        return self.tmresp

    def taxa_process(self, tempoTotal):

        tempo = 0.0
        for i in tempoTotal:
            tempo += i

        return len(tempoTotal) / tempo

    def confidence_med_dv(self, data, confidence=0.95):
        n = len(data)
        std = st.stdev(data)
        m, se = st.mean(data), scipy.stats.sem(data)
        h = se * sp.stats.t._ppf((1 + confidence) / 2., n - 1)
        return (m, m - h, m + h, std)