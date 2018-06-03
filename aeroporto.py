import itertools
import random
from Aeroporto.statistica import Estatisticas
import numpy as np
import simpy

RANDOM_SEED = 42
GAS_STATION_SIZE = 1600  # liters
THRESHOLD = 10  # Threshold for calling the tank truck (in %)
FUEL_TANK_SIZE = 16000  # liters
FUEL_TANK_LEVEL = [1445, 9752]  # Min/max levels of fuel tanks (in liters)
REFUELING_SPEED = 2  # liters / second
TANK_TRUCK_TIME = 300  # Seconds it takes the tank truck to arrive
T_INTER = [1800, 7200]  # Create a airplane every [min, max] seconds
SIM_TIME = 100000  # Simulation time in seconds
PROB_ABASTECE = 10
TEMPO_PISTA = [1200, 1800]
TEMPO_DECOLAGEM = [120, 180]
PASSAGEIROS = [85, 215]
TEMPO_EMB_DES = [45, 90]
num_avioes = 0
num_avioes_finger = 0
numAv_atendidos = 0 # ou seja, pousa e decola. A simulação pode acabar antes q todos os aviões decolem
tempo_solo= list()
tempo_finger = list()
tempoChegada = 0
tempoDecolagem = 0
tempo_pista = list()
tempo_termino = 0 # tempo de execução até ultimo que decolou

def airplane(name, env, pista, finger, passageiros, fuel_tank_level, gas_station, fuel_pump):
    """A airplane arrives at the gas station for refueling.

    It requests one of the gas station's fuel pumps and tries to get the
    desired amount of gas from it. If the stations reservoir is
    depleted, the airplane has to wait for the tank truck to arrive.

    """
    global num_avioes
    global tempo_termino
    global numAv_atendidos
    global num_avioes_finger


    print('%s chegou no aeroporto as %1.f'
          % (name, env.now))

    """Solicita pista de pouso"""
    with pista.request() as req:
        start = env.now

        yield req
        tempoChegada = env.now

        print('%s esperou %.1f segundos para usar a pista'
               %(name, env.now))
        num_avioes +=1

        taxiando = random.randint(*TEMPO_PISTA)
        tempo_pista.append(taxiando)
        yield env.timeout(taxiando)

    flag = False
    with (finger.request()) as req:

        start = env.now

        yield req
        ini_finger = env.now
        num_avioes_finger +=1
        print('%s esperou %1.f segundos para usar um dos fingers' % (name, env.now ))

        tempo_emb_des = 0
        for i in range(passageiros):
            tempo_emb_des += random.randint(*TEMPO_EMB_DES)

        passageiros = random.randint(*PASSAGEIROS)

        for i in range(passageiros):
            tempo_emb_des += random.randint(*TEMPO_EMB_DES)

        yield env.timeout(tempo_emb_des)
        termino_finger = env.now
        tempo_finger.append(termino_finger - ini_finger)
        print('Tempo de embarque/desembarque do aviao {} terminou em {}!'.format(name,env.now));
        i = np.random.random() * PROB_ABASTECE
        flag = True

    if flag == True and i > 5:

        with gas_station.request() as req:
            start = env.now
            # Request one of the gas pumps
            print('%s foi abastecer  as %1.f'
                  % (name, env.now))
            yield req  # Get the required amount of fuel
            liters_required = FUEL_TANK_SIZE - fuel_tank_level

            yield env.timeout(liters_required)
            print('%s terminou de abastecer as %.1f seconds.' % (name, env.now ))
            with pista.request() as req:
                start = env.now
                print('%s foi para pista de decolagem  as %1.f'
                      % (name, env.now))
                yield req

                taxiando = random.randint(*TEMPO_PISTA)
                tempo_pista.append(taxiando)
                yield env.timeout(taxiando)
                tempoDecolagem = env.now
                tempSolo = tempoDecolagem - tempoChegada
                tempo_solo.append(tempSolo)
                numAv_atendidos +=1
                tempo_termino = tempoDecolagem
                print('%s DECOLOU as %.1f seconds e ficou %d no solo' % (name, env.now,tempSolo))

    else:
        with pista.request() as req:
            start = env.now
            print('%s foi para pista de decolagem  as %1.f'
                  % (name, env.now))
            yield req

            taxiando = random.randint(*TEMPO_PISTA)
            tempo_pista.append(taxiando)
            yield env.timeout(taxiando)
            tempoDecolagem = env.now
            tempSolo = tempoDecolagem - tempoChegada
            tempo_solo.append(tempSolo)
            numAv_atendidos +=1
            tempo_termino = tempoDecolagem
            print('%s DECOLOU as %.1f seconds e ficou %d no solo' % (name, env.now,tempSolo))

def gas_station_control(env, fuel_pump):
    """Periodically check the level of the *fuel_pump* and call the tank
    truck if the level falls below a threshold."""
    while True:
        if fuel_pump.level / fuel_pump.capacity * 100 < THRESHOLD:
            # We need to call the tank truck now!
            print('Calling tank truck at %d' % env.now)
            # Wait for the tank truck to arrive and refuel the station
            yield env.process(tank_truck(env, fuel_pump))

        yield env.timeout(10)  # Check every 10 seconds


def tank_truck(env, fuel_pump):
    """Arrives at the gas station after a certain delay and refuels it."""
    yield env.timeout(TANK_TRUCK_TIME)
    print('Tank truck arriving at time %d' % env.now)
    ammount = fuel_pump.capacity - fuel_pump.level
    print('Tank truck refuelling %.1f liters.' % ammount)
    yield fuel_pump.put(ammount)


def airplane_generator(env, pista, finger, gas_station, fuel_pump):
    """Generate new airplanes that arrive at the gas station."""
    for i in itertools.count():
        yield env.timeout(random.randint(*T_INTER))
        passageiros = random.randint(*PASSAGEIROS)
        fuel_tank_level = random.randint(*FUEL_TANK_LEVEL)
        env.process(airplane('Aviao %d' % i, env, pista, finger, passageiros, fuel_tank_level, gas_station, fuel_pump))


# Setup and start the simulation
print('Aeroporto')

#ainda n tem nada de util na classe estatistica


random.seed(RANDOM_SEED)

# Create environment and start processes
env = simpy.Environment()
gas_station = simpy.Resource(env, 1)
pista = simpy.Resource(env, 1)
finger = simpy.Resource(env, 2)
gas_station = simpy.Resource(env, 1)
fuel_pump = simpy.Container(env, GAS_STATION_SIZE, init=GAS_STATION_SIZE)
env.process(gas_station_control(env, fuel_pump))
env.process(airplane_generator(env, pista, finger, gas_station, fuel_pump))

# Execute!
env.run(until=SIM_TIME)

est = Estatisticas.Estatistica(num_avioes, tempo_solo, tempo_termino , numAv_atendidos , tempo_finger, num_avioes_finger)
print(est.temp_med_solo())
numAtendidos = est.num_av_atendidos()
print(numAtendidos)
print(est.uti_finger())
print(est.uti_pista(tempo_pista))