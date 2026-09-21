import asyncio
import random
import time

class Machine:
    def __init__(self, machine_id, name, cycle_time, input_queue=None, output_queue=None, batch_size=1, variance=1.0):
        self.machine_id = machine_id
        self.name = name
        self.cycle_time = cycle_time 
        self.input_queue = input_queue    
        self.output_queue = output_queue  
        self.batch_size = batch_size      
        self.variance = variance          
        
        self.total_produced = 0
        self.good_produced = 0
        self.scrap_produced = 0
        
        self.total_busy_time = 0.0   
        self.total_idle_time = 0.0   
        self.total_breakdown_time = 0.0 
        
        self.status = "IDLE"

    async def start_production(self):
        print(f"[{self.name}] Makine/Istasyon Acildi, Hazir.")

        while True:
            gelen_malzeme = "Sonsuz Hammadde"
            
            # 1. Giris bandi kontrolu ve bekleme suresi olcumu
            if self.input_queue is not None:
                self.status = "WAITING_INPUT"
                bekleme_baslangic = time.time()
                
                gelen_malzeme = await self.input_queue.get()
                self.total_idle_time += (time.time() - bekleme_baslangic)

            self.status = "RUNNING"

            # 2. Parti (Batch) isleme dongusu
            for dilim_no in range(1, self.batch_size + 1):
                # Ariza kontrolu (%2 ihtimal)
                if random.random() < 0.02:
                    self.status = "BREAKDOWN"
                    tamir_suresi = random.uniform(5.0, 10.0) 
                    print(f"[{self.name}] ARIZA/DURUS! Durus suresi: {tamir_suresi:.1f}s")
                    await asyncio.sleep(tamir_suresi)
                    self.total_breakdown_time += tamir_suresi
                    self.status = "RUNNING"
                    print(f"[{self.name}] Durus sona erdi, calismaya devam ediliyor.")

                # Fiili isleme suresi ve sayac artirimi
                actual_time = max(0.5, random.uniform(self.cycle_time - self.variance, self.cycle_time + self.variance))
                await asyncio.sleep(actual_time)    
                self.total_busy_time += actual_time

                # Kalite kontrolu (%5 hata ihtimali)
                if random.random() < 0.05:
                    self.scrap_produced += 1
                    kalite_durumu = "HATALI (HURDA)"
                else:
                    self.good_produced += 1
                    kalite_durumu = "SAGLAM"

                self.total_produced += 1

                print(f"[{self.name}] Islem bitti ({actual_time:.2f}s) -> Durum: {kalite_durumu} | Toplam: {self.total_produced}")

                # Cikis bandina aktarma
                if kalite_durumu == "SAGLAM" and self.output_queue is not None:
                    urun_adi = f"{self.name} Parca #{self.good_produced}"
                    await self.output_queue.put(urun_adi)
                elif kalite_durumu == "HATALI (HURDA)":
                    print(f"[{self.name}] Hatali urun kirmaya/ayirmaya gonderildi.")


async def factory_dashboard(machines, queues, interval=5):
    start_time = time.time()
    await asyncio.sleep(2)

    while True:
        await asyncio.sleep(interval)
        elapsed_time = time.time() - start_time

        print("\n" + "=" * 70)
        print(f"FABRIKA CANLI DURUM RAPORU (Calisma Suresi: {elapsed_time:.1f}s)")
        print("=" * 70)

        # 1. WIP / Bant Stok Durumu
        print("--- ARA STOK / BANTLAR (WIP) ---")
        for q_name, q in queues.items():
            print(f"  Bant: {q_name:<18} | Stok: {q.qsize()} adet")

        # 2. Makine Performansi ve Darbogaz Tespiti
        print("\n--- MAKINE KULLANIMLARI & CIKTILAR ---")
        highest_utilization = -1.0
        bottleneck_machine = None

        for m in machines:
            utilization = (m.total_busy_time / elapsed_time) * 100 if elapsed_time > 0 else 0
            if utilization > highest_utilization:
                highest_utilization = utilization
                bottleneck_machine = m.name

            print(
                f"  {m.name:<18} | Durum: {m.status:<14} "
                f"| Kullanim: %{utilization:5.1f} "
                f"| Saglam: {m.good_produced:<3} | Hurda: {m.scrap_produced:<2}"
            )

        print("-" * 70)
        if bottleneck_machine:
            print(f"DARBOGAZ (BOTTLENECK): {bottleneck_machine} (%{highest_utilization:.1f} Doluluk)")
        print("=" * 70 + "\n")


async def main():
    bobin_bandi = asyncio.Queue()
    paketleme_bandi = asyncio.Queue()

    levha_makinesi = Machine(
        machine_id=1, 
        name="Levha Makinesi", 
        cycle_time=30, 
        input_queue=None, 
        output_queue=bobin_bandi, 
        batch_size=1, 
        variance=2.0
    )
    dilme_a = Machine(
        machine_id=2, 
        name="Dilme A", 
        cycle_time=15, 
        input_queue=bobin_bandi, 
        output_queue=paketleme_bandi, 
        batch_size=5, 
        variance=1.5
    )
    dilme_b = Machine(
        machine_id=3, 
        name="Dilme B", 
        cycle_time=15, 
        input_queue=bobin_bandi, 
        output_queue=paketleme_bandi, 
        batch_size=5, 
        variance=1.5
    )
    paket_1 = Machine(
        machine_id=4, 
        name="Paketleme 1", 
        cycle_time=4, 
        input_queue=paketleme_bandi, 
        output_queue=None, 
        batch_size=1, 
        variance=2.0
    )
    paket_2 = Machine(
        machine_id=5, 
        name="Paketleme 2", 
        cycle_time=4, 
        input_queue=paketleme_bandi, 
        output_queue=None, 
        batch_size=1, 
        variance=2.0
    )
    paket_3 = Machine(
        machine_id=6, 
        name="Paketleme 3", 
        cycle_time=4, 
        input_queue=paketleme_bandi, 
        output_queue=None, 
        batch_size=1, 
        variance=2.0
    )

    machines_list = [levha_makinesi, dilme_a, dilme_b, paket_1, paket_2, paket_3]
    queues_dict = {"Bobin Bandi": bobin_bandi, "Paketleme Bandi": paketleme_bandi}

    await asyncio.gather(
        levha_makinesi.start_production(),
        dilme_a.start_production(),
        dilme_b.start_production(),
        paket_1.start_production(),
        paket_2.start_production(),
        paket_3.start_production(),
        factory_dashboard(machines_list, queues_dict, interval=5)
    )

asyncio.run(main())