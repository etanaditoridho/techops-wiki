# Relation Proposals

Generated: 2026-04-24T21:46:45

These are proposal-only typed relations. They were not applied to wiki pages or Notion.

## Summary

- `causes`: 5
- `controls`: 11
- `depends_on`: 5
- `escalates_to`: 49
- `failure_mode_of`: 42
- `monitored_by`: 75
- `owned_by`: 3
- `uses_form`: 58

## Proposals

- `partikel` --`causes`-> `kontaminasi` (medium, wiki/engineering/hvac-system.md:51)
  Evidence: - Menyebabkan kontaminasi partikel pada produk
- `out-of-specification` --`causes`-> `OOS` (medium, wiki/engineering/hvac-system.md:52)
  Evidence: - Memicu out-of-specification (OOS) kondisi lingkungan
- `regulatory` --`causes`-> `recall` (medium, wiki/engineering/synthesis-emergency-shutdown.md:17)
  Evidence: - Memicu investigasi regulatory dan potensi recall
- `mesin filling` --`causes`-> `produksi` (medium, wiki/engineering/synthesis-emergency-shutdown.md:65)
  Evidence: **Catatan**: Kehilangan udara tekan ke mesin filling dapat menyebabkan kontaminasi produk — koordinasikan dengan Produksi sebelum shutdown terencana.
- `produk` --`causes`-> `GMP` (medium, wiki/qa/sop-qa-004-change-control.md:75)
  Evidence: | **Mayor** | Berdampak pada kualitas/keamanan produk dan regulasi/GMP — tidak menyebabkan dampak fatal | Perubahan parameter setting instrumen yang perlu re-kualifikasi |
- `kebocoran` --`controls`-> `keselamatan` (medium, wiki/engineering/electrical-system.md:23)
  Evidence: | Sistem Grounding | Pengamanan dari tegangan berlebih dan kebocoran arus; menjaga keselamatan personel |
- `HVAC` --`controls`-> `produksi` (medium, wiki/engineering/hvac-system.md:3)
  Evidence: **Summary**: Konsep teknis sistem HVAC PT EBI meliputi komponen utama, parameter yang dikontrol, standar filtrasi, dan konteks GMP untuk area produksi farmasi steril.
- `tekanan` --`controls`-> `tekanan diferensial` (medium, wiki/engineering/hvac-system.md:23)
  Evidence: | Exhaust Fan | Membuang udara kotor/tercemar ke luar area; menjaga tekanan diferensial negatif |
- `suhu` --`controls`-> `produksi` (medium, wiki/engineering/hvac-system.md:35)
  Evidence: | Suhu ruangan | Dikontrol per area sesuai standar produksi |
- `tekanan` --`controls`-> `tekanan diferensial` (medium, wiki/engineering/hvac-system.md:38)
  Evidence: | Tekanan diferensial ruangan | Menjaga hirarki tekanan antar ruangan untuk mencegah kontaminasi |
- `kelembaban` --`controls`-> `RH` (medium, wiki/engineering/hvac-system.md:39)
  Evidence: | Kelembaban relatif (RH) | Mencegah kondensasi dan pertumbuhan mikroba |
- `Perawatan` --`controls`-> `kerusakan` (medium, wiki/engineering/maintenance-types.md:15)
  Evidence: **Definisi**: Perawatan terjadwal periodik yang dilakukan sebelum terjadi kerusakan untuk menjaga mesin tetap beroperasi optimal.
- `HVAC` --`controls`-> `suhu` (medium, wiki/engineering/operasi-perawatan-hvac.md:30)
  Evidence: Menjaga sistem HVAC selalu beroperasi normal; menjaga partikel, suhu, aliran udara, pertukaran udara, tekanan, dan kelembaban sesuai standar GMP.
- `Sistem Udara Tekan` --`controls`-> `tekanan` (medium, wiki/engineering/operasi-perawatan-udara-tekan.md:41)
  Evidence: **Sistem Udara Tekan**: sistem yang menjaga kualitas udara dengan tekanan lebih besar dari tekanan atmosfer.
