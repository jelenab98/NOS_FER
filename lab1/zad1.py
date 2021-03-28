from multiprocessing import Process, Queue

import random
import queue
import time
import sys


ZELIM_NA_MOST = 0
ODI_NA_MOST = 1
SIDI_S_MOSTA = 2


class Car:
    def __init__(self, reg_plate, times_to_cross):
        self.reg_plate = reg_plate
        self.direction = random.randint(0, 1)
        self.times_to_cross = times_to_cross
        self.process = None

    def make_process(self, q1, q2):
        self.process = Process(target=self.run, args=(q1, q2))
        self.process.start()

    def run(self, q1, q2):
        for i in range(self.times_to_cross):
            # Spavaj neko vrijeme između 100 i 2000 milisekundi
            time.sleep(random.uniform(0.1, 2))

            # Zatraži prelazak preko mosta
            q1.put([ZELIM_NA_MOST, self.reg_plate, self.direction])
            sys.stdout.write("Automobil {} čeka na prelazak preko mosta u smjeru {}.\n".format(self.reg_plate,
                                                                                               self.direction))
            sys.stdout.flush()

            # Čitaj poruke dok ne dobiš poruku Popni se i svoju registracijsku oznaku
            while True:
                message, reg_plate, direction = q2.get()
                if message != ODI_NA_MOST:
                    q2.put([message, reg_plate, direction])
                else:
                    if reg_plate == self.reg_plate:
                        break
                    else:
                        q2.put([message, reg_plate, direction])

            sys.stdout.write("Automobil {} se popeo na most.\n".format(self.reg_plate))
            sys.stdout.flush()

            # Čitaj poruke dok ne dobiš poruku Siđi i svoju registracijsku oznaku
            while True:
                message, reg_plate, direction = q2.get()
                if message != SIDI_S_MOSTA:
                    q2.put([message, reg_plate, direction])
                else:
                    if reg_plate == self.reg_plate:
                        break
                    else:
                        q2.put([message, reg_plate, direction])

            sys.stdout.write("Automobil {} je prešao most.\n".format(self.reg_plate))
            sys.stdout.flush()

            # Okreni se polukružno i započni opet proces prelaska preko mosta
            self.direction = (self.direction + 1) % 2


class Bridge:
    def __init__(self, times_to_cross=2, n_process_min=5, n_process_max=100, n_max_cars=3):
        self.n_process = random.randint(n_process_min, n_process_max)
        self.times_to_cross = times_to_cross
        self.max_cars = n_max_cars
        self.q1 = Queue()
        self.q2 = Queue()
        self.my_direction = random.randint(0, 1)
        self.cars = []

    def run(self):
        # Stvori aute i pokreni njihove procese
        for idx in range(self.n_process):
            self.cars.append(Car(idx, self.times_to_cross))

        for car in self.cars:
            car.make_process(self.q1, self.q2)

        active_cars = self.n_process

        dir_0_counter = 0
        dir_1_counter = 0

        ids_0 = queue.Queue()
        ids_1 = queue.Queue()
        print("Stvoreno {} auta".format(self.n_process))

        # Ponavljaj izmjenu semafora dok svi auti ne produ preko mosta
        while active_cars > 0:
            start_time = time.perf_counter()
            print("Smjer semafora na mostu je ", self.my_direction)

            # Čitaj zahtjeve za prelaz preko mosta dok ne istekne vrijeme ili su skupljena 3 zahtjeva
            while True:
                if (dir_1_counter >= 3 and self.my_direction == 1) or (dir_0_counter >= 3 and self.my_direction == 0) \
                        or time.perf_counter() - start_time >= random.uniform(0.5, 1):
                    break
                if self.q1.empty():
                    continue
                message, reg_plate, direction = self.q1.get_nowait()
                if message == ZELIM_NA_MOST and direction == 0:
                    dir_0_counter += 1
                    ids_0.put(reg_plate)
                elif message == ZELIM_NA_MOST and direction == 1:
                    dir_1_counter += 1
                    ids_1.put(reg_plate)
                else:
                    self.q1.put([message, reg_plate, direction])

            # Odredi kojim autima je potrebno dojaviti da idu na most
            if self.my_direction == 0:
                cars_to_take = min(3, dir_0_counter)
                dir_0_counter -= cars_to_take
                ids = []
                for i in range(cars_to_take):
                    ids.append(ids_0.get())
            else:
                cars_to_take = min(3, dir_1_counter)
                dir_1_counter -= cars_to_take
                ids = []
                for i in range(cars_to_take):
                    ids.append(ids_1.get())

            # Posalji signal da se popnu na most
            for id_i in ids:
                self.q2.put([ODI_NA_MOST, id_i, self.my_direction])
                time.sleep(0.05)  # kratko spavanje jer su auti jedan iza drugoga pa ne mogu istodobno svi na most

            # Auti su na mostu 1-3 sekunde
            time.sleep(random.uniform(1, 3))

            # Javi autima da moraju sici s mosta
            for id_i in ids:
                self.q2.put([SIDI_S_MOSTA, id_i, self.my_direction])
                time.sleep(0.05)  # kratko spavanje jer silaze s mosta jedan za drugim

            # Dodatno spavanje samo radi preglednijeg ispisa
            time.sleep(1)

            # Promijeni smjer semafora na mostu
            self.my_direction = (self.my_direction + 1) % 2

            # Provjeri koliko ih je još aktivnih
            active_cars = 0
            for car in self.cars:
                if car.process.exitcode is None:
                    active_cars += 1


if __name__ == '__main__':
    n = int(input("Odaberite max broj auta za se stvoriti >> "))
    times = int(input("Koliko puta svaki auto prelazi preko mosta >> "))
    bridge = Bridge(times, 5, n, 3)
    bridge.run()
