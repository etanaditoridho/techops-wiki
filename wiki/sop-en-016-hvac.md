# SOP/EBI/EN-016 — Pengoperasian dan Perawatan Sistem HVAC

**Summary**: Source summary untuk SOP pengoperasian dan perawatan sistem HVAC (Heating, Ventilation, Air Conditioning) di PT Etana Biotechnologies Indonesia — sistem kritis untuk area produksi GMP.

**Sources**: 
- `SOP-EBI-EN-016.07 Pengoperasian Dan Perawatan Terhadap Sistem Ventilasi, Pemanas, Tata Udara.pdf`
- `SOP-EBI-EN-016.07 Pengoperasian Dan Perawatan Terhadap Sistem Ventilasi, Pemanas, Tata Udara.docx`

**Last updated**: 2026-04-14

---

## Identitas Dokumen

| Field | Value |
|---|---|
| SOP No. | SOP/EBI/EN-016 |
| Revision | 07 |
| Prepared by | Riki Depano (Engineering SPV) |
| Reviewed by | Purno Budi Kiswanto (Engineering Manager) |
| Approved by | Shandy (QA Manager) |
| Halaman | 41 halaman |

## Tujuan

1. Petunjuk pengoperasian dan perawatan sistem HVAC (Ventilasi, Pemanas, Tata Udara) sesuai standar PT EBI.
2. Memastikan HVAC beroperasi normal: menjaga jumlah partikel, suhu, aliran udara, pertukaran udara, tekanan, dan kelembaban sesuai standar yang ditetapkan.
3. Mendukung semua kegiatan, terutama **proses produksi** (sesuai CPOB/GMP dan GEP).
(source: SOP-EBI-EN-016.07 ...pdf)

## Peralatan yang Dicakup

| Peralatan | Fungsi |
|---|---|
| **AHU (Air Handling Unit)** | Mengkondisikan udara: suhu, kelembaban, partikel, tekanan, aliran udara ruang produksi |
| **FCU (Fan Coil Unit)** | Mendinginkan ruangan via remote kontrol |
| **Exhaust Fan** | Ventilasi pembuangan udara |
| **Chiller Carrier Evergreen 23XRV** | Menghasilkan air dingin untuk sistem pendinginan |
| **Pompa Sirkulasi** | Pompa air dingin (CHWP), air pendingin (CWP), air panas (HWP) |
| **Cooling Tower (CT)** | Membuang panas kondenser ke atmosfer |
| **Hot Water Generator** | Menghasilkan air panas untuk sistem AHU |
| **Filter HEPA** | Menyaring partikel ultrafine — kritis untuk cleanroom GMP |

## Ruang Lingkup

Area: **Produksi, QA, QC, Warehouse, CUB** (Central Utility Building)

## Parameter Pemantauan Harian (Chiller)

| Parameter | Setpoint |
|---|---|
| Suhu supply air dingin (CHL OUT) | 6–7 °C |
| Suhu return air dingin (CHL IN) | 9–12 °C |
| Suhu supply air pendingin (CWP supply) | 31 °C |
| Suhu return air pendingin | 36 °C |
| Suhu return air panas | 20–55 °C |
| LCL set point | 6–7 °C |
| ECL set point | 9–12 °C |
| % AMP IN | ≥ 40% |
| Oil Level (Sight Glass) | ≥ 50% |
| Suhu Motor Winding Compressor | ≤ 93 °C |
| Suhu Discharge Compressed Air | ≤ 60 °C |
| Oil Pressure AP running | min 170 kPa |
| Condensor Pressure | ≤ 1000 kPa |
| Refrigerant Evaporator Pressure | 250–400 kPa |
| Tekanan air dingin IN | 3–5 Bar |
| Tekanan air dingin OUT | 2.5–4.5 Bar |
| Tekanan air pendingin IN | ≥ 1.5 Bar |
| Tekanan air pendingin OUT | ≥ 1 Bar |
| Rectifier Temperature | ≤ 71 °C |
| Inverter Temperature | ≤ 71 °C |

## Pemantauan Filter (Mingguan — setiap Senin)

| Filter | Efisiensi | Batas Waspada | Batas Tindakan |
|---|---|---|---|
| **F7 Bag** | 80–85% | ≤15 Pa atau ≥335 Pa | ≤10 Pa atau ≥350 Pa |
| **F7 Rigid Bag** | 80–90% | ≤15 Pa atau ≥335 Pa | ≤10 Pa atau ≥350 Pa |
| **HEPA H10** | 85% | ≤100 Pa atau ≥485 Pa | ≤90 Pa atau ≥500 Pa |

- **Batas waspada**: Lapor ke atasan, periksa penyebab, siapkan spare parts untuk jadwal penggantian.
- **Batas tindakan**: Lapor dan koordinasi dengan user untuk jadwal penggantian segera.

## Prosedur Operasi Singkat

### Menghidupkan HVAC
1. Hidupkan AHU (tekan tombol ON/hijau pada panel starter AHU)
2. Hidupkan hot water generator (tombol ON pada panel kontrol)
3. Hidupkan Chiller (tekan dan tahan tombol START 1 detik pada layar ICVC)
4. Hidupkan CT, CHWP, CWP (tombol ON pada panel starter Chiller)

### Mematikan HVAC
1. Matikan AHU (tekan tombol OFF/merah)
2. Matikan hot water generator (tombol OFF/merah)
3. Matikan Chiller (tekan dan tahan tombol STOP 1 detik pada ICVC)
4. Matikan CT, CHWP, CWP (tombol OFF pada panel starter)

### Operasi FCU
- Tekan ON/OFF pada remote kontrol; atur suhu yang diinginkan.

## Tanggung Jawab

| Peran | Tanggung Jawab |
|---|---|
| Teknisi HVAC | Operasikan HVAC; lakukan pemantauan harian; perawatan berkala; follow up PJE dari departemen lain; lapor penyimpangan ke Supervisor |
| Supervisor Engineering | Jadwal perawatan berkala; pastikan kalibrasi alat ukur; training; pastikan stok critical parts; koordinasi laporan kerusakan ke Manager |
| Manager Engineering | Tentukan spare parts pengganti; putuskan penggantian/modifikasi sistem HVAC |

## Kepatuhan Regulasi

- **CPOB 2018** (Cara Pembuatan Obat yang Baik) / GMP
- **GEP** (Good Engineering Practices): keandalan, perawatan, keberlanjutan, fleksibilitas, keamanan

## Related pages

- [[hvac-system]]
- [[engineering-responsibilities]]
- [[sop-en-001-lampu-listrik]]
- [[sop-en-013-udara-tekan]]