- `Perawatan` --`controls`-> `kerusakan` (medium, wiki/engineering/perawatan-mesin-filling-tofflon.md:38)
  Evidence: | PM (Preventive Maintenance) | Perawatan rutin terjadwal untuk memastikan equipment berfungsi normal dan mencegah kerusakan tak terduga |
- `suhu` --`controls`-> `kelembaban` (medium, wiki/engineering/synthesis-onboarding-teknisi.md:39)
  Evidence: - Parameter yang dikontrol: partikel, suhu, aliran udara, tekanan, kelembaban
- `Genset` --`depends_on`-> `UPS` (medium, wiki/engineering/electrical-system.md:22)
  Evidence: | Genset / UPS | Sumber daya cadangan untuk beban kritis saat PLN padam |
- `HVAC` --`depends_on`-> `pemantauan` (medium, wiki/engineering/operasi-perawatan-bms-ems.md:54)
  Evidence: SOP ini adalah versi pertama (Revision 00) — dokumen baru. Dibuat untuk mendukung sistem pemantauan gedung yang terintegrasi dengan sistem HVAC.
- `AHU` --`depends_on`-> `suhu` (medium, wiki/engineering/operasi-perawatan-hvac.md:46)
  Evidence: **Sistem Tata Udara**: sistem yang mengkondisikan lingkungan melalui pengendalian suhu, kelembaban nisbi, arah pergerakan udara, dan mutu udara — termasuk pengendalian partikel dan pembuangan kontaminan (vapors, fumes). AHU terdiri dari beberapa mesin/alat yang terintegrasi membentuk sistem tata uda
- `HVAC` --`depends_on`-> `Produksi` (medium, wiki/engineering/operasi-perawatan-hvac.md:59)
  Evidence: Sistem HVAC kritis untuk mendukung proses produksi farmasi steril. Semua parameter harus sesuai standar GMP yang berlaku.
- `genset` --`depends_on`-> `UPS` (medium, wiki/engineering/synthesis-emergency-shutdown.md:81)
  Evidence: 6. Jika PLN padam: pastikan genset/UPS aktif untuk beban kritis (produksi steril, cold storage)
- `formulir` --`escalates_to`-> `Lapor` (medium, wiki/engineering/engineering-responsibilities.md:39)
  Evidence: | Dokumentasi | Catat di kartu riwayat mesin; isi formulir pelaporan |
- `Lapor` --`escalates_to`-> `kerusakan` (medium, wiki/engineering/engineering-responsibilities.md:40)
  Evidence: | Pelaporan | Lapor deviasi, kerusakan, dan hasil pekerjaan ke Supervisor |
- `eskalasi` --`escalates_to`-> `Lapor` (medium, wiki/engineering/engineering-responsibilities.md:53)
  Evidence: | Koordinasi | Lapor ke Manager jika ada kerusakan signifikan atau eskalasi |
- `QA` --`escalates_to`-> `HSSE` (medium, wiki/engineering/engineering-responsibilities.md:64)
  Evidence: | Eskalasi | Penanganan insiden level tinggi; koordinasi dengan departemen lain (QA, QS, HSSE) |
- `Lapor` --`escalates_to`-> `kerusakan` (medium, wiki/engineering/engineering-responsibilities.md:74)
  Evidence: - Laporkan kerusakan gedung yang ditemukan
- `eskalasi` --`escalates_to`-> `deviasi` (medium, wiki/engineering/engineering-responsibilities.md:83)
  Evidence: - Eskalasi dilakukan segera jika deviasi ditemukan
- `Laporan Breakdown` --`escalates_to`-> `F01B` (medium, wiki/engineering/maintenance-types.md:45)
  Evidence: 2. Laporan dibuat ke Engineering via formulir (F01B — Laporan Breakdown)
- `Laporan Breakdown` --`escalates_to`-> `F01B` (medium, wiki/engineering/maintenance-types.md:81)
  Evidence: | Laporan Breakdown (F01B) | Pelaporan awal kegagalan mesin oleh operator |
- `EMS` --`escalates_to`-> `BMS` (medium, wiki/engineering/operasi-perawatan-bms-ems.md:30)
  Evidence: | Teknisi EMS & BMS | Operasikan sistem sesuai kebutuhan; perawatan terjadwal; pemantauan harian; lapor deviasi ke Supervisor |
