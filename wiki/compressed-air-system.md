# Sistem Udara Tekan (Compressed Air System)

**Summary**: Konsep sistem udara tekan di PT EBI — klasifikasi, peralatan, dan standar kualitas untuk penggunaan di area produksi farmasi.

**Sources**:
- `SOP-EBI-EN-013 Pengoperasian Dan Perawatan Terhadap Sistem Udara Tekan.DOC` (versi lama)
- `SOP-EBI-EN-013 Pengoperasian Dan Perawatan Terhadap Sistem Udara Tekan.pdf` (Rev.04 — sumber utama)

**Last updated**: 2026-04-14

---

## Definisi

**Sistem udara tekan** adalah sistem yang menjaga kualitas udara yang dipelihara dengan tekanan lebih besar dari tekanan atmosfer.
(source: SOP-EBI-EN-013 ...DOC)

## Dua Klasifikasi Udara Tekan di PT EBI

| Tipe | Penggunaan | Standar Kualitas |
|---|---|---|
| **Kontak Produk** | Kontak langsung dengan produk steril (contoh: proses autoclave) | ISO 14644:1 (partikel) + ISO 8573-1:2010 (uap air & oli) |
| **Non-Kontak Produk** | Tidak kontak langsung dengan produk (contoh: pneumatik) | ISO 8573-1:2010 |

Detail klasifikasi sesuai Point of Use (POU) lihat lampiran `SOP/EBI/EN-004-L01` dan `SOP/EBI/EN-004-L02`.

## Peralatan

| Unit | Peralatan | Keterangan |
|---|---|---|
| Compressor 1 | Ingersoll Rand IRN37 OF-A10 | Unit Udara Tekan 1 |
| Compressor 2 | Ingersoll Rand IRN37 OF-A10 | Unit Udara Tekan 2 |
| Compressor 3 | Atlas Copco ZT37KW | Unit Udara Tekan 3 |
| Dryer 1 | Refrigerator Dryer | Unit 1 — bergantian tiap 1 hari |
| Dryer 2 | Refrigerator Dryer | Unit 2 — bergantian tiap 1 hari |
| Dryer 3 | Heatless Desiccant Dryer | Unit 1 — utama |
| Dryer 4 | Heatless Desiccant Dryer (Atlas Copco) | Cadangan — digunakan jika ada kendala |
| Dryer 5 | Atlas Copco Dryer CD 130+ - 70 | Dryer tambahan |

## Pola Operasi

- Dua compressor IR dan Refrigerator Dryer dijalankan **bergantian setiap 1 hari**.
- Heatless Desiccant Dryer: **1 unit utama aktif**, Atlas Copco sebagai cadangan.
- Kecuali ada kendala — bisa jalankan hanya 1 unit compressor.

## Akses Kontrol

- **Supervisor**: bisa mengubah setting dan parameter mesin.
- **Operator/Teknisi**: hanya bisa **memantau** dan melaporkan penyimpangan ke Supervisor via formulir.

Catatan: mesin IR IRN37 OF-A10 dan Atlas Copco ZT37KW tidak memiliki akses user personel di program mesin.

## Parameter Pemantauan Kunci

| Peralatan | Parameter | Standar |
|---|---|---|
| IR37-OF Compressor | Package discharge pressure | 7–10 bar |
| IR37-OF Compressor | Tank contact/non-contact product pressure | 7–9 bar |
| Atlas Copco ZT37KW | Compressor outlet pressure | 7–10 bar |
| Atlas Copco ZT37KW | Oil pressure | 1,5–2,5 bar |
| Atlas Copco ZT37KW | Compressor outlet temperature | 25–40 °C |
| Refrigerant Dryer D780IN-A | Pressure Dew Point | ≤ 4 °C |
| Heatless Desiccant Dryer D500IL | Pressure Dew Point | -65 s/d -90 °C (alert: -67 °C) |
| Atlas Copco CD 130+ -70 | Pressure Dew Point | -65 s/d -90 °C (alert: -67 °C) |

Detail lengkap parameter per equipment lihat [[sop-en-013-udara-tekan]].

## Interval Perawatan

| Interval | Kode | Contoh Kegiatan |
|---|---|---|
| 3 bulan | L2 | Cek kebocoran pipa, Separator Element, filter udara, electrical connections |
| 6 bulan | L3 | Ganti filter udara (setiap 4.000 jam), greasing fan motor |
| 1 tahun | L4 | Ganti oli coolant (8.000 jam), ganti filter oli, cleaning Separate Element |

## Standar dan Referensi

| Standar | Cakupan |
|---|---|
| ISO 14644:1 | Klasifikasi cleanroom — kandungan partikel |
| ISO 8573-1:2010 | Kualitas udara tekan — kandungan uap air (W) dan oli (O) |

## Related pages

- [[sop-en-013-udara-tekan]]
- [[hvac-system]]
- [[engineering-responsibilities]]
