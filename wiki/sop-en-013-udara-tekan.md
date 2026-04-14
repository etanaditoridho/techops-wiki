# SOP/EBI/EN-013 — Pengoperasian dan Perawatan Sistem Udara Tekan

**Summary**: Source summary untuk SOP pengoperasian dan perawatan sistem udara tekan (compressed air) di PT Etana Biotechnologies Indonesia.

**Sources**:
- `SOP-EBI-EN-013 Pengoperasian Dan Perawatan Terhadap Sistem Udara Tekan.DOC` (versi lama, tanpa nomor revisi)
- `SOP-EBI-EN-013 Pengoperasian Dan Perawatan Terhadap Sistem Udara Tekan.pdf` (**Rev.04**, 37 halaman — sumber utama)

**Last updated**: 2026-04-14

---

## Identitas Dokumen

| Field | Value |
|---|---|
| SOP No. | SOP/EBI/EN-013 |
| Revision | **04** (sumber: PDF Rev.04) |
| Total halaman | 26 halaman prosedur + lampiran |
| Signatories | Riki Depano (Engineering Supervisor) · Purno Budi Kiswanto (Engineering Manager) · Happy Monda Pintauli (QA Manager) |

## Tujuan

Petunjuk pengoperasian dan perawatan sistem udara tekan berikut peralatan pendukungnya agar sesuai standar PT EBI: Ingersoll Rand IRN37 OF-A10, Atlas Copco ZT37KW, Refrigerator Dryer, Desiccant Dryer, dan Atlas Copco Dryer CD 130+ - 70.
(source: SOP-EBI-EN-013 ...pdf Rev.04)

## Peralatan yang Dicakup

| Peralatan | Keterangan |
|---|---|
| Ingersoll Rand IRN37 OF-A10 | Compressor variable speed (Unit 1 & 2) |
| Atlas Copco ZT37KW | Compressor variable speed (Unit 3) |
| Refrigerator Dryer D780IN-A | 2 unit, dijalankan bergantian tiap 1 hari |
| Heatless Desiccant Dryer D500IL | Unit utama |
| Atlas Copco Dryer CD 130+ - 70 | Heatless desiccant dryer — sebagai **cadangan** (backup); digunakan jika D500IL mengalami kendala |

## Klasifikasi Udara Tekan

| Tipe | Penggunaan | Standar |
|---|---|---|
| **Kontak Produk** | Kontak langsung dengan produk steril (mis. proses autoclave) | ISO 14644:1 (partikel); ISO 8573-1:2010 (uap air & oli) |
| **Non-Kontak Produk** | Tidak kontak langsung dengan produk (mis. pneumatik) | ISO 8573-1:2010 |

Klasifikasi lengkap sesuai Point of Use (POU) lihat lampiran `SOP/EBI/EN-004-L01` dan `SOP/EBI/EN-004-L02`.

## Operasional

- 3 unit compressor: **Udara Tekan 1** (IR IRN37), **Udara Tekan 2** (IR IRN37), **Udara Tekan 3** (Atlas Copco ZT37KW).
- Compressor dan Refrigerator Dryer dijalankan **bergantian setiap 1 hari**.
- **Akses setting/parameter mesin** hanya bisa dilakukan oleh **Supervisor**; Operator/Teknisi hanya bisa memantau dan melaporkan penyimpangan ke formulir.

### Prosedur Start-Up Compressor (IR37-OF / Atlas Copco ZT37KW)

1. Pastikan katup-katup pada jalur pipa udara tekan telah **terbuka**.
2. Pastikan kompressor dalam keadaan **Unloading**.
3. Cek semua parameter dan indikator pada display — pastikan sesuai standar.
4. Jika display menampilkan "**Ready To Start**" → tekan tombol **Start** (hijau).

### Prosedur Shut-Down Compressor

- Normal: tekan **Unloaded Stop** hingga Sump Pressure < **2,9 bar** → tekan **Stop** (merah).
- Darurat: tekan **Emergency Stop**.

### Prosedur Start-Up Refrigerant Air Dryer D780IN-A

1. Pastikan katup inlet dan outlet terbuka.
2. Putar saklar main power ke posisi **On**.
3. Cek semua parameter dan indikator.
4. Tekan tombol **Start/Stop** (merah) satu kali pada panel P&ID.

### Prosedur Start-Up Heatless Desiccant Dryer (D500IL / Atlas Copco CD 130+ - 70)

1. Pastikan katup inlet dan outlet terbuka.
2. Putar saklar utama ke posisi **I (ON)**.
3. Cek semua parameter dan indikator.
4. Tekan tombol **nomor 1 (ON)** pada panel display. Untuk mematikan, tekan **nomor 7 (OFF)**.

## Parameter Pemantauan Harian

### IR37-OF — Monitoring Parameters

| Parameter | Standar / Limit |
|---|---|
| Package discharge pressure | 7–10 bar |
| Inlet vacuum pressure | alert ≤ 0,05 bar; action ≤ 0,07 bar |
| 1st discharge temperature | 105–250 °C |
| 2nd stage inlet pressure | alert ≤ 3,0 bar; action ≤ 3,2 bar |
| 2nd stage discharge pressure | 7–10 bar |
| 2nd stage discharge temperature | 105–280 °C |
| Oil Filter Drop pressure | alert ≤ 3,0 bar; action ≤ 3,2 bar |
| Oil level | terlihat pada sight glass (tambah jika tidak terlihat) |
| Tank non-contact product pressure | 7–9 bar |
| Tank contact product pressure | 7–9 bar |

### Atlas Copco ZT37KW — Monitoring Parameters