- `EMS` --`escalates_to`-> `Supervisor Engineering` (medium, wiki/engineering/operasi-perawatan-bms-ems.md:31)
  Evidence: | Supervisor Engineering | Jadwal berkala; pastikan pelaksanaan; pastikan alat ukur terkalibrasi; training EMS ke departemen lain; pastikan ketersediaan critical parts; koordinasi & lapor ke Manager jika ada kerusakan |
- `HVAC` --`escalates_to`-> `teknisi` (medium, wiki/engineering/operasi-perawatan-hvac.md:40)
  Evidence: | Teknisi HVAC | Operasikan sistem sesuai kebutuhan; perawatan terjadwal; pemantauan harian; tindak lanjuti PJE dari departemen lain yang menyangkut HVAC; lapor deviasi ke Supervisor |
- `Supervisor Engineering` --`escalates_to`-> `lapor` (medium, wiki/engineering/operasi-perawatan-hvac.md:41)
  Evidence: | Supervisor Engineering | Jadwal berkala; pastikan pelaksanaan; pastikan alat ukur terkalibrasi; training departemen lain; pastikan ketersediaan critical parts; koordinasi & lapor ke Manager jika ada kerusakan |
- `Sistem Pengolahan Air` --`escalates_to`-> `Teknisi` (medium, wiki/engineering/operasi-perawatan-pengolahan-air.md:30)
  Evidence: | Teknisi Sistem Pengolahan Air | Perawatan harian (kebersihan mesin/ruangan), operasikan sesuai standar, pemantauan harian, perawatan terjadwal, lapor deviasi ke Supervisor |
- `Supervisor Engineering` --`escalates_to`-> `Kalibrasi` (medium, wiki/engineering/operasi-perawatan-pengolahan-air.md:31)
  Evidence: | Supervisor Engineering | Jadwal berkala, pastikan pelaksanaan, pastikan alat ukur terkalibrasi, koordinasi ke departemen terkait jika sistem tidak dapat beroperasi, lapor ke Manager jika ada kerusakan, buat tren data conductivity & TOC tiap 3 bulan |
- `Supervisor Engineering` --`escalates_to`-> `lapor` (medium, wiki/engineering/operasi-perawatan-udara-tekan.md:36)
  Evidence: | Supervisor Engineering | Jadwal berkala, pastikan pelaksanaan, pastikan alat ukur terkalibrasi, koordinasi & lapor ke Manager jika ada kerusakan |
- `teknisi` --`escalates_to`-> `Inspeksi` (medium, wiki/engineering/penanganan-lampu-distribusi-listrik.md:40)
  Evidence: | Teknisi Engineering | Inspeksi rutin, identifikasi hazard, perawatan pencegahan & perbaikan, lapor ke Supervisor |
- `vendor` --`escalates_to`-> `PJE` (medium, wiki/engineering/penanganan-perbaikan-mesin.md:3)
  Evidence: **Summary**: Prosedur penanganan dan perbaikan mesin (breakdown, commissioning mesin baru/bekas, PJE dari departemen lain, pekerjaan vendor) di PT EBI termasuk sistem label mesin dan formulir pelaporan.
- `Laporan Breakdown` --`escalates_to`-> `F01B` (medium, wiki/engineering/penanganan-perbaikan-mesin.md:75)
  Evidence: | F01B | Laporan Breakdown |
- `Teknisi` --`escalates_to`-> `Inspeksi` (medium, wiki/engineering/perawatan-gedung-infrastruktur.md:40)
  Evidence: | Teknisi Engineering | Inspeksi, perbaikan cepat, lapor kerusakan |
- `lapor` --`escalates_to`-> `Kerusakan` (medium, wiki/engineering/perawatan-gedung-infrastruktur.md:43)
  Evidence: | Pengguna Area/Ruangan | Lapor kerusakan yang ditemukan; jaga kebersihan area |
