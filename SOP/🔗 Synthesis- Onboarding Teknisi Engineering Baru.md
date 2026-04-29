---
title: "🔗 Synthesis: Onboarding Teknisi Engineering Baru"
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
  - Synthesis Emergency Shutdown
  - Hvac System
  - Maintenance Types
  - Operasi Perawatan Hvac
  - Compressed Air System
  - SOP EN-001
  - SOP EN-003
notion_id: 34c664a8-3e24-8199-8e35-e80aaa468f08
synced: 2026-04-29
---

**Summary**: Panduan orientasi bagi teknisi Engineering baru di PT EBI — apa yang harus dipelajari, sistem apa yang harus dipahami, dan prosedur apa yang wajib dikuasai sebelum bekerja mandiri.
**Sources**: `SOP-EBI-EN-001.02`, `SOP-EBI-EN-003.03`, `SOP-EBI-EN-004.02`, `SOP-EBI-EN-005.03`, `SOP-EBI-EN-013 Rev.04`, `SOP-EBI-EN-014.01`, `SOP-EBI-EN-016.07`, `SOP-EBI-EN-055.00`
**Last updated**: 2026-04-22
## Tujuan Dokumen Ini
Halaman ini mensintesiskan pengetahuan yang tersebar di 11+ SOP Engineering menjadi panduan terstruktur untuk teknisi baru. Ini bukan pengganti SOP resmi — melainkan peta orientasi untuk memahami ekosistem Engineering PT EBI.
## Fase 1: Orientasi Organisasi (Hari 1–3)
### Pahami Struktur Engineering
Baca [[engineering-responsibilities]] untuk memahami:
- Peran Teknisi, Supervisor, dan Manager Engineering
- Spesialisasi bidang (HVAC, Utility, Listrik, Non-Utility, EMS/BMS, Site)
- Ke siapa melapor dalam berbagai situasi
### Pahami Area yang Dilayani
| Area | Sistem Kritis |
|---|---|
| Area Produksi | HVAC steril, udara tekan kontak produk, mesin filling |
| QA/QC | HVAC laboratorium, EMS monitoring |
| Warehouse & CUB | Cold storage, HVAC, sistem listrik |
| Gedung & Infrastruktur | Panel listrik, sistem penerangan, fasilitas umum |
## Fase 2: Sistem Teknis (Minggu 1–2)
### Sistem HVAC
Baca [[hvac-system]] dan [[operasi-perawatan-hvac]]:
- Komponen: AHU, FCU, chiller, cooling tower, HWG, HEPA filter
- Parameter yang dikontrol: partikel, suhu, aliran udara, tekanan, kelembaban
- Konteks GMP — mengapa HVAC kritis di fasilitas farmasi
- Integrasi dengan BMS/EMS
### Sistem Udara Tekan
Baca [[compressed-air-system]] dan [[operasi-perawatan-udara-tekan]]:
- Klasifikasi: kontak produk vs non-kontak produk
- Peralatan: kompressor Ingersoll Rand + Atlas Copco, dryer refrigerant + desiccant
- Pola rotasi harian kompressor dan dryer
- Jadwal perawatan L2/L3/L4
### Sistem Kelistrikan
Baca [[electrical-system]] dan [[penanganan-lampu-distribusi-listrik]]:
- Alur distribusi: PLN → transformator → MDP → SDP → beban
- Standar yang berlaku: PUIL 2011, Permenaker 12/2015
- Persyaratan kompetensi: K3 Listrik
### EMS & BMS
Baca [[operasi-perawatan-bms-ems]]:
- Fungsi BMS: kontrol otomatis sistem HVAC
- Fungsi EMS: monitoring lingkungan kritis, alert deviasi
- Hanya personel terlatih yang boleh mengoperasikan
## Fase 3: Prosedur Kerja (Minggu 2–4)
### Jenis-Jenis Perawatan
Baca [[maintenance-types]]:
- **PM** (Preventive): terjadwal, sebelum rusak
- **CM** (Corrective): dijadwal ulang karena halangan
- **BM** (Breakdown): reaktif setelah gagal
- **AM** (Autonomous): dilakukan operator, bukan teknisi
### Proses PJE
Baca [[pje-permintaan-jasa-engineering]]:
- PJE = formulir resmi dari departemen lain ke Engineering
- Kapan PJE diperlukan vs tidak
- Alur: penerimaan → penugasan → pelaksanaan → verifikasi
### Penanganan Breakdown
Baca [[penanganan-perbaikan-mesin]]:
- Terima laporan via F01B
- Catat pekerjaan di F02B (Kartu Riwayat Mesin)
- Uji coba 15 menit sebelum serahkan ke user
- Bedakan label Engineering vs label Vendor
### Manajemen Suku Cadang
Baca [[spare-parts-management]] dan [[pengelolaan-suku-cadang]]:
- Critical vs Non-Critical — perbedaan dan implikasi stok
- Cara menggunakan Part Code dan Database Inventory
- Prosedur minta suku cadang via F03B
- Change control untuk perubahan spesifikasi kritikal
## Fase 4: Keselamatan Kerja
### APD yang Wajib Digunakan
| Area/Pekerjaan | APD |
|---|---|
| Area produksi GMP | Sesuai standar GMP (gown, gloves, dll.) |
| Pekerjaan listrik | Sarung tangan dielektrik, sepatu safety |
| Ruang mesin (HVAC, kompressor) | Safety shoes, helm |
| Pekerjaan di ketinggian | Harness, helm, safety shoes |
| Gudang suku cadang (angkat berat) | Sarung tangan, safety shoes |
### Emergency Shutdown
Baca [[synthesis-emergency-shutdown]] — wajib dipahami sebelum bertugas mandiri:
- Urutan shutdown HVAC, udara tekan, dan listrik
- Cara menggunakan label status mesin
- Kapan dan bagaimana eskalasi
## Dokumen/Formulir yang Harus Dikenal
| Kode | Nama | Digunakan Saat |
|---|---|---|
| F01B | Laporan Breakdown | Menerima laporan kegagalan mesin |
| F02B | Kartu Riwayat Mesin | Mencatat semua pekerjaan per mesin |
| F03B | Formulir Permintaan Barang | Butuh spare parts untuk PJE/BM |
| F04B | Laporan Pekerjaan Vendor | Vendor selesai mengerjakan perbaikan |
| Form PJE | Permintaan Jasa Engineering | Permintaan dari departemen lain |
| Form PM | Formulir PM per sistem | Setelah menyelesaikan pekerjaan PM |
## Sistem Monitoring Harian
Baca [[synthesis-daily-monitoring]] untuk panduan lengkap apa yang harus diperiksa setiap hari di setiap sistem.
## Checklist Onboarding