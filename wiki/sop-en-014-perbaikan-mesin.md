# SOP/EBI/EN-014 — Penanganan dan Perbaikan Mesin

**Summary**: Source summary untuk SOP penanganan dan perbaikan semua mesin di PT EBI, mencakup commissioning mesin baru, pelaporan breakdown, proses PJE, dan pekerjaan vendor.

**Sources**:
- `SOP-EBI-EN-014 Penanganan Dan Perbaikan Terhadap Semua Mesin-Mesin Di Pt. Etana Biotechnologies Indonesia.DOC` (versi lama)
- `SOP-EBI-EN-014.01 Penanganan Perbaikan Terhadap Semua Mesin-mesin di PT Etana Biotechnologies Indonesia.docx` (Rev.01)
- `SOP-EBI-EN-014 Penanganan Dan Perbaikan Terhadap Semua Mesin-Mesin Di Pt. Etana Biotechnologies Indonesia.pdf` (Rev.01 — dikonfirmasi via PDF)

**Last updated**: 2026-04-14

---

## Identitas Dokumen

| Field | Value |
|---|---|
| SOP No. | SOP/EBI/EN-014 |
| Revision | **01** (dikonfirmasi via PDF) |
| Signatories | Wendi Rukmansyah (Non Utility Engineering SPV) · Purno Budi Kiswanto (Engineering Manager) · Happy Monda Pintauli (QA Manager) |

### Riwayat Revisi

| Tanggal | No. Change Control | Revisi | Alasan |
|---|---|---|---|
| 10 Apr 2019 | N/A | 00 | Dokumen baru |
| — | N/A | 01 | Perpanjangan tanggal berlaku SOP |

### Distribusi

Engineering · Produksi · QC (Pengawasan Mutu) · QA (Pemastian Mutu)

## Tujuan

1. Memastikan mesin yang diperoleh/dibeli/dipindahkan (baru maupun bekas) dapat digunakan sesuai fungsinya.
2. Prosedur pelaporan breakdown ke Engineering oleh operator/pemegang alat.
3. Prosedur pengajuan perbaikan mesin (PJE).
4. Petunjuk laporan pekerjaan vendor.
5. Petunjuk label mesin sedang diperbaiki oleh Engineering atau vendor.
(source: SOP-EBI-EN-014.01 ...docx)

## Ruang Lingkup

Departemen Engineering untuk penanganan dan perbaikan mesin:
- Utility, Produksi, Warehouse, QA (Pemastian Mutu), QC (Pengawasan Mutu)

## Prosedur Mesin Baru

Sebelum mengoperasikan mesin baru, lakukan pemeriksaan:

1. Cek jumlah mesin dan komponen sesuai **Packing List / surat jalan**.
2. Baca buku instalasi dan buku pengoperasian.
3. Siapkan tempat yang cukup untuk test run.
4. Pastikan **grounding** memenuhi syarat: ≤ 7 Ω (umum), ≤ 1 Ω (peralatan elektronik).
5. Gunakan connector power source yang sesuai female connector-nya.
6. Siapkan data spesifikasi teknis mesin.
7. Pastikan semua alat ukur telah terkalibrasi.
8. Siapkan **APAR** (tipe CO2 atau Dry Powder, kelas B dan C) di sekitar area uji coba.
9. Catat: arus listrik, RPM, temperatur motor, voltage, pressure gauge, inverter, nomor serial, tahun pembuatan di **formulir percobaan data mesin baru**.
10. Setelah selesai uji coba, lakukan **serah terima** dengan kepala bagian/supervisor terkait.

## Syarat Perbaikan Mesin

Perbaikan dilakukan apabila:
- Diperlukan penggantian **critical parts** (pompa, motor, dll) → mesin harus dikualifikasi ulang.
- Terdapat perubahan yang mempengaruhi kinerja mesin dan mutu produk → gunakan **Change Control Form** (disetujui semua Manager dan Plant Manager).