- `teknisi` --`escalates_to`-> `Perawatan` (medium, wiki/engineering/perawatan-mesin-filling-bosch.md:30)
  Evidence: | Teknisi PM Engineering | Lakukan perawatan sesuai SOP dan jadwal; lapor kerusakan ke Supervisor |
- `produksi` --`escalates_to`-> `Perawatan` (medium, wiki/engineering/perawatan-mesin-filling-bosch.md:33)
  Evidence: | Operator Mesin Produksi | Lapor kelainan/kerusakan; perawatan harian (kencangkan klem/ferulle/baut kendor; bersihkan body mesin); jaga komponen listrik/elektronik dari air; buang kondensat dari Air Service Regulator |
- `teknisi` --`escalates_to`-> `Perawatan` (medium, wiki/engineering/perawatan-mesin-filling-tofflon.md:30)
  Evidence: | Teknisi PM Engineering | Lakukan perawatan sesuai SOP dan jadwal; lapor kerusakan ke Supervisor |
- `PJE` --`escalates_to`-> `Laporan Breakdown` (medium, wiki/engineering/pje-permintaan-jasa-engineering.md:25)
  Evidence: | Breakdown darurat | Tidak (lapor langsung via Laporan Breakdown F01B, PJE menyusul) |
- `Teknisi` --`escalates_to`-> `Perawatan` (medium, wiki/engineering/preventive-maintenance-mesin.md:31)
  Evidence: | Teknisi PM | Lakukan perawatan sesuai SOP dan jadwal; lapor kerusakan ke Supervisor |
- `eskalasi` --`escalates_to`-> `lapor` (medium, wiki/engineering/synthesis-daily-monitoring.md:14)
  Evidence: - **Deviasi = eskalasi segera**: jangan tunggu akhir shift untuk lapor ke Supervisor
- `kalibrasi` --`escalates_to`-> `lapor` (medium, wiki/engineering/synthesis-daily-monitoring.md:15)
  Evidence: - **Alat ukur rusak**: beri penandaan jelas, lapor ke Supervisor untuk kalibrasi/penggantian
- `produksi` --`escalates_to`-> `lapor` (medium, wiki/engineering/synthesis-daily-monitoring.md:73)
  Evidence: | Harian | Cek lampu penerangan area produksi dan koridor — laporkan yang mati |
- `Laporan Breakdown` --`escalates_to`-> `F01B` (medium, wiki/engineering/synthesis-daily-monitoring.md:88)
  Evidence: | Setiap shift | Terima dan proses Laporan Breakdown (F01B) jika ada |
- `shutdown` --`escalates_to`-> `eskalasi` (medium, wiki/engineering/synthesis-daily-monitoring.md:103)
  Evidence: Supervisor memutuskan: monitor lanjut / shutdown / eskalasi ke Manager
- `Laporan Breakdown` --`escalates_to`-> `F01B` (medium, wiki/engineering/synthesis-daily-monitoring.md:115)
  Evidence: | Laporan Breakdown F01B | Mesin | Saat ada breakdown |
- `AHU` --`escalates_to`-> `teknisi` (medium, wiki/engineering/synthesis-emergency-shutdown.md:19)
  Evidence: Semua teknisi harus mengetahui urutan shutdown yang benar dan cara eskalasi yang tepat.
- `eskalasi` --`escalates_to`-> `Lapor` (medium, wiki/engineering/synthesis-emergency-shutdown.md:26)
  Evidence: 4. **Laporkan segera** — eskalasi ke Supervisor dalam hitungan menit, bukan jam
- `HVAC` --`escalates_to`-> `QA` (medium, wiki/engineering/synthesis-emergency-shutdown.md:47)
  Evidence: **Catatan**: Sistem HVAC area produksi steril yang dimatikan mendadak harus segera diinformasikan ke QA — batch yang sedang diproduksi mungkin terpengaruh.
- `HSSE` --`escalates_to`-> `K3` (medium, wiki/engineering/synthesis-emergency-shutdown.md:80)
  Evidence: 5. Hubungi K3/HSSE dan Supervisor segera
- `Laporan Breakdown` --`escalates_to`-> `F01B` (medium, wiki/engineering/synthesis-emergency-shutdown.md:100)
  Evidence: 4. Laporkan via formulir **Laporan Breakdown (F01B)**
