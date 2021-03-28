import multiprocessing as mp
import numpy as np
import time
import sys


def run(id_process, clock, PIPES, database):
    pipe = PIPES[id_process][1]
    n_process = len(PIPES)
    waiting_processes = mp.Queue()

    # Svaki proces želi 5 puta ući u KO pa imamo vanjsku petlju
    for i in range(1, 6):
        # Spavaj neko vrijeme od 100 do 2000 milisekundi
        time.sleep(np.random.uniform(0.1, 2))

        # Pošalji zathjev za ulazak u KO svim procesima osim sebi i zabiljezi koja je vrijednost sata
        message = f"0 {id_process} {clock}"
        previous_clock = clock
        for idx, (p1, p2) in PIPES.items():
            if idx == id_process:
                continue
            sys.stdout.write(f"Proces {id_process} šalje poruku {message} procesu {idx}\n")
            sys.stdout.flush()
            p1.send(message)

        counter_of_replies = 0

        # Ponavljaj citanje poruka dok ih ne skupis dosta za uci u KO
        while True:
            time.sleep(0.05)
            # Procitaj i obradi poruku
            message = pipe.recv()
            operation_id, other_process_id, other_clock = message.split(" ")
            # Svaki put kad primis poruku uskladi svoj lokalni sat
            clock = max(clock, int(other_clock)) + 1
            sys.stdout.write(f"Proces {id_process} primio poruku {message} od procesa {other_process_id} "
                             f"i ustimao svoj sat na {clock}\n")
            sys.stdout.flush()
            # Ako si primio odgovor da mozes uci, povecaj brojac da znas koliko ih jos moras primiti
            if int(operation_id) == 1:
                counter_of_replies += 1
            # ako si primio novi zahtjev za KO pogledaj odnos lokalnih satova
            if int(operation_id) == 0:
                # ako je njegov sat manji od tvog, on ima prednost pa pusti njega prije
                if int(other_clock) < previous_clock:
                    message = f"1 {id_process} {other_clock}"
                    sys.stdout.write(f"Proces {id_process} šalje poruku {message} procesu {other_process_id}\n")
                    sys.stdout.flush()
                    pipe_out = PIPES[int(other_process_id)][0]
                    pipe_out.send(message)
                # Ako su satovi izjednaceni, pogledaj tko ima manji indeks i on ima prednost
                elif int(other_clock) == previous_clock:
                    if int(other_process_id) < id_process:
                        message = f"1 {id_process} {other_clock}"
                        sys.stdout.write(f"Proces {id_process} šalje poruku {message} procesu {other_process_id}\n")
                        sys.stdout.flush()
                        pipe_out = PIPES[int(other_process_id)][0]
                        pipe_out.send(message)
                    else:
                        waiting_processes.put((operation_id, other_process_id, other_clock))
                # Ako ti imas prednost, zabljezi da taj proces ceka tvoj odgovor koji ces mu kasnije poslati
                else:
                    waiting_processes.put((operation_id, other_process_id, other_clock))
            # ako si dobio sve odgovore, izadi van i udi u KO
            if counter_of_replies == n_process - 1:
                break

        # Ulazak u KO
        sys.stdout.write(f"Proces {id_process} ulazi u KO\n")
        sys.stdout.flush()

        # Azuriranje baze podataka i ispis kao kontrola
        id_x, clock_in_base, entries_in_base = database[id_process*3:id_process*3+3]
        database[id_process*3+1] = clock
        database[id_process*3+2] += 1
        sys.stdout.write(f"Ažuriram bazu podataka s ({id_process},{clock_in_base},{entries_in_base}) "
              f"na ({id_process},{clock},{i})\n")
        sys.stdout.flush()
        sys.stdout.write("Baza sada izgleda kao:\n")
        sys.stdout.flush()
        for j in range(0, len(database), 3):
            sys.stdout.write(f"{database[j]} | {database[j+1]} | {database[j+2]}\n")
            sys.stdout.flush()
        sys.stdout.write(f"Proces {id_process} izlazi iz KO\n")
        sys.stdout.flush()

        # Izlazak iz KO i javljanje procesima koji cekaju da sam izasao pa da oni mogu uci
        while not waiting_processes.empty():
            operation_id, other_process_id, other_clock = waiting_processes.get()
            message = f"1 {id_process} {other_clock}"
            sys.stdout.write(f"Proces {id_process} šalje poruku {message} procesu {other_process_id}\n")
            sys.stdout.flush()
            pipe_out = PIPES[int(other_process_id)][0]
            pipe_out.send(message)


if __name__ == '__main__':
    n = int(input("Upišite broj procesa >> "))
    PIPES = {}
    processes = []
    clocks = []
    start_database = []

    # Stvaranje cjevovoda i lokalnog sata za svaki proces
    for idx in range(n):
        PIPES[idx] = mp.Pipe()
        clock_i = int(np.random.uniform(0, 1e3))
        start_database.append(idx)
        start_database.append(clock_i)
        start_database.append(0)
        clocks.append(clock_i)

    # Inicijalni ispis baze podataka kao provjera
    sys.stdout.write("Početna baza podataka >> \n")
    sys.stdout.flush()
    for i in range(0, len(start_database), 3):
        sys.stdout.write(f"{start_database[i]} | {start_database[i+1]} | {start_database[i+2]}\n")
        sys.stdout.flush()

    database = mp.Array("i", start_database)

    # Stvaranje procesa i pokretanje
    for idx in range(n):
        processes.append(mp.Process(target=run, args=(idx, clocks[idx], PIPES, database)))
        processes[-1].start()

    for process in processes:
        process.join()
