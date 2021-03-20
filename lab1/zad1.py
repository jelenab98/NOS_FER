from multiprocessing import Process, Queue

import random
import queue
import time
import sys
import numpy as np

"""
Stari most je uski most i stoga postavlja ograničenja na promet. 
Na njemu istovremeno smije biti najviše 3 automobila koji voze u istom smjeru. 
Simulirati automobile procesom Auto  koji obavlja niže navedene radnje. Napisati program koji stvara N  automobila, 
gdje je N proizvoljan broj između 5 i 100 koji se određuje prilikom pokretanja programa te svakom automobilu dodjeljuje 
registarsku oznaku. Smjer se automobilu određuje nasumično.

Proces semafor određuje koji automobili će prijeći most, a početni smjer prijelaza se određuje nasumično te se zatim 
izmjenjuju. Prijelazak mosta se omogućuje kada se zabilježi 3 zahtjeva za prijelaz u trenutnom smjeru ili prođe X 
milisekundi, gdje je X slučajan broj između 500 i 1000. 
Prijelaz mosta traje Y milisekundi gdje je Y broj između 1000 i 3000.

Procesi međusobno komuniciraju uz pomoć reda poruka koristeći raspodijeljeni centralizirani protokol, 
gdje je proces Semafor odgovoran za međusobno isključivanje.

Proces Auto(registarska_oznaka, smjer) {
   // smjer = 0 ili 1
   // registarska oznaka je redni broj automobila u sustavu
   spavaj Z milisekundi; // Z je slučajan broj između 100 i 2000
   pošalji zahtjev za prijelaz mosta i ispiši("Automobil registarska_oznaka čeka na prelazak preko mosta");
   po primitku poruke "Prijeđi" ispiši("Automobil registarska_oznaka se popeo na most");
   po primitku poruke "Prešao" ispiši("Automobil registarska_oznaka je prešao most.");
}
"""


class Car:
    def __init__(self, reg_plate, times_to_cross):
        self.reg_plate = reg_plate
        self.direction = random.randint(0, 1)
        self.times_to_cross = times_to_cross
        self.process = None

    def make_process(self, q):
        self.process = Process(target=self.run, args=(q, ""))
        self.process.start()

    def run(self, q, a):
        for i in range(self.times_to_cross):
            # Spavaj neko vrijeme između 100 i 2000 milisekundi
            time.sleep(random.uniform(0.1, 2))

            # Zatraži prelazak preko mosta
            q.put(["Ja bih na most", self.reg_plate, self.direction])
            sys.stdout.write("Automobil {} čeka na prelazak preko mosta u smjeru {}.\n".format(self.reg_plate,
                                                                                               self.direction))
            sys.stdout.flush()

            # Čitaj poruke dok ne dobiš poruku Popni se i svoju registracijsku oznaku
            while True:
                message, reg_plate, direction = q.get()
                if message != "Popni se":
                    q.put([message, reg_plate, direction])
                else:
                    if reg_plate == self.reg_plate:
                        break
                    else:
                        q.put([message, reg_plate, direction])

            sys.stdout.write("Automobil {} se popeo na most.\n".format(self.reg_plate))
            sys.stdout.flush()

            # Čitaj poruke dok ne dobiš poruku Siđi i svoju registracijsku oznaku
            while True:
                message, reg_plate, direction = q.get()
                if message != "Sidi dole":
                    q.put([message, reg_plate, direction])
                else:
                    if reg_plate == self.reg_plate:
                        break
                    else:
                        q.put([message, reg_plate, direction])

            sys.stdout.write("Automobil {} je prešao most.\n".format(self.reg_plate))
            sys.stdout.flush()

            # Okreni se polukružno i započni opet proces prelaska preko mosta
            self.direction = (self.direction + 1) % 2
        """
        sys.stdout.write("Automobil {} je prešao most {} puta i krenuo doma.\n".format(self.reg_plate,
                                                                                     self.times_to_cross))
        sys.stdout.flush()
        """


class Bridge:
    def __init__(self, times_to_cross=2, n_process_min=5, n_process_max=100, n_max_cars=3):
        self.n_process = random.randint(n_process_min, n_process_max)
        self.times_to_cross = times_to_cross
        self.max_cars = n_max_cars
        self.q = Queue()
        self.my_direction = random.randint(0, 1)
        self.cars = []

    def run(self):
        for idx in range(self.n_process):
            self.cars.append(Car(idx, self.times_to_cross))

        for car in self.cars:
            car.make_process(self.q)

        active_cars = self.n_process

        dir_0_counter = 0
        dir_1_counter = 0

        ids_0 = queue.Queue()
        ids_1 = queue.Queue()

        while active_cars > 0:
            print("Aktivnih auti ima {}, a moj smjer je {}".format(active_cars, self.my_direction))

            start_time = time.perf_counter()
            print("Velicine | q={}, c0={}, {}, c1={}, {}".format(self.q.qsize(), dir_0_counter, ids_0.qsize(),
                                                                 dir_1_counter, ids_1.qsize()))
            while True:
                if (abs(time.perf_counter() - start_time) >= 2 and self.q.qsize() == 0) or \
                        (dir_1_counter >= 3 and self.my_direction == 1) or \
                        (dir_0_counter >= 3 and self.my_direction == 0):
                    print("Izlazim van uz")
                    print("Velicine | q={}, c0={}, {}, c1={}, {}".format(self.q.qsize(), dir_0_counter, ids_0.qsize(),
                                                                         dir_1_counter, ids_1.qsize()))
                    break
                message, reg_plate, direction = self.q.get()
                if message == "Ja bih na most" and direction == 0:
                    dir_0_counter += 1
                    ids_0.put(reg_plate)
                elif message == "Ja bih na most" and direction == 1:
                    dir_1_counter += 1
                    ids_1.put(reg_plate)
                else:
                    self.q.put([message, reg_plate, direction])

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

            for id_i in ids:
                self.q.put(["Popni se", id_i, self.my_direction])
                time.sleep(0.05)

            time.sleep(3)

            for id_i in ids:
                self.q.put(["Sidi dole", id_i, self.my_direction])
                time.sleep(0.05)

            time.sleep(1)

            self.my_direction = (self.my_direction + 1) % 2

            active_cars = np.count_nonzero(np.array([car.process.exitcode is None for car in self.cars]))


if __name__ == '__main__':
    bridge = Bridge(1, 5, 10, 3)
    bridge.run()
