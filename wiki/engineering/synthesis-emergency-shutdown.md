# Synthesis: Prosedur Emergency Shutdown

##  LLM Summary
- System: Emergency Shutdown Lintas Sistem
- Equipment: HVAC, kompresor, panel listrik, mesin produksi, chiller, pompa
- Symptoms: [shutdown darurat, kegagalan sistem kritis, alarm, kebakaran, kebocoran, short circuit]
- Keywords: [emergency shutdown, shutdown darurat, eskalasi, keselamatan, GMP, stop mesin]
- Severity: High

**Summary**: Sintesis prosedur penghentian darurat dan penanganan kegagalan sistem lintas semua SOP Engineering — HVAC, udara tekan, kelistrikan, dan mesin produksi.

**Sources**: `SOP-EBI-EN-016.07`, `SOP-EBI-EN-013 Rev.04`, `SOP-EBI-EN-001.02`, `SOP-EBI-EN-014.01`, `SOP-EBI-EN-055.00`

**Last updated**: 2026-04-22

---

## Mengapa Ini Penting

Kegagalan sistem di fasilitas produksi farmasi steril dapat:
- Mencemari batch produksi
- Membahayakan keselamatan personel
- Menyebabkan kerusakan peralatan permanen
- Memicu investigasi regulatory dan potensi recall

Semua teknisi harus mengetahui urutan shutdown yang benar dan cara eskalasi yang tepat.

## Prinsip Umum Emergency Shutdown

1. **Utamakan keselamatan personel** — evakuasi area jika bahaya langsung
2. **Ikuti urutan shutdown yang benar** — penghentian sembarangan dapat merusak mesin atau memperparah kondisi
3. **Beri tanda/label** — mesin yang dimatikan darurat harus diberi label status
4. **Laporkan segera** — eskalasi ke Supervisor dalam hitungan menit, bukan jam
5. **Jangan restart tanpa otorisasi** — Supervisor atau Manager harus menyetujui restart setelah investigasi

## Sistem HVAC

### Kondisi Darurat yang Memerlukan Shutdown
- Kebakaran di ruang mesin HVAC
- Kebocoran refrigerant (freon) dari chiller
- Kegagalan total blower/fan AHU di area kritis
- Alarm suhu atau tekanan chiller di luar batas operasi
- Banjir atau intrusi air ke panel kontrol

### Urutan Shutdown HVAC
1. Matikan AHU/FCU area terdampak terlebih dahulu
2. Matikan chiller setelah beban (AHU/FCU) dimatikan
3. Matikan pompa sirkulasi setelah chiller berhenti
4. Matikan cooling tower terakhir
5. Pastikan semua isolasi valve terkunci jika diperlukan
6. Beri label "JANGAN DIOPERASIKAN" di panel kontrol
7. Lapor ke Supervisor segera

**Catatan**: Sistem HVAC area produksi steril yang dimatikan mendadak harus segera diinformasikan ke QA — batch yang sedang diproduksi mungkin terpengaruh.

## Sistem Udara Tekan

### Kondisi Darurat yang Memerlukan Shutdown
- Kebocoran udara tekan besar (suara desis/tekanan turun drastis)
- Temperatur kompressor over-limit (alarm temperatur)
- Kebakaran di ruang kompressor
- Kegagalan total dryer saat produksi sedang berjalan

### Urutan Shutdown Udara Tekan
1. Aktifkan kompressor cadangan/backup jika tersedia
2. Tutup isolasi valve ke area terdampak
3. Matikan kompressor yang bermasalah via panel kontrol (bukan emergency stop kecuali darurat)
4. Drain kondensat setelah shutdown
5. Beri label status di panel
6. Lapor ke Supervisor

**Catatan**: Kehilangan udara tekan ke mesin filling dapat menyebabkan kontaminasi produk — koordinasikan dengan Produksi sebelum shutdown terencana.

## Sistem Kelistrikan

### Kondisi Darurat yang Memerlukan Shutdown
- Kebakaran panel listrik (bau terbakar, asap, percikan api)
- Banjir mendekat ke panel MDP/SDP
- Sengatan listrik pada personel
- Short circuit berulang yang tidak bisa diisolasi

### Urutan Shutdown Listrik
1. Untuk **kebakaran panel**: Jangan gunakan air — gunakan APAR CO₂ atau dry powder. Matikan MCB/MCCB utama terlebih dahulu jika aman.
2. Untuk **sengatan listrik**: Matikan daya sebelum menyentuh korban. Gunakan benda non-konduktor untuk memisahkan korban dari sumber listrik.
3. Isolasi panel/area terdampak via circuit breaker upstream
4. Pasang **lockout-tagout** di breaker yang diisolasi
5. Hubungi K3/HSSE dan Supervisor segera
6. Jika PLN padam: pastikan genset/UPS aktif untuk beban kritis (produksi steril, cold storage)

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
2. Amankan area sekitar mesin
3. Beri label "Sedang Diperbaiki oleh Engineering"
4. Laporkan via formulir **Laporan Breakdown (F01B)**
5. Engineering melakukan investigasi sebelum restart
6. Uji coba **minimal 15 menit** setelah perbaikan sebelum serahkan ke Produksi

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
- [[hvac-failure-diagnosis]]
- [[boiler-leak-response]]
- [[electrical-system]]
- [[compressed-air-system]]
- [[maintenance-types]]
- [[engineering-responsibilities]]
