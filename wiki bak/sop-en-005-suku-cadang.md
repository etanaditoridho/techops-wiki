# SOP/EBI/EN-005 — Penyimpanan dan Pengelolaan Suku Cadang

**Summary**: Source summary untuk SOP pengelolaan suku cadang Departemen Engineering PT EBI, mencakup penerimaan, pengkodean, penyimpanan, pemesanan, dan kontrol inventori.

**Sources**:
- `SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.docx`
- `SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.pdf` (sumber utama — lebih lengkap)

**Last updated**: 2026-04-14

---

## Identitas Dokumen

| Field | Value |
|---|---|
| SOP No. | SOP/EBI/EN-005 |
| Revision | 03 |

## Tujuan

Panduan pengelolaan suku cadang agar dapat dipergunakan sebagaimana mestinya dan menjamin stok suku cadang utama.
(source: SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.docx)

## Ruang Lingkup

Mencakup gudang suku cadang di Departemen Engineering.

## Definisi

| Istilah | Definisi |
|---|---|
| **Pengelolaan suku cadang** | Prosedur yang mengatur langkah penerimaan, pemakaian, pemesanan, dan pengontrolan suku cadang |
| **Critical Part** | Suku cadang yang berdampak langsung terhadap kualitas produk dan memiliki waktu pengiriman yang lama |
| **Non-Critical Part (General Part)** | Suku cadang tanpa hubungan langsung ke kualitas produk; dapat diaplikasikan untuk lebih dari satu mesin |

## Prosedur Utama

### Identifikasi dan Pengkodean

1. Suku cadang dibagi menjadi **Critical Part** dan **Non-Critical Part (General Part)**.
2. Setiap suku cadang diberi **Part Code** untuk mempermudah penanganan dan pengenalan.
3. Part Code dibuat oleh petugas/administrasi suku cadang dan dimasukkan ke **Database Inventory**.
4. Saat part baru datang: tambahkan ke database (Part Code, nama part, kategori, satuan, Qty).

### Kontrol Inventori

- Inventori dikontrol menggunakan **sistem program di komputer**.
- **Limit Order Parts** (suku cadang bernilai tinggi/sporadis): pemesanan harus minimalis dan terukur, tidak melebihi alokasi anggaran yang disetujui.
- Kelebihan pesanan dari batas anggaran harus disetujui oleh manajemen.
- Petugas/administrasi suku cadang memantau ketersediaan suku cadang setiap **Senin, Rabu, dan Jumat**.
(source: SOP-EBI-EN-005.03 ...pdf)

### Sistem Kode Lokasi Suku Cadang

Setiap lokasi penempatan suku cadang diberi **kode lokasi** untuk memudahkan pencarian.

**Format kode: `R. part – R[no rak] . [area]`**

Contoh:
- `R. part – R1 . A` → Lokasi: ruang sparepart, rak nomor 1, area A
- `R. part – R1 . B` → Lokasi: ruang sparepart, rak nomor 1, area B
- `R. part – L1 . A` → Lokasi: ruang sparepart, posisi L (rak berbeda), nomor 1, area A

(source: SOP-EBI-EN-005.03 ...pdf)

### Akses Ruang Suku Cadang

- Hanya personel yang berkepentingan yang boleh berada di ruang suku cadang.

### Change Control

- Setiap penggantian spesifikasi **critical spare part** harus membuat **Change Control**.

## Tanggung Jawab

| Peran | Tanggung Jawab |
|---|---|
| Petugas/Administrasi Suku Cadang | Pelaksanaan SOP; penyimpanan; pembuatan Part Code; update database |
| Teknisi Engineering | Memberi masukan jika ada penambahan item suku cadang |
| Supervisor Engineering | Kontrol dan pastikan pelaksanaan SOP |
| Manager Engineering | Evaluasi SOP; tentukan kategori Critical Part dan Non-Critical Part |

## Petunjuk Umum

- Gunakan APD saat memindahkan suku cadang ke tempat yang lebih tinggi.
- Penggantian spare part harus sesuai spesifikasi dan fungsinya.

## Related pages

- [[spare-parts-management]]
- [[sop-en-004-perawatan-mesin]]
- [[sop-en-014-perbaikan-mesin]]
- [[engineering-responsibilities]]
