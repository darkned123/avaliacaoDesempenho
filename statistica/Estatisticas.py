class Estatistica():

    def __init__(self, num_avioes, tempo_solo, tempo_termino , numAv_atendidos, tempo_finger, num_avioes_finger):
        self.num_avioes = num_avioes
        self.tempo_solo = tempo_solo
        self.tempo_termino = tempo_termino
        self.numAv_atendidos = numAv_atendidos
        self.tempo_finger = tempo_finger
        self.num_avioes_finger = num_avioes_finger

    def temp_med_solo(self):
        tempo_total = 0
        for i in self.tempo_solo:
            tempo_total = tempo_total + i
        return tempo_total/self.num_avioes

    def num_av_atendidos(self):
        hora = self.tempo_termino/60 #considerei qque temp_termino fosse em minutos por exemplo
        return self.numAv_atendidos/hora


    '''
    TEM Q CONVERTER PRA MINUTOOO
    '''
    def uti_pista(self, tempo_pista):
        tempo_totalP = 0
        for k in tempo_pista:
            tempo_totalP += k
        return tempo_totalP/ self.numAv_atendidos


    def uti_finger(self):
        tempo_total = 0
        for l in self.tempo_finger:
            tempo_total = tempo_total + l
        return tempo_total/self.num_avioes_finger
