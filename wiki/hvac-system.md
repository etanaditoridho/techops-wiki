# Sistem HVAC (Heating, Ventilation, Air Conditioning)

**Summary**: Konsep sistem HVAC di PT EBI — peralatan, fungsi, parameter kritis, dan kaitannya dengan persyaratan GMP/CPOB untuk area produksi farmasi.

**Sources**: `SOP-EBI-EN-016.07 Pengoperasian Dan Perawatan Terhadap Sistem Ventilasi, Pemanas, Tata Udara.pdf`

**Last updated**: 2026-04-14

---

## Definisi

**Sistem Tata Udara (HVAC)** adalah sistem yang mengkondisikan lingkungan melalui pengendalian:
- Suhu
- Kelembaban relatif
- Arah pergerakan udara
- Mutu udara (pengendalian partikel dan pembuangan kontaminan — vapors, fumes)

Disebut "sistem" karena terdiri dari beberapa mesin/alat yang terintegrasi untuk membentuk satu kesatuan yang dapat mengontrol seluruh parameter ruang produksi.
(source: SOP-EBI-EN-016.07 ...pdf)

## Mengapa HVAC Kritis di Fasilitas Farmasi

Desain HVAC memengaruhi:
- **Tata letak ruang** (posisi airlock, pintu)
- **Arah aliran udara** (mencegah kontaminasi silang)
- **Perbedaan tekanan** antar ruangan
- **Pencegahan kontaminasi dan kontaminasi silang** — pertimbangan desain esensial sesuai CPOB

HVAC harus memenuhi persyaratan **CPOB** dan **GEP (Good Engineering Practices)**: keandalan, kemudahan perawatan, keberlanjutan, fleksibilitas, dan keamanan.

## Komponen Utama

| Komponen | Singkatan | Fungsi |
|---|---|---|
| Air Handling Unit | AHU | Unit utama pengkondisian udara — mengontrol suhu, kelembaban, partikel, tekanan, dan aliran udara ruang produksi |
| Fan Coil Unit | FCU | Pendingin ruangan individual dengan remote kontrol |
| Exhaust Fan | EF | Pembuangan udara kotor |
| Chiller Carrier Evergreen 23XRV | — | Menghasilkan air dingin (chilled water) untuk AHU dan FCU |
| Pompa Air Dingin | CHWP | Sirkulasi chilled water |
| Pompa Air Pendingin | CWP | Sirkulasi cooling water ke cooling tower |
| Pompa Air Panas | HWP | Sirkulasi hot water untuk pemanasan AHU |
| Cooling Tower | CT | Membuang panas kondenser ke atmosfer |
| Hot Water Generator | HWG | Menghasilkan air panas untuk sistem |
| Filter HEPA | — | Menyaring partikel ultrafine — kritis untuk cleanroom |

## Sistem Filtrasi Bertingkat

HVAC di PT EBI menggunakan sistem filtrasi bertingkat:

| Tahap | Jenis Filter | Efisiensi | Penempatan |
|---|---|---|---|
| Pre-filter | — | — | Upstream AHU |
| Medium filter | F7 Bag / F7 Rigid Bag | 80–90% | Tengah AHU |
| Final filter | HEPA H10 | 85% | Downstream AHU |

Pemantauan **pressure differential** filter dilakukan **setiap Senin**. Lihat detail setpoint di [[sop-en-016-hvac]].

## Kaitannya dengan Ruang Bersih (Cleanroom)

Kualitas udara di area produksi farmasi dikontrol ketat berdasarkan **klasifikasi ruangan**:
- ISO 14644:1 (klasifikasi partikel)
- CPOB (persyaratan tekanan, kelembaban, dan pertukaran udara per jam)

Pemantauan harian parameter Chiller, pompa, dan filter adalah bagian dari kepatuhan GMP.

## Related pages

- [[sop-en-016-hvac]]
- [[compressed-air-system]]
- [[electrical-system]]
- [[engineering-responsibilities]]