## Penting: Pickling dan Passivating

Untuk peralatan baru dari material **stainless steel** atau wadah yang kontak produk yang telah dilakukan **pengelasan ulang** → wajib dilakukan **Pickling dan Passivating**.

## Prosedur Pemindahan Mesin ke/dari Area Produksi

Jika mesin harus dibawa keluar dari ruang produksi untuk diperbaiki:
1. Tentukan berat mesin dan pilih alat pengangkut yang sesuai kapasitasnya.
2. Tentukan jumlah petugas sesuai berat mesin.
3. Personel yang masuk ke kelas ruangan **CNC, D, C, B, A** harus mengikuti SOP/EBI/PD-004 (Prosedur Alur Personil, Material, Produk Jadi, dan Limbah di Area Produksi).
4. Setelah selesai, bersihkan mesin dan tutup dengan **cover plastik**.
5. Kembalikan mesin ke ruang antara area produksi.
6. Lakukan **uji coba 15 menit** dengan observasi visual dan audible.
7. Catat hasil perbaikan di **Kartu Riwayat Mesin** (SOP/EBI/EN-004).
8. Lakukan serah terima dengan Supervisor Produksi.

## Label Mesin

- **Label Engineering**: ditempel pada mesin yang sedang dalam PM atau breakdown repair. Berisi: nama mesin, lokasi, paraf pelaksana. Tujuan: mencegah mesin dioperasikan operator lain.
- **Label Vendor**: ditempel jika mesin/alat sedang diperbaiki oleh vendor/supplier.

Form: `SOP/EBI/EN-014-F04B` (label Engineering), `SOP/EBI/EN-014-F05B` (label Vendor).

## PJE (Permintaan Jasa Engineering)

- Departemen lain yang membutuhkan perbaikan mesin menggunakan **formulir PJE** `SOP/EBI/EN-014-F02B`.
- Teknisi membuat formulir permintaan barang jika PJE memerlukan material.
- Semua kegiatan perbaikan yang selesai dicatat di **buku riwayat mesin**.

## Lampiran / Formulir

| Nomor Form | Nama |
|---|---|
| SOP/EBI/EN-014-L01B | Flow Chart Perbaikan Mesin Produksi |
| SOP/EBI/EN-014-F01B | Formulir Pencatatan Data Hasil Percobaan Mesin Baru |
| SOP/EBI/EN-014-F02B | Formulir Permintaan Jasa Engineering (PJE) |
| SOP/EBI/EN-014-F03B | Formulir Laporan Pekerjaan oleh Vendor |
| SOP/EBI/EN-014-F04B | Label Mesin Sedang Diperbaiki oleh Engineering |
| SOP/EBI/EN-014-F05B | Label Mesin Sedang Diperbaiki oleh Vendor |

## Tanggung Jawab

| Peran | Tanggung Jawab |
|---|---|
| Teknisi Engineering | Perbaikan peralatan; catat di kartu riwayat; buat form permintaan barang; selesaikan PJE |
| Supervisor Engineering | Review bulanan kinerja teknisi PM; training ke departemen terkait |
| Manager Engineering | Tentukan spare parts pengganti; putuskan penggantian/modifikasi; review dan pastikan kesesuaian SOP |

## Catatan Sumber Dokumen

| File | Format | Keterangan |
|---|---|---|
| EN-014 ...DOC | Binary DOC (lama) | Versi awal, substansi sama |
| EN-014.01 ...docx | DOCX | Rev.01 — versi terbaru yang aktif |
| EN-014 ...pdf | PDF | Konfirmasi independen Rev.01; form dengan suffix B (F01B, F02B, dst.) |

## Related pages

- [[machine-repair-workflow]]
- [[pje-permintaan-jasa-engineering]]
- [[maintenance-types]]
- [[sop-en-004-perawatan-mesin]]
- [[spare-parts-management]]
- [[engineering-responsibilities]]
