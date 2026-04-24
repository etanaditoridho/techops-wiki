# Sistem HVAC — Konsep & Komponen

##  LLM Summary
- System: HVAC
- Equipment: AHU, FCU, exhaust fan, chiller, cooling tower, HWG, HEPA filter
- Symptoms: []
- Keywords: [HVAC, AHU, FCU, suhu, kelembaban, tekanan diferensial, HEPA]
- Severity: N/A

**Summary**: Konsep teknis sistem HVAC PT EBI meliputi komponen utama, parameter yang dikontrol, standar filtrasi, dan konteks GMP untuk area produksi farmasi steril.

**Sources**: `SOP-EBI-EN-016.07 Pengoperasian Dan Perawatan Terhadap Sistem Ventilasi, Pemanas, Tata Udara.pdf`, `SOP-EBI-EN-055.00 BMS EMS Final engineering.pdf`

**Last updated**: 2026-04-22

---

## Definisi

**Sistem Tata Udara (HVAC)**: sistem yang mengkondisikan lingkungan melalui pengendalian suhu, kelembaban nisbi, arah pergerakan udara, dan mutu udara — termasuk pengendalian partikel dan pembuangan kontaminan (vapors, fumes).

AHU (Air Handling Unit) terdiri dari beberapa mesin/alat yang terintegrasi membentuk sistem tata udara.

## Komponen Utama

| Komponen | Fungsi |
|---|---|
| Air Handling Unit (AHU) | Unit pengkondisi udara terpusat; mengintegrasikan cooling, heating, filtrasi, dan distribusi udara |
| Fan Coil Unit (FCU) | Unit pendingin/pemanas lokal di ruangan; menggunakan air dingin atau panas dari chiller/HWG |
| Exhaust Fan | Membuang udara kotor/tercemar ke luar area; menjaga tekanan diferensial negatif |
| Chiller Carrier Evergreen 23XRV | Menghasilkan air dingin untuk sistem AHU dan FCU |
| Pompa Sirkulasi | Mendistribusikan air dingin (chilled water), air pendingin (condenser water), dan air panas (hot water) |
| Cooling Tower | Membuang panas kondensor ke atmosfer |
| Hot Water Generator (HWG) | Menghasilkan air panas untuk pemanasan udara (reheat) di sistem AHU |
| HEPA Filter | High-Efficiency Particulate Air filter — menyaring partikel hingga ukuran 0,3 µm dengan efisiensi ≥99,97% |

## Parameter yang Dikontrol

| Parameter | Keterangan |
|---|---|
| Jumlah partikel udara | Sesuai klasifikasi ruangan GMP (ISO Class) |
| Suhu ruangan | Dikontrol per area sesuai standar produksi |
| Aliran udara (air flow) | Volume udara per satuan waktu; menentukan distribusi merata |
| Pertukaran udara (ACH) | Air Changes per Hour — frekuensi pergantian udara total per jam |
| Tekanan diferensial ruangan | Menjaga hirarki tekanan antar ruangan untuk mencegah kontaminasi |
| Kelembaban relatif (RH) | Mencegah kondensasi dan pertumbuhan mikroba |

## Klasifikasi Area yang Dilayani

- **Area Produksi**: ruangan steril dan non-steril; kritis untuk kontrol partikel dan tekanan
- **Area QA/QC**: laboratorium; membutuhkan kondisi lingkungan stabil
- **Warehouse & CUB**: penyimpanan bahan baku dan produk; kontrol suhu dan kelembaban
- **CUB (Central Utility Building)**: ruang mesin utama sistem HVAC

## Konteks GMP

Sistem HVAC adalah **sistem kritis** dalam produksi farmasi steril. Kegagalan sistem HVAC dapat:
- Menyebabkan kontaminasi partikel pada produk
- Memicu out-of-specification (OOS) kondisi lingkungan
- Mengharuskan investigasi dan potensi reject batch produksi

Semua parameter harus terdokumentasi dan dipantau secara real-time via [[operasi-perawatan-bms-ems|EMS/BMS]].

## Integrasi dengan BMS/EMS

BMS (Building Management System) mengintegrasikan kontrol dan monitoring sistem HVAC secara otomatis. EMS (Environmental Monitoring System) memantau parameter lingkungan kritis secara kontinu dan menghasilkan alert jika terjadi deviasi.

## Jadwal Perawatan

| Level | Interval |
|---|---|
| Harian | Pengecekan visual, pembacaan parameter, log BMS/EMS |
| Mingguan | Pembersihan filter pre/intermediate, pengecekan kondensasi |
| Bulanan | Penggantian filter medium, kalibrasi sensor |
| Tahunan/Semi-tahunan | Penggantian HEPA filter, overhaul chiller, cleaning cooling tower |

## Related pages

- [[operasi-perawatan-hvac]]
- [[operasi-perawatan-bms-ems]]
- [[hvac-failure-diagnosis]]
- [[boiler-leak-response]]
- [[maintenance-types]]
- [[engineering-responsibilities]]
- [[synthesis-daily-monitoring]]
