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
- `perawatan-gedung-infrastruktur.md`
- `penanganan-lampu-distribusi-listrik.md`
- `preventive-maintenance-mesin.md`
- `pengelolaan-suku-cadang.md`
- `operasi-perawatan-udara-tekan.md`
- `penanganan-perbaikan-mesin.md`
- `sop-en-015-pure-water-form.md`
- `operasi-perawatan-hvac.md`

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
- `preventive-maintenance-mesin.md` — ditambahkan PDF Copy sebagai sumber, dicatat sebagai draft review dengan 19 anotasi reviewer
- `pengelolaan-suku-cadang.md` — ditambahkan PDF sebagai sumber; kode lokasi suku cadang (`R. part – R1 . A/B/C`) dan jadwal Senin/Rabu/Jumat
- `operasi-perawatan-udara-tekan.md` — **upgrade besar**: revisi ke Rev.04, prosedur start/stop tiap equipment, parameter monitoring numerik per mesin, jadwal L2/L3/L4
- `penanganan-perbaikan-mesin.md` — riwayat revisi; prosedur pemindahan mesin dari area GMP; uji coba 15 menit; label Engineering/Vendor; tabel 5 formulir (F01B–F05B)
- `sop-en-015-pure-water-form.md` — **upgrade besar**: 21 parameter monitoring dengan nilai standar dan alert/action limits; frekuensi 6x/hari (3 shift)
- `compressed-air-system.md` — parameter pemantauan kunci per equipment; interval perawatan L2/L3/L4
- `spare-parts-management.md` — seksi Sistem Kode Lokasi dan Jadwal Pemantauan Inventori
- `index.md` — 5 sumber PDF baru ditambahkan ke tabel Dokumen Raw

**Catatan:**
- `SOP-EBI-EN-013 ...pdf` Rev.04 lebih lengkap dari versi DOC lama: parameter monitoring numerik detail dan prosedur start/stop eksplisit per equipment.
- `SOP-EBI-EN-015-F01H ...pdf` (61 hal.) mengungkap isi logbook sesungguhnya — DOCX hanya berisi kolom "Date:" kosong.
- `SOP-EBI-EN-004.02 ... - Copy.pdf` adalah draft dalam review — dicatat sebagai demikian, bukan sumber utama.

---

## 2026-04-21 — Ekstraksi Metadata & Restrukturisasi ke wiki/engineering/

**Operasi:**
- Baca semua 11 PDF di `raw/` menggunakan pdfplumber
- Ekstrak per file: judul (ID+EN), SOP number, revision, effective date, prepared/reviewed/approved by (nama + jabatan)
- Buat direktori `wiki/engineering/` sebagai lokasi canonical semua halaman SOP
- Buat 11 halaman baru di `wiki/engineering/` (tidak ada .md yang cocok di wiki/engineering/ sebelumnya — direktori kosong)
- Update `wiki/index.md`: semua referensi source pages diubah ke `engineering/` path; Dokumen Raw diperbarui dengan 11 PDF aktual

**Halaman yang dibuat (11 halaman di wiki/engineering/):**
- `penanganan-lampu-distribusi-listrik.md` ← SOP/EBI/EN-001 Rev.02
- `perawatan-gedung-infrastruktur.md` ← SOP/EBI/EN-003 Rev.03
- `preventive-maintenance-mesin.md` ← SOP/EBI/EN-004 Rev.02
- `pengelolaan-suku-cadang.md` ← SOP/EBI/EN-005 Rev.03
- `operasi-perawatan-udara-tekan.md` ← SOP/EBI/EN-013 Rev.04
- `penanganan-perbaikan-mesin.md` ← SOP/EBI/EN-014 Rev.01
- `operasi-perawatan-pengolahan-air.md` ← SOP/EBI/EN-015 Rev.08 (109 hal.)
- `operasi-perawatan-hvac.md` ← SOP/EBI/EN-016 Rev.07
- `perawatan-mesin-filling-bosch.md` ← SOP/EBI/EN-024 Rev.04 *(baru)*
- `perawatan-mesin-filling-tofflon.md` ← SOP/EBI/EN-044 Rev.01 *(baru)*
- `operasi-perawatan-bms-ems.md` ← SOP/EBI/EN-055 Rev.00 *(baru)*

**Catatan:**
- Effective Date kosong di semua PDF (kolom tidak diisi)
- wiki/ root tidak ada .md selain index.md dan log.md — tidak ada file yang perlu dipindahkan
- SOP-EBI-EN-015 adalah dokumen terpanjang (109 hal., Rev.08)
- SOP-EBI-EN-055 adalah dokumen paling baru (Rev.00, approved oleh Project Leader Bhirawa Septariyanto)
- PDF tool: pdfplumber (pdftoppm tidak tersedia di environment ini)

