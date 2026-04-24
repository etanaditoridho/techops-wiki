---
title: "🔗 Synthesis: Monitoring Harian Sistem Engineering"
status: verified
folder: ENGINEERING
owner: ""
version: 2
review_date: 
confidence: 
tags:
  - Electrical System
  - Hvac System
  - Hvac Failure Diagnosis
  - Synthesis Emergency Shutdown
  - Boiler Leak Response
  - Operasi Perawatan Udara Tekan
  - Operasi Perawatan Bms Ems
  - Operasi Perawatan Hvac
  - SOP EN-016
  - SOP EN-013
notion_id: 34c664a8-3e24-818c-9982-db8e72d0f2ec
synced: 2026-04-24
---

**Summary**: Sintesis tugas pemantauan harian yang harus dilakukan teknisi Engineering PT EBI — mencakup semua sistem utama: HVAC, udara tekan, EMS/BMS, kelistrikan, dan mesin produksi.
**Sources**: `SOP-EBI-EN-016.07`, `SOP-EBI-EN-013 Rev.04`, `SOP-EBI-EN-055.00`, `SOP-EBI-EN-001.02`, `SOP-EBI-EN-004.02`
**Last updated**: 2026-04-22
## Prinsip Monitoring Harian
- **Dokumentasikan semua**: setiap pembacaan parameter dicatat di formulir yang relevan
- **Deviasi = eskalasi segera**: jangan tunggu akhir shift untuk lapor ke Supervisor
- **Alat ukur rusak**: beri penandaan jelas, lapor ke Supervisor untuk kalibrasi/penggantian
- **Gunakan APD**: safety shoes dan helm di area mesin
## Checklist Harian per Sistem
### 1. Sistem HVAC
| Waktu | Tugas |
|---|---|
| Setiap shift | Baca dan log parameter BMS/EMS: suhu, RH, tekanan diferensial, alarm aktif |
| Harian | Pengecekan visual kondisi AHU, FCU, exhaust fan (vibrasi, bocor, suara abnormal) |
| Harian | Periksa status chiller: suhu inlet/outlet air dingin, tekanan refrigerant, alarm |
| Harian | Cek kondensasi di area sekitar cooling coil |
| Harian | Periksa status hot water generator jika aktif |
**Parameter kritis yang harus normal**:
- Suhu ruangan produksi: sesuai set point area
- RH: dalam rentang yang ditentukan per area
- Tekanan diferensial: hirarki positif/negatif terjaga
- Tidak ada alarm aktif di panel BMS
### 2. Sistem Udara Tekan
| Waktu | Tugas |
|---|---|
| Setiap shift | Log tekanan sistem di outlet kompressor dan titik distribusi utama |
| Harian | Verifikasi rotasi kompressor dan dryer sesuai jadwal (bergantian 1 hari) |
| Harian | Cek temperatur outlet kompressor yang aktif |
| Harian | Drain kondensat dari separator/receiver tank |
| Harian | Visual check: kebocoran udara (dengarkan suara desis) |
**Parameter kritis yang harus normal**:
- Tekanan sistem: dalam rentang operasi yang ditetapkan
- Temperatur kompressor: di bawah batas alarm
- Tidak ada kebocoran udara terdeteksi
- Dryer berfungsi normal (dew point terjaga)
### 3. Sistem EMS & BMS
| Waktu | Tugas |
|---|---|
| Setiap shift | Review dashboard BMS: status semua sistem yang terhubung |
| Setiap shift | Review alert EMS: ada alarm suhu/kelembaban area kritis? |
| Harian | Verifikasi sensor EMS berfungsi (tidak ada sensor error/offline) |
| Harian | Cek cold storage monitoring: suhu dalam rentang normal |
| Harian | Log semua pembacaan ke formulir F01 SOP/EBI/ENG-055 |
**Area kritis yang dipantau EMS**:
- Ruangan produksi steril
- Cold storage produk jadi
- Laboratorium QA/QC
- Area penyimpanan bahan baku sensitif
### 4. Sistem Kelistrikan
| Waktu | Tugas |
|---|---|
| Harian | Pengecekan visual panel MDP/SDP: indikator normal, tidak ada alarm |
| Harian | Cek lampu penerangan area produksi dan koridor — laporkan yang mati |
| Harian | Verifikasi status genset/UPS (ready/charged) |
| Harian | Amati tanda-tanda bahaya: bau terbakar, panas berlebih, bunyi abnormal dari panel |
**Tanda bahaya yang harus segera dilaporkan**:
- Bau ozon/terbakar dari panel
- Lampu indikator fault/alarm menyala
- Suhu panel terasa panas berlebihan
- Bunyi buzzing/humming tidak normal
### 5. Mesin Produksi (PM Harian)
| Waktu | Tugas |
|---|---|
| Sebelum produksi | Verifikasi mesin dalam kondisi siap operasi |
| Setiap shift | Terima dan proses Laporan Breakdown (F01B) jika ada |
| Setiap shift | Cek mesin yang sedang dalam PM/perbaikan — update status |
| Harian | Update Kartu Riwayat Mesin (F02B) untuk pekerjaan yang selesai |
## Alur Jika Ditemukan Deviasi
## Formulir yang Digunakan
| Formulir | Sistem | Frekuensi |
|---|---|---|
| Log parameter BMS/EMS (F01 EN-055) | EMS/BMS | Per shift |
| Log kompressor & dryer | Udara Tekan | Per shift/harian |
| Log parameter HVAC | HVAC | Per shift/harian |
| Laporan Breakdown F01B | Mesin | Saat ada breakdown |
| Kartu Riwayat Mesin F02B | Mesin | Saat ada pekerjaan |
## Eskalasi Cepat
| Situasi | Eskalasi |
|---|---|
| Alarm EMS area steril tidak bisa di-reset | Supervisor + QA segera |
| Tekanan udara tekan drop drastis | Supervisor segera |
| Panel listrik alarm/bau terbakar | Supervisor + HSSE segera |
| Chiller trip saat produksi | Supervisor + Produksi segera |
## Related pages
- [[hvac-system]]
- [[compressed-air-system]]
- [[electrical-system]]
- [[operasi-perawatan-bms-ems]]
- [[operasi-perawatan-udara-tekan]]
- [[operasi-perawatan-hvac]]
- [[hvac-failure-diagnosis]]
- [[boiler-leak-response]]
- [[maintenance-types]]
- [[engineering-responsibilities]]
- [[synthesis-emergency-shutdown]]