# Sistem Kelistrikan (Electrical System)

**Summary**: Konsep sistem kelistrikan di PT EBI — distribusi listrik dari PLN, panel listrik, lampu penerangan, transformator tegangan menengah, dan prosedur perawatannya.

**Sources**: `SOP-EBI-EN-001.02 Penanganan dan Perawatan Terhadap Lampu Penerangan dan Sistem Penyaluran Tenaga Listrik.pdf`

**Last updated**: 2026-04-14

---

## Komponen Sistem Kelistrikan PT EBI

| Komponen | Fungsi |
|---|---|
| **Jalur distribusi PLN** | Sumber listrik utama dari jaringan nasional (PLN) ke panel tegangan menengah |
| **Transformator Tegangan Menengah** | Menurunkan tegangan menengah ke tegangan rendah untuk distribusi internal |
| **Panel Listrik (LP)** | Mendistribusikan listrik ke semua peralatan dan area |
| **Sistem Penerangan** | Lampu di area produksi, QC, gudang, kantor, dan halaman/jalan |
| **Sistem Grounding** | Keamanan listrik — perlindungan dari arus bocor |
| **Generator Set** | Backup otomatis saat terjadi pemadaman listrik (lihat SOP/EBI/EN-002) |

(source: SOP-EBI-EN-001.02 ...pdf)

## Standar yang Berlaku

| Standar | Keterangan |
|---|---|
| IEC | International Electrotechnical Commission |
| NEC | National Electrical Code |
| IEEE | Institute of Electrical and Electronics Engineers |
| **Permenaker No. 12 Tahun 2015** | Peraturan K3 Listrik Indonesia |
| **PUIL 2011** | Persyaratan Umum Instalasi Listrik Indonesia |

## Jadwal Perawatan

### Lampu Penerangan

| Kode | Frekuensi | Kegiatan |
|---|---|---|
| L2 | 3 bulan | Bersihkan kaca pelindung lampu; cek silicon seal ruang steril |
| L3 | 6 bulan | Periksa sambungan kabel; periksa saklar; periksa input line trafo |

### Panel Listrik

| Kode | Frekuensi | Kegiatan |
|---|---|---|
| L2 | 3 bulan | Cek sambungan terminal dan konektor; cek suhu kontak point (maks 65°C via thermal imager); cek kondisi bodi panel |
| L4 | 1 tahun | Hitung unbalance tiga fasa (R, S, T) menggunakan Vf = √3 · VL-N |

## Ketentuan Penting

- **Kabel rol dilarang** digunakan untuk equipment.
- **MCB/Overload protection** harus sesuai spesifikasi arus beban peralatan.
- **Grounding** yang memenuhi syarat: ≤ 7 Ω (umum), ≤ 1 Ω (elektronik) — lihat [[sop-en-014-perbaikan-mesin]].
- **Pemadaman listrik**: genset otomatis memback-up via SOP/EBI/EN-002.
- Ruang lampu steril: perlu cek **silicon seal** secara berkala.

## Keselamatan Listrik

- Harus menjaga agar tidak terjadi sentuhan tidak sengaja dengan bagian bertegangan.
- Bahaya listrik di area kerja harus dihindari secara proaktif.
- Teknisi yang menangani listrik harus memiliki kualifikasi K3 Listrik.

## Related pages

- [[sop-en-001-lampu-listrik]]
- [[hvac-system]]
- [[engineering-responsibilities]]