| Parameter | Standar / Limit |
|---|---|
| Oil level | terlihat pada sight glass |
| Tank non-contact product pressure | 7–9 bar |
| Tank contact product pressure | 7–9 bar |
| Oil pressure | 1,5–2,5 bar |
| Intercooler pressure | 1,8–2,6 bar |
| Element 1 outlet temperature | ≤ 230 °C |
| Element 2 outlet temperature | ≤ 230 °C |
| Element 2 inlet temperature | 30–55 °C |
| Compressor outlet temperature | 25–40 °C |
| Compressor outlet pressure | 7–10 bar |

### Refrigerant Air Dryer D780IN-A — Monitoring Parameters

| Parameter | Standar |
|---|---|
| Pressure Dew Point (unit 1 & 2) | ≤ 4 °C |
| Econometer Pre Filter FA 800 IG | Hijau = OK; kuning = siapkan spare; merah = ganti filter |
| Econometer After Filter FA 800 IH | Hijau = OK; kuning = siapkan spare; merah = ganti filter |
| Katup drain otomatis | Tekan tombol tes — harus mengeluarkan tekanan udara |

### Heatless Desiccant Dryer D500IL — Monitoring Parameters

| Parameter | Standar |
|---|---|
| Pressure Dew Point | -65 s/d -90 °C; alert limit -67 °C → order Desiccant Dryer |
| Econometer After Filter FA 800 IH | Kuning = siapkan spare; merah = ganti filter |
| Blue moisture indicator | Harus menunjukkan warna **biru** |
| Katup drain otomatis | Cek apakah bekerja normal |

### Atlas Copco Dryer CD 130+ - 70 — Monitoring Parameters

| Parameter | Standar |
|---|---|
| Pressure Dew Point | -65 s/d -90 °C; alert limit -67 °C |
| Pre filter UD 140+ | Kuning = OK; oranye = alert; merah = action |
| After filter DDp+ dan PDP 110+ | 0–290 mbar; alert 300 mbar; action 350 mbar |
| Katup drain otomatis | Cek apakah bekerja normal |

## Jadwal Perawatan Berkala

### L2 — 3 Bulanan (Compressor IR37-OF dan Atlas Copco ZT37KW)

- Periksa semua katup dan instalasi pipa dari kebocoran di area: CUB, mezzanine produksi lantai 1 & 2, mezzanine QC, mezzanine Animal House.
- Cek Separator Element differential pressure (ganti jika = 0 atau > 1 bar).
- Cek dan bersihkan: filter udara, Scavenge Screen, Cooler Cores, Moisture Separator, Motor Cowl.
- Cek Pressure Relief Valve dan sensor suhu/tekanan tinggi dan rendah.
- Cek koneksi kelistrikan (MCB, kontaktor); kencangkan jika longgar.
- Cek kipas pendingin board VSD.

### L2 — 3 Bulanan (Refrigerant Air Dryer D780IN-A)

- Bersihkan kondensor dengan udara bertekanan.
- Bersihkan saluran buangan pipa kondensat.
- Cek arus listrik pada ketiga kawat phasa.
- Cek tekanan refrigerant di pipa suction saat dryer beroperasi.

### L2 — 3 Bulanan (Heatless Desiccant Dryer D500IL dan Atlas Copco CD 130+ - 70)

- Cek pressure gauge selama purging terhadap kemungkinan tekanan balik.
- Cek arus listrik pada ketiga kawat phasa.
- Cek semua katup dari kebocoran.
- Cek semua komponen kelistrikan.

### L3 — 6 Bulanan (Compressor)

- Ganti filter udara setiap **4.000 jam operasi**.
- Cek dan bersihkan selang-selang setiap 4.000 jam.
- Lumasi Motor Fan dengan greasing setiap 4.000 jam.

### L4 — Tahunan (Compressor)

- Ganti Oli Coolant setiap **8.000 jam operasi**.
- Ganti Filter Oli setiap 8.000 jam.
- Ganti Filter Udara.
- Cleaning Separate Element.

### L4 — Tahunan (Refrigerant Air Dryer D780IN-A)

- Cek fan kondensor.
- Ganti Pre Filter Econometer 0,1 Micron FA 800 IG (no 1 & 2).
- Ganti Econometer After Filter 0,01 Micron FA 800 IH.

## Tanggung Jawab

| Peran | Tanggung Jawab |
|---|---|
| Teknisi Engineering | Perawatan harian (bersihkan badan mesin, ruangan), operasikan sesuai kebutuhan, pemantauan harian, perawatan berkala |
| Supervisor Engineering | Jadwal perawatan berkala; pastikan pelaksanaan; kalibrasi alat ukur; koordinasi laporan kerusakan ke Manager |
| Manager Engineering | Tentukan spare parts pengganti; putuskan penggantian/modifikasi/change control |

## Petunjuk Umum

- Semua alat ukur (pressure gauge, thermometer, voltmeter, amperemeter) harus **dikalibrasi secara berkala**.
- Alat ukur rusak harus diberi **penandaan yang jelas**.
- APD wajib: **penutup telinga (earmuff)**.
- Penggantian spare part harus sesuai spesifikasi dan fungsi.
- Perubahan major pada sistem udara tekan harus menggunakan **formulir change control** dan disetujui seluruh manajer.
- Semua kegiatan perbaikan/perawatan dicatat pada form `SOP/EBI/EN-013-F03`.

## Alat dan Bahan

**Alat**: Kain lap/duster, tang ampere (clamp meter), tang (pliers), obeng, kunci set (tool box)
**Bahan**: Pelumas/gemuk (lubricant/grease)

## Related pages

- [[compressed-air-system]]
- [[engineering-responsibilities]]
- [[sop-en-004-perawatan-mesin]]
