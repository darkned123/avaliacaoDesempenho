

from trabalhofinal.Estatistica import Estatistica
import random
import itertools
import simpy

"tudo em ms, Kbyte ou Kbyteps"
SEED = 500
TAXA_CHEGADA = [2000,4000]
SIM_TIME = 43200000
LATENCIA = 0.05
USUARIOS = 150
RTT = 0.01
HTTP = 0.1
VEL_LAN = 1000000
VEL_DISCO = 6
CACHE_HIT =80
#VEL_LINK = 0.007  #Velocidade de 56kbps em Kbytesms
VEL_LINK = 0.193   #Velocidade de 1,544Mbps em Kbytesms
VEL_CPU_HIT = 0.25
VEL_CPU_MISS = 0.5

"""Quantidade recurso"""
LAN = 1
ROTEADOR = 1
DISCO = 1
CPU = 1
LINK_ENTRADA = 1
LINK_SAIDA = 1

USUARIO_INTERNET_MAX = USUARIOS/10
"""Tempos"""
TEMPO_LAN = []
TEMPO_CPU = []
TEMPO_DISCO = []
TEMPO_ROTEADOR = []
TEMPO_SAIDA = []
TEMPO_ENTRADA = []
TEMPO_TOTAL = []
totalTimeSimulation = []
def requi(env, lan, roteador, cpu, disco, linkSaida, linkEntrada, tamArquivo):
    tempoTotal = env.now

    achou = False

    with lan.request() as req:

        yield  req

        chegaLan = env.now

        yield env.timeout(float(HTTP/VEL_LAN))

        tempoLan = env.now - chegaLan


        TEMPO_LAN.append(tempoLan)


    with cpu.request() as req:


        yield req

        chegaCPU = env.now

        act =  random.randint(1, 100)

        if act <= CACHE_HIT:
            yield env.timeout(VEL_CPU_HIT)

            achou = True
        else:
            yield env.timeout(VEL_CPU_MISS)

        tempoCPU = env.now - chegaCPU

        TEMPO_CPU.append(tempoCPU)


    if not achou:

        with lan.request() as req:

            yield  req

            chegaLan = env.now

            yield env.timeout(float(HTTP/VEL_LAN))

            tempoLan = env.now - chegaLan

            TEMPO_LAN.append(tempoLan)

        with roteador.request() as req:
            yield req

            chegaRoteador = env.now

            yield env.timeout(LATENCIA)

            tempoRoteador = env.now - chegaRoteador

            TEMPO_ROTEADOR.append(tempoRoteador)

            #entra no lnk de saida
        with linkSaida.request() as req:

            yield req

            chegaSaida = env.now

            yield env.timeout(float(HTTP/VEL_LINK))

            tempoSaida = env.now - chegaSaida

            TEMPO_SAIDA.append(tempoSaida)



        yield env.timeout(RTT)

        with  linkEntrada.request() as req:

            yield req

            chegaEntrada = env.now

            yield env.timeout(float(tamArquivo/VEL_LINK))

            tempoEntrada = env.now - chegaEntrada

            TEMPO_ENTRADA.append(tempoEntrada)

        with roteador.request() as req:

            yield req

            chegaRoteador = env.now

            yield env.timeout(float((tamArquivo/HTTP)/LATENCIA))

            tempoRoteador = env.now - chegaRoteador

            TEMPO_ROTEADOR.append(tempoRoteador)

        with lan.request() as req:

            yield  req

            chegaLan = env.now

            yield env.timeout(float(tamArquivo/VEL_LAN))

            tempoLan = env.now - chegaLan

            TEMPO_LAN.append(tempoLan)


        with cpu.request() as req:

            yield req

            chegaCPU = env.now

            yield env.timeout(VEL_CPU_HIT)

            tempoCPU = env.now - chegaCPU

            TEMPO_CPU.append(tempoCPU)

    with disco.request() as req:

        yield req

        chegaDisco = env.now

        yield env.timeout(float(tamArquivo*VEL_DISCO))


        tempoDisco = env.now - chegaDisco


        TEMPO_DISCO.append(tempoDisco)

    with cpu.request() as req:

        yield req

        chegaCPU = env.now

        yield env.timeout(VEL_CPU_HIT)

        tempoCPU = env.now - chegaCPU

        TEMPO_CPU.append(tempoCPU)

    with lan.request() as req:

        yield  req

        chegaLan = env.now

        yield env.timeout(float(tamArquivo/VEL_LAN))

        tempoLan = env.now - chegaLan
        TEMPO_LAN.append(tempoLan)
    tempoTotal = env.now - tempoTotal
    TEMPO_TOTAL.append(tempoTotal )


def reqGenerator(env, lan, roteador, cpu, disco, linkSaida, linkEntrada, pensador):

    for i in itertools.count():

        with pensador.request() as req:

            yield req

            yield env.timeout(random.randint(*TAXA_CHEGADA))

            prob = random.randint(0,100)
            if prob <= 35:
                tamArquivo = 0.8
            elif prob <= 85:
                tamArquivo = 5.5
            elif prob <= 99:
                tamArquivo = 80
            else :
                tamArquivo =800

            env.process(requi(env, lan, roteador, cpu, disco, linkSaida, linkEntrada, tamArquivo))


def main():
    print('Servico web')
    random.seed(SEED)
    estatistica = Estatistica()


    env = simpy.Environment()
    lan = simpy.Resource(env, LAN)
    roteador = simpy.Resource(env, ROTEADOR)
    cpu = simpy.Resource(env, CPU)
    disco = simpy.Resource(env, DISCO)
    linkSaida = simpy.Resource(env, LINK_SAIDA)
    linkEntrada = simpy.Resource(env,LINK_ENTRADA)
    pensador = simpy.Resource(env, USUARIO_INTERNET_MAX)


    env.process(reqGenerator(env, lan, roteador, cpu, disco, linkSaida, linkEntrada, pensador))


    # Execute!
    env.run(until=SIM_TIME)




    print('LAN ',  estatistica.uti_link_p(TEMPO_LAN, SIM_TIME))
    print('CPU ',estatistica.uti_link_p(TEMPO_CPU, SIM_TIME))
    print('ENTRADA',estatistica.uti_link_p(TEMPO_ENTRADA, SIM_TIME))
    print('SAIDA ',estatistica.uti_link_p(TEMPO_SAIDA, SIM_TIME))
    print('DISCO ',estatistica.uti_link_p(TEMPO_DISCO, SIM_TIME))


    print()
    a = estatistica.tempo_medio_resp(TEMPO_TOTAL)
    print('TEMPO MEDIO DE RESPOSTA ', a)
    a = estatistica.taxa_process(TEMPO_TOTAL)
    print('TAXA PROCESSAMENTO ',a)
main()