---

## 2026-04-16 — Update: Ekstraksi Knowledge dari Raw SOP Docx

**Sumber yang dibaca ulang:**
1. `wiki/SOP-EBI-EN-003.03 Perawatan Gedung dan Infrastruktur.md` (hasil konversi docx)
2. `wiki/SOP-EBI-EN-014.01 Penanganan Perbaikan Terhadap Semua Mesin-mesin...md` (hasil konversi docx)

**Analisis gap:**
- SOP-003: `perawatan-gedung-infrastruktur.md` hanya berisi metadata dokumen; prosedur aktual, tanggung jawab, alat & bahan belum tercermin.
- SOP-014.01: `penanganan-perbaikan-mesin.md` sudah lengkap — tidak ada gap signifikan.

**Halaman yang diperbarui (2 halaman):**
- `perawatan-gedung-infrastruktur.md` — ditambahkan: Tanggung Jawab (5 peran termasuk *Pengguna Area/Ruangan* baru di Rev.03), Petunjuk Umum (termasuk ISO 14001), Alat & Bahan, Prosedur lengkap (inspeksi, perbaikan cepat/lama, PJE, pembersihan lantai/mesin/plafon)
- `building-maintenance-overview.md` — ditambahkan: tabel Tanggung Jawab 5 peran, seksi Kepatuhan ISO 14001

---

## 2026-04-22 — Buat Concept Pages, Synthesis Pages, dan Ingest 3 Dokumen QA

### Concept Pages (7 halaman baru di wiki/engineering/)

- `hvac-system.md` — komponen AHU/FCU/chiller, 6 parameter GMP, integrasi BMS/EMS, jadwal perawatan
- `compressed-air-system.md` — klasifikasi kontak/non-kontak produk, 3 kompressor + 4 dryer, jadwal L2/L3/L4
- `electrical-system.md` — alur distribusi PLN→MDP→SDP, standar PUIL 2011 + Permenaker 12/2015, grounding
- `engineering-responsibilities.md` — matriks lengkap 3 peran utama + peran tambahan (administrasi suku cadang, housekeeping)
- `maintenance-types.md` — 4 jenis PM/CM/BM/AM, tabel perbandingan, formulir F01B/F02B
- `pje-permintaan-jasa-engineering.md` — alur PJE, kapan diperlukan vs tidak, integrasi dengan F03B
- `spare-parts-management.md` — critical vs non-critical, Part Code, kode lokasi R1.A/B/C, jadwal Sen/Rab/Jum

### Synthesis Pages (3 halaman baru di wiki/engineering/)

- `synthesis-emergency-shutdown.md` — prosedur shutdown HVAC, udara tekan, listrik, mesin produksi; urutan; label; eskalasi
- `synthesis-onboarding-teknisi.md` — 4 fase orientasi, checklist 10 item, formulir wajib, APD per area
- `synthesis-daily-monitoring.md` — checklist harian 5 sistem; alur deviasi; tabel formulir per sistem

### Ingest QA Dokumen (3 halaman baru di wiki/qa/)

**Sumber yang diproses:**
1. `SOP-EBI-QA-004.04 SOP Change Control (1).pdf` — 40 halaman, Rev.04
2. `SOP-EBI-QA-008.08 Penanganan Penyimpangan.pdf` — 64 halaman, Rev.08
3. `SOP-EBI-QA-035.06 Penanganan dan Manajemen CAPA.pdf` — 46 halaman, Rev.06

**Halaman yang dibuat:**
- `wiki/qa/sop-qa-004-change-control.md` — CC: 3 kategori (Kritikal/Mayor/Minor), 9 peran, alur CC, lampiran L05/L07
- `wiki/qa/sop-qa-008-deviasi.md` — Deviasi: 3 klasifikasi event, alur penanganan, tren analisa periodik, form L04
- `wiki/qa/sop-qa-035-capa.md` — CAPA: inisiasi dari 9+ sumber quality event, effectiveness check, tren analisa tahunan

**index.md diperbarui:**
- Concept pages diupdate ke path `engineering/`
- Ditambahkan seksi Synthesis Pages (Engineering)
- Ditambahkan seksi QA Pages

**Catatan:**
- Semua 3 QA PDF: Effective Date kosong (kolom tidak diisi)
- QA-008 Rev.08 adalah revisi tertinggi di antara 3 dokumen — sistem deviasi paling mature
- QA-004 melibatkan CRB (Cross Review Board) dan QMS berbasis SharePoint
- QA-035 melibatkan 8 reviewer lintas departemen — CAPA berdampak ke seluruh PT EBI

---
