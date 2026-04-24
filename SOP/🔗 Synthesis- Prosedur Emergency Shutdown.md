---
title: "🔗 Synthesis: Prosedur Emergency Shutdown"
status: verified
folder: ENGINEERING
owner: ""
version: 1
review_date: 
confidence: 
tags:
  - Electrical System
  - Penanganan Lampu Distribusi Listrik
  - Operasi Perawatan Bms Ems
  - Hvac System
  - Maintenance Types
  - Operasi Perawatan Hvac
  - Penanganan Perbaikan Mesin
  - Compressed Air System
  - SOP EN-016
  - SOP EN-013
notion_id: 34c664a8-3e24-8163-80c7-d720244a9507
synced: 2026-04-24
---

**Summary**: Sintesis prosedur penghentian darurat dan penanganan kegagalan sistem lintas semua SOP Engineering — HVAC, udara tekan, kelistrikan, dan mesin produksi.
**Sources**: `SOP-EBI-EN-016.07`, `SOP-EBI-EN-013 Rev.04`, `SOP-EBI-EN-001.02`, `SOP-EBI-EN-014.01`, `SOP-EBI-EN-055.00`
**Last updated**: 2026-04-22
## Mengapa Ini Penting
Kegagalan sistem di fasilitas produksi farmasi steril dapat:
- Mencemari batch produksi
- Membahayakan keselamatan personel
- Menyebabkan kerusakan peralatan permanen
- Memicu investigasi regulatory dan potensi recall
Semua teknisi harus mengetahui urutan shutdown yang benar dan cara eskalasi yang tepat.
## Prinsip Umum Emergency Shutdown
1. **Utamakan keselamatan personel** — evakuasi area jika bahaya langsung
1. **Ikuti urutan shutdown yang benar** — penghentian sembarangan dapat merusak mesin atau memperparah kondisi
1. **Beri tanda/label** — mesin yang dimatikan darurat harus diberi label status
1. **Laporkan segera** — eskalasi ke Supervisor dalam hitungan menit, bukan jam
1. **Jangan restart tanpa otorisasi** — Supervisor atau Manager harus menyetujui restart setelah investigasi
## Sistem HVAC
### Kondisi Darurat yang Memerlukan Shutdown
- Kebakaran di ruang mesin HVAC
- Kebocoran refrigerant (freon) dari chiller
- Kegagalan total blower/fan AHU di area kritis
- Alarm suhu atau tekanan chiller di luar batas operasi
- Banjir atau intrusi air ke panel kontrol
### Urutan Shutdown HVAC
1. Matikan AHU/FCU area terdampak terlebih dahulu
1. Matikan chiller setelah beban (AHU/FCU) dimatikan
1. Matikan pompa sirkulasi setelah chiller berhenti
1. Matikan cooling tower terakhir
1. Pastikan semua isolasi valve terkunci jika diperlukan
1. Beri label "JANGAN DIOPERASIKAN" di panel kontrol
1. Lapor ke Supervisor segera
**Catatan**: Sistem HVAC area produksi steril yang dimatikan mendadak harus segera diinformasikan ke QA — batch yang sedang diproduksi mungkin terpengaruh.
## Sistem Udara Tekan
### Kondisi Darurat yang Memerlukan Shutdown
- Kebocoran udara tekan besar (suara desis/tekanan turun drastis)
- Temperatur kompressor over-limit (alarm temperatur)
- Kebakaran di ruang kompressor
- Kegagalan total dryer saat produksi sedang berjalan
### Urutan Shutdown Udara Tekan
1. Aktifkan kompressor cadangan/backup jika tersedia
1. Tutup isolasi valve ke area terdampak
1. Matikan kompressor yang bermasalah via panel kontrol (bukan emergency stop kecuali darurat)
1. Drain kondensat setelah shutdown
1. Beri label status di panel
1. Lapor ke Supervisor
**Catatan**: Kehilangan udara tekan ke mesin filling dapat menyebabkan kontaminasi produk — koordinasikan dengan Produksi sebelum shutdown terencana.
## Sistem Kelistrikan
### Kondisi Darurat yang Memerlukan Shutdown
- Kebakaran panel listrik (bau terbakar, asap, percikan api)
- Banjir mendekat ke panel MDP/SDP
- Sengatan listrik pada personel
- Short circuit berulang yang tidak bisa diisolasi
### Urutan Shutdown Listrik
1. Untuk **kebakaran panel**: Jangan gunakan air — gunakan APAR CO₂ atau dry powder. Matikan MCB/MCCB utama terlebih dahulu jika aman.
1. Untuk **sengatan listrik**: Matikan daya sebelum menyentuh korban. Gunakan benda non-konduktor untuk memisahkan korban dari sumber listrik.
1. Isolasi panel/area terdampak via circuit breaker upstream
1. Pasang **lockout-tagout** di breaker yang diisolasi
1. Hubungi K3/HSSE dan Supervisor segera
1. Jika PLN padam: pastikan genset/UPS aktif untuk beban kritis (produksi steril, cold storage)
### Beban Kritis (Tidak Boleh Padam)
- Sistem HVAC area steril
- Cold storage produk jadi
- EMS/BMS monitoring
- Sistem alarm kebakaran
## Kegagalan Mesin Produksi
### Kondisi yang Memerlukan Penghentian Segera
- Mesin mengeluarkan asap, bau terbakar, atau bunyi abnormal keras
- Kerusakan fisik komponen yang membahayakan operator
- Kontaminasi produk terdeteksi selama proses
### Prosedur
1. Tekan tombol **Emergency Stop (E-Stop)** mesin
1. Amankan area sekitar mesin
1. Beri label "Sedang Diperbaiki oleh Engineering"
1. Laporkan via formulir **Laporan Breakdown (F01B)**
1. Engineering melakukan investigasi sebelum restart
1. Uji coba **minimal 15 menit** setelah perbaikan sebelum serahkan ke Produksi
## Eskalasi dan Pelaporan
| Kondisi | Eskalasi ke | Waktu |
|---|---|---|
| Kegagalan sistem kritis (HVAC, listrik) | Supervisor Engineering | Segera (< 5 menit) |
| Supervisor tidak dapat dihubungi | Manager Engineering | Segera |
| Dampak ke produksi/QA | Supervisor + QA Manager | Segera |
| Kebakaran/kecelakaan | HSSE + Management | Segera + hubungi 113/118 |
## Label Status Mesin
| Label | Kondisi |
|---|---|
| "Sedang Diperbaiki oleh Engineering" | Mesin dalam perbaikan oleh teknisi Engineering |
| "Sedang Diperbaiki oleh Vendor" | Mesin dalam perbaikan oleh pihak vendor |
| "JANGAN DIOPERASIKAN" (Lockout-Tagout) | Isolasi darurat; tidak boleh dioperasikan sampai ada otorisasi |
## Related pages
- [[operasi-perawatan-hvac]]
- [[operasi-perawatan-udara-tekan]]
- [[penanganan-lampu-distribusi-listrik]]
- [[penanganan-perbaikan-mesin]]
- [[operasi-perawatan-bms-ems]]
- [[hvac-system]]
- [[electrical-system]]
- [[compressed-air-system]]
- [[maintenance-types]]