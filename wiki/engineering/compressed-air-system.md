# Sistem Udara Tekan — Konsep & Komponen

**Summary**: Konsep teknis sistem udara tekan PT EBI meliputi klasifikasi udara, konfigurasi peralatan, standar kualitas, dan jadwal perawatan.

**Sources**: `SOP-EBI-EN-013 Pengoperasian Dan Perawatan Terhadap Sistem Udara Tekan.pdf`

**Last updated**: 2026-04-22

---

## Definisi

**Sistem Udara Tekan**: sistem yang menghasilkan dan mendistribusikan udara dengan tekanan lebih besar dari tekanan atmosfer untuk keperluan produksi, instrumentasi, dan pneumatik.

## Klasifikasi Udara Tekan PT EBI

| Tipe | Penggunaan | Persyaratan Kualitas |
|---|---|---|
| Kontak Produk | Udara kontak langsung dengan produk steril (misal: autoclave, filling) | Standar lebih ketat — bebas oil, partikel, dan mikroba |
| Non-Kontak Produk | Udara tidak kontak langsung (misal: pneumatik, aktuator) | Standar umum — bebas oil dan air |

## Konfigurasi Peralatan

### Kompressor (3 Unit)
| Unit | Model | Tipe |
|---|---|---|
| Compressed Air 1 | Ingersoll Rand IRN37 OF-A10 | Oil-free rotary screw |
| Compressed Air 2 | Atlas Copco ZT37KW | Oil-free rotary screw |
| Compressed Air 3 | (cadangan/rotasi) | — |

Kompressor dijalankan secara bergantian (rotasi harian) untuk pemerataan jam operasi.

### Dryer (4 Unit)
| Unit | Tipe | Jumlah | Keterangan |
|---|---|---|---|
| RD1, RD2 | Refrigerator Dryer | 2 | Bergantian setiap 1 hari |
| DD1, DD2 | Heatless Desiccant Dryer | 2 | Untuk udara berkualitas tinggi (kontak produk) |
| CD-130+ | Atlas Copco Dryer CD 130+ | 1 | Cadangan/backup |

## Prinsip Kerja

1. **Kompressor** mengompresi udara atmosfer
2. **Refrigerator Dryer** mendinginkan udara untuk kondensasi dan pembuangan air
3. **Desiccant Dryer** menghilangkan sisa kelembaban (dew point sangat rendah)
4. **Receiver tank** menyimpan udara tekan sebagai buffer
5. **Distribusi** melalui jaringan pipa ke titik penggunaan

## Parameter Pemantauan Kunci

| Parameter | Keterangan |
|---|---|
| Tekanan sistem | Dipantau di outlet kompressor dan titik distribusi |
| Dew point | Indikator kandungan uap air; kritis untuk udara kontak produk |
| Temperatur outlet | Indikator kondisi kompressor |
| Oil carry-over | Harus nol untuk kompressor oil-free |
| Partikel | Dipantau untuk udara kontak produk |

## Jadwal Perawatan

| Level | Interval | Lingkup |
|---|---|---|
| L2 | Mingguan / 2 mingguan | Pengecekan visual, log parameter, drain kondensat |
| L3 | Bulanan | Penggantian filter, pembersihan menyeluruh |
| L4 | Tahunan / semi-tahunan | Overhaul kompressor, penggantian desiccant, kalibrasi alat ukur |

## Catatan Operasional

- Kompressor dan refrigerant dryer dioperasikan bergantian setiap 1 hari
- Jika terjadi kegagalan satu kompressor, unit lain mengambil alih beban
- Detail parameter monitoring numerik dan prosedur start/stop per equipment terdapat di SOP/EBI/EN-013 Rev.04

## Related pages

- [[operasi-perawatan-udara-tekan]]
- [[finding-kompresor-trip-suhu-tinggi]]
- [[maintenance-types]]
- [[engineering-responsibilities]]
- [[synthesis-daily-monitoring]]