- `eskalasi` --`escalates_to`-> `Lapor` (medium, wiki/engineering/synthesis-emergency-shutdown.md:104)
  Evidence: ## Eskalasi dan Pelaporan
- `HSSE` --`escalates_to`-> `Kebakaran` (medium, wiki/engineering/synthesis-emergency-shutdown.md:111)
  Evidence: | Kebakaran/kecelakaan | HSSE + Management | Segera + hubungi 113/118 |
- `Laporan Breakdown` --`escalates_to`-> `F01B` (medium, wiki/engineering/synthesis-onboarding-teknisi.md:121)
  Evidence: | F01B | Laporan Breakdown | Menerima laporan kegagalan mesin |
- `hvac` --`escalates_to`-> `produksi` (medium, wiki/log.md:143)
  Evidence: - `synthesis-emergency-shutdown.md` — prosedur shutdown HVAC, udara tekan, listrik, mesin produksi; urutan; label; eskalasi
- `Lapor` --`escalates_to`-> `GMP` (medium, wiki/qa/sop-qa-008-deviasi.md:3)
  Evidence: **Summary**: Prosedur manajemen penyimpangan PT EBI mencakup pelaporan, klasifikasi dampak (Event Comment/Non-Conformity/Laporan Penyimpangan), investigasi akar masalah, CAPA, dan penutupan — berlaku untuk semua aktivitas GMP, GDP, dan GLP.
- `Lapor` --`escalates_to`-> `GMP` (medium, wiki/qa/sop-qa-008-deviasi.md:50)
  Evidence: | **Pemrakarsa** | Laporkan semua event penyimpangan ke supervisor/manager; cantumkan nomor laporan di catatan bets/logbook/dokumen GMP; sediakan data dan dokumentasi pendukung |
- `eskalasi` --`escalates_to`-> `Lapor` (medium, wiki/qa/sop-qa-008-deviasi.md:51)
  Evidence: | **Koordinator Penyimpangan** | Daftarkan dokumen ke logsheet tracking (L04); nilai tingkat dampak dan klasifikasikan event; periksa semua informasi laporan; koordinasikan eskalasi ke investigasi; pastikan CAPA sesuai akar masalah; buat tren analisa periodik |
- `QA Manager` --`escalates_to`-> `QA` (medium, wiki/qa/sop-qa-008-deviasi.md:54)
  Evidence: | **QA Manager** | Kaji dan setujui laporan penyimpangan; persetujuan akhir penutupan |
- `Lapor` --`escalates_to`-> `CAPA` (medium, wiki/qa/sop-qa-008-deviasi.md:64)
  Evidence: | **Laporan Penyimpangan** | Dokumentasi formal penyimpangan dengan investigasi dan CAPA |
- `Lapor` --`escalates_to`-> `CAPA` (medium, wiki/qa/sop-qa-008-deviasi.md:76)
  Evidence: | **Laporan Penyimpangan** | Dampak signifikan; investigasi penuh; CAPA wajib; penutupan formal |
- `QA Manager` --`escalates_to`-> `QA` (medium, wiki/qa/sop-qa-008-deviasi.md:99)
  Evidence: QA Manager review dan setujui laporan
- `lapor` --`escalates_to`-> `CAPA` (medium, wiki/qa/sop-qa-035-capa.md:54)
  Evidence: | **Pemilik CAPA (CAPA Owner)** | Inisiasi CAPA sesuai akar masalah; melaksanakan CAPA yang disetujui; lapor kejadian tak terduga; lapor progress implementasi; lakukan pemeriksaan efektivitas; minta perpanjangan/perubahan jika diperlukan; inisiasi pembatalan CAPA jika diperlukan |
- `lapor` --`escalates_to`-> `CAPA` (medium, wiki/qa/sop-qa-035-capa.md:93)
  Evidence: CAPA Owner laporkan progress secara berkala
- `Kompressor` --`failure_mode_of`-> `kegagalan` (medium, wiki/engineering/compressed-air-system.md:69)
  Evidence: - Jika terjadi kegagalan satu kompressor, unit lain mengambil alih beban
