# Wiki Log

Catatan append-only dari semua operasi wiki.

---

## 2026-04-14 — Ingest Awal: Semua Raw Sources

**Sumber yang diproses:**
1. `SOP-EBI-EN-003.03 Perawatan Gedung dan Infrastruktur.pdf` *(sesi sebelumnya)*
2. `SOP-EBI-EN-001.02 Penanganan dan Perawatan Terhadap Lampu Penerangan dan Sistem Penyaluran Tenaga Listrik.pdf`
3. `SOP-EBI-EN-004.02 Perawatan terhadap mesin.docx`
4. `SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.docx`
5. `SOP-EBI-EN-013 Pengoperasian Dan Perawatan Terhadap Sistem Udara Tekan.DOC`
6. `SOP-EBI-EN-014 Penanganan Dan Perbaikan Terhadap Semua Mesin-Mesin ...DOC`
7. `SOP-EBI-EN-014.01 Penanganan Perbaikan Terhadap Semua Mesin-mesin ...docx`
8. `SOP-EBI-EN-015-F01H Pemantauan Harian Terhadap Generator Air Murni ...docx`
9. `SOP-EBI-EN-016.07 Pengoperasian Dan Perawatan Terhadap Sistem Ventilasi ...pdf`

**Halaman yang dibuat (17 halaman):**

*Source pages:*
- `sop-en-003-perawatan-gedung.md`
- `sop-en-001-lampu-listrik.md`
- `sop-en-004-perawatan-mesin.md`
- `sop-en-005-suku-cadang.md`
- `sop-en-013-udara-tekan.md`
- `sop-en-014-perbaikan-mesin.md`
- `sop-en-015-pure-water-form.md`
- `sop-en-016-hvac.md`

*Concept pages:*
- `building-maintenance-overview.md`
- `damage-classification.md`
- `maintenance-types.md`
- `spare-parts-management.md`
- `hvac-system.md`
- `compressed-air-system.md`
- `electrical-system.md`
- `machine-repair-workflow.md`
- `pje-permintaan-jasa-engineering.md`
- `engineering-responsibilities.md`

*Infrastruktur:*
- `index.md` — dibuat
- `log.md` — dibuat

**Catatan:**
- File `SOP-EBI-EN-004.02 - Copy.docx` adalah duplikat dari versi original; tidak dibuatkan halaman terpisah.
- File `~$P-EBI-EN-004.02 ...docx` adalah temp file Word; diabaikan.
- `SOP-EBI-EN-015-F01H` adalah form (bukan prosedur SOP) — dicatat sebagai demikian.
- File DOC lama (SOP-013, SOP-014) berhasil dibaca via Windows COM interface.

---

## 2026-04-14 — Ingest Lanjutan: 5 File PDF Baru

**Sumber yang diproses (sesi 3):**
1. `SOP-EBI-EN-004.02 Perawatan terhadap mesin - Copy.pdf` — 18 halaman, draft review (anotasi FD1–FD19)
2. `SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.pdf` — 17 halaman
3. `SOP-EBI-EN-013 Pengoperasian Dan Perawatan Terhadap Sistem Udara Tekan.pdf` — 37 halaman, **Rev.04**
4. `SOP-EBI-EN-014 Penanganan Dan Perbaikan Terhadap Semua Mesin-Mesin ...pdf` — 19 halaman, Rev.01
5. `SOP-EBI-EN-015-F01H Pemantauan Harian Terhadap Generator Air Murni ...pdf` — 61 halaman logbook

**Halaman yang diperbarui (8 halaman):**
- `sop-en-004-perawatan-mesin.md` — ditambahkan PDF Copy sebagai sumber, dicatat sebagai draft review dengan 19 anotasi reviewer
- `sop-en-005-suku-cadang.md` — ditambahkan PDF sebagai sumber; kode lokasi suku cadang (`R. part – R1 . A/B/C`) dan jadwal Senin/Rabu/Jumat
- `sop-en-013-udara-tekan.md` — **upgrade besar**: revisi ke Rev.04, prosedur start/stop tiap equipment, parameter monitoring numerik per mesin, jadwal L2/L3/L4
- `sop-en-014-perbaikan-mesin.md` — riwayat revisi; prosedur pemindahan mesin dari area GMP; uji coba 15 menit; label Engineering/Vendor; tabel 5 formulir (F01B–F05B)
- `sop-en-015-pure-water-form.md` — **upgrade besar**: 21 parameter monitoring dengan nilai standar dan alert/action limits; frekuensi 6x/hari (3 shift)
- `compressed-air-system.md` — parameter pemantauan kunci per equipment; interval perawatan L2/L3/L4
- `spare-parts-management.md` — seksi Sistem Kode Lokasi dan Jadwal Pemantauan Inventori
- `index.md` — 5 sumber PDF baru ditambahkan ke tabel Dokumen Raw

**Catatan:**
- `SOP-EBI-EN-013 ...pdf` Rev.04 lebih lengkap dari versi DOC lama: parameter monitoring numerik detail dan prosedur start/stop eksplisit per equipment.
- `SOP-EBI-EN-015-F01H ...pdf` (61 hal.) mengungkap isi logbook sesungguhnya — DOCX hanya berisi kolom "Date:" kosong.
- `SOP-EBI-EN-004.02 ... - Copy.pdf` adalah draft dalam review — dicatat sebagai demikian, bukan sumber utama.

---
