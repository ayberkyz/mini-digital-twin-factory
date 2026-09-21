import asyncio
import random

class Machine :
    def __init__ (self, machine_id , name , cycle_time) :
        self.machine_id = machine_id
        self.name = name
        self.cycle_time = cycle_time 
        self.total_produced = 0
        self.good_produced = 0
        self.scrap_produced = 0
        self.status = "IDLE"


    async  def start_production(self):
        self.status = "RUNNING"
        print(f"[{self.name}] Makine Üretime Başladı...")

        while True:
            if random.random() < 0.05:
                self.status = "BREAKDOWN"
                tamir_suresi = random.uniform(5.0, 8.0) # 5 ile 8 saniye arası tamir sürsün
                print(f"🚨 [{self.name}] ARIZA YAPTI! Bakım bekleniyor... (Tahmini duruş: {tamir_suresi:.1f}s)")
                await asyncio.sleep(tamir_suresi)
                self.status = "RUNNING"
                print(f"✅ [{self.name}] Tamir tamamlandı, üretime geri dönüldü.")

            await asyncio.sleep(self.cycle_time) 
            
            actual_time = random.uniform(self.cycle_time - 0.5, self.cycle_time + 0.5)
            await asyncio.sleep(actual_time)    

            if random.random() < 0.10:
                self.scrap_produced += 1
                kalite_durumu = "HATALI (HURDA)"
            else:
                self.good_produced += 1
                kalite_durumu = "SAĞLAM"

            self.total_produced += 1

            print(f"[{self.name}] Parça bitti -> Durum: {kalite_durumu} | Toplam: {self.total_produced} (Sağlam: {self.good_produced}, Hurda: {self.scrap_produced})")



async def main():
    bukum_makinesi = Machine(101, "Büküm İstasyonu", 3)
    kırma_makinesi = Machine(102, "Kırma Makinesi", 5)
    await asyncio.gather(
        bukum_makinesi.start_production(),
        kırma_makinesi.start_production()
    )


asyncio.run(main())