- `kebocoran` --`failure_mode_of`-> `keselamatan` (medium, wiki/engineering/electrical-system.md:23)
  Evidence: | Sistem Grounding | Pengamanan dari tegangan berlebih dan kebocoran arus; menjaga keselamatan personel |
- `Lapor` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/engineering-responsibilities.md:40)
  Evidence: | Pelaporan | Lapor deviasi, kerusakan, dan hasil pekerjaan ke Supervisor |
- `eskalasi` --`failure_mode_of`-> `Lapor` (medium, wiki/engineering/engineering-responsibilities.md:53)
  Evidence: | Koordinasi | Lapor ke Manager jika ada kerusakan signifikan atau eskalasi |
- `Lapor` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/engineering-responsibilities.md:74)
  Evidence: - Laporkan kerusakan gedung yang ditemukan
- `Kompresor` --`failure_mode_of`-> `suhu` (medium, wiki/engineering/finding-kompresor-trip-suhu-tinggi.md:1)
  Evidence: # TEST — Kompresor trip saat suhu ambient tinggi
- `Kompresor` --`failure_mode_of`-> `suhu` (medium, wiki/engineering/finding-kompresor-trip-suhu-tinggi.md:3)
  Evidence: **Summary**: Kompresor cenderung trip ketika suhu ruang melebihi 35°C. Perlu tindakan preventif berupa pengecekan ventilasi dan filter udara.
- `Kompresor` --`failure_mode_of`-> `suhu` (medium, wiki/engineering/finding-kompresor-trip-suhu-tinggi.md:14)
  Evidence: Kompresor trip berulang kali saat suhu ambient di ruang kompresor melebihi 35°C.
- `Kompresor` --`failure_mode_of`-> `suhu` (medium, wiki/engineering/finding-kompresor-trip-suhu-tinggi.md:23)
  Evidence: Tambahkan monitoring suhu otomatis di ruang kompresor dan set alert di 33°C sebelum mencapai threshold trip.
- `HVAC` --`failure_mode_of`-> `produksi` (medium, wiki/engineering/hvac-system.md:50)
  Evidence: Sistem HVAC adalah **sistem kritis** dalam produksi farmasi steril. Kegagalan sistem HVAC dapat:
- `Perawatan` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/maintenance-types.md:15)
  Evidence: **Definisi**: Perawatan terjadwal periodik yang dilakukan sebelum terjadi kerusakan untuk menjaga mesin tetap beroperasi optimal.
- `Teknisi` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/maintenance-types.md:71)
  Evidence: | Preventive (PM) | Sebelum kerusakan | Jadwal berkala | Teknisi Engineering |
- `Teknisi` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/maintenance-types.md:73)
  Evidence: | Breakdown (BM) | Setelah kerusakan | Mesin gagal operasi | Teknisi Engineering |
- `Laporan Breakdown` --`failure_mode_of`-> `F01B` (medium, wiki/engineering/maintenance-types.md:81)
  Evidence: | Laporan Breakdown (F01B) | Pelaporan awal kegagalan mesin oleh operator |
- `EMS` --`failure_mode_of`-> `Supervisor Engineering` (medium, wiki/engineering/operasi-perawatan-bms-ems.md:31)
  Evidence: | Supervisor Engineering | Jadwal berkala; pastikan pelaksanaan; pastikan alat ukur terkalibrasi; training EMS ke departemen lain; pastikan ketersediaan critical parts; koordinasi & lapor ke Manager jika ada kerusakan |
- `Supervisor Engineering` --`failure_mode_of`-> `lapor` (medium, wiki/engineering/operasi-perawatan-hvac.md:41)
  Evidence: | Supervisor Engineering | Jadwal berkala; pastikan pelaksanaan; pastikan alat ukur terkalibrasi; training departemen lain; pastikan ketersediaan critical parts; koordinasi & lapor ke Manager jika ada kerusakan |
- `Supervisor Engineering` --`failure_mode_of`-> `Kalibrasi` (medium, wiki/engineering/operasi-perawatan-pengolahan-air.md:31)
  Evidence: | Supervisor Engineering | Jadwal berkala, pastikan pelaksanaan, pastikan alat ukur terkalibrasi, koordinasi ke departemen terkait jika sistem tidak dapat beroperasi, lapor ke Manager jika ada kerusakan, buat tren data conductivity & TOC tiap 3 bulan |
- `Shutdown` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/operasi-perawatan-pengolahan-air.md:40)
  Evidence: | Shutdown Water System | Kondisi semua sistem air tidak dapat sanitasi karena kerusakan boiler (sumber panas sanitasi) |
- `Supervisor Engineering` --`failure_mode_of`-> `lapor` (medium, wiki/engineering/operasi-perawatan-udara-tekan.md:36)
  Evidence: | Supervisor Engineering | Jadwal berkala, pastikan pelaksanaan, pastikan alat ukur terkalibrasi, koordinasi & lapor ke Manager jika ada kerusakan |
- `produksi` --`failure_mode_of`-> `kegagalan` (medium, wiki/engineering/penanganan-lampu-distribusi-listrik.md:58)
  Evidence: - Meminimalkan risiko kegagalan sistem yang mengganggu produksi
- `Perawatan` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/penanganan-perbaikan-mesin.md:44)
  Evidence: | Autonomous Maintenance | Perawatan mandiri oleh operator; deteksi dini gejala kerusakan sebelum breakdown |
- `Teknisi` --`failure_mode_of`-> `Inspeksi` (medium, wiki/engineering/perawatan-gedung-infrastruktur.md:40)
  Evidence: | Teknisi Engineering | Inspeksi, perbaikan cepat, lapor kerusakan |
- `lapor` --`failure_mode_of`-> `Kerusakan` (medium, wiki/engineering/perawatan-gedung-infrastruktur.md:43)
  Evidence: | Pengguna Area/Ruangan | Lapor kerusakan yang ditemukan; jaga kebersihan area |
- `Teknisi` --`failure_mode_of`-> `PJE` (medium, wiki/engineering/perawatan-gedung-infrastruktur.md:49)
  Evidence: 2. **Perbaikan cepat** (kerusakan ringan): teknisi langsung tanpa PJE
- `PJE` --`failure_mode_of`-> `Kerusakan` (medium, wiki/engineering/perawatan-gedung-infrastruktur.md:50)
  Evidence: 3. **Perbaikan via PJE** (kerusakan sedang/berat): permintaan formal ke Engineering
- `teknisi` --`failure_mode_of`-> `Perawatan` (medium, wiki/engineering/perawatan-mesin-filling-bosch.md:30)
  Evidence: | Teknisi PM Engineering | Lakukan perawatan sesuai SOP dan jadwal; lapor kerusakan ke Supervisor |
- `produksi` --`failure_mode_of`-> `Perawatan` (medium, wiki/engineering/perawatan-mesin-filling-bosch.md:33)
  Evidence: | Operator Mesin Produksi | Lapor kelainan/kerusakan; perawatan harian (kencangkan klem/ferulle/baut kendor; bersihkan body mesin); jaga komponen listrik/elektronik dari air; buang kondensat dari Air Service Regulator |
- `teknisi` --`failure_mode_of`-> `Perawatan` (medium, wiki/engineering/perawatan-mesin-filling-tofflon.md:30)
  Evidence: | Teknisi PM Engineering | Lakukan perawatan sesuai SOP dan jadwal; lapor kerusakan ke Supervisor |
- `Perawatan` --`failure_mode_of`-> `kerusakan` (medium, wiki/engineering/perawatan-mesin-filling-tofflon.md:38)
  Evidence: | PM (Preventive Maintenance) | Perawatan rutin terjadwal untuk memastikan equipment berfungsi normal dan mencegah kerusakan tak terduga |
- `teknisi` --`failure_mode_of`-> `PJE` (medium, wiki/engineering/pje-permintaan-jasa-engineering.md:26)
  Evidence: | Perbaikan cepat gedung (kerusakan ringan) | Tidak (teknisi langsung tanpa PJE) |
- Additional proposals omitted from Markdown view: 148
