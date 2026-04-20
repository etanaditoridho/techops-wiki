# Pengelolaan Suku Cadang (Spare Parts Management)

**Summary**: Konsep dan prosedur pengelolaan suku cadang di Departemen Engineering PT EBI, mencakup klasifikasi critical vs non-critical, sistem Part Code, dan kontrol inventori.

**Sources**:
- `SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.docx`
- `SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.pdf`

**Last updated**: 2026-04-14

---

## Klasifikasi Suku Cadang

### Critical Part

- Berdampak **langsung** terhadap kualitas produk.
- Memiliki **waktu pengiriman yang lama**.
- Setiap perubahan spesifikasi critical part harus membuat **Change Control**.
(source: SOP-EBI-EN-005.03 ...docx)

### Non-Critical Part (General Part)

- **Tidak** memiliki hubungan langsung ke kualitas produk.
- Dapat diaplikasikan untuk **lebih dari satu mesin** (cross-functional).
- Pemesanan lebih fleksibel.
(source: SOP-EBI-EN-005.03 ...docx)

## Sistem Part Code

Setiap suku cadang diberi **Part Code** unik untuk mempermudah penanganan dan pengenalan.

- Part Code dibuat oleh **petugas/administrasi suku cadang**.
- Dimasukkan ke **Database Inventory** (berbasis komputer).
- Database mencakup: Part Code, nama part, kategori, satuan, Quantity.

### Saat Part Baru Datang

1. Petugas menyusun Part Code baru.
2. Tambahkan ke Database Inventory lengkap dengan data-datanya.
3. Tempatkan di gudang suku cadang sesuai kategorinya.

## Sistem Kode Lokasi

Setiap posisi penyimpanan suku cadang diberi **kode lokasi** untuk memudahkan pencarian.

**Format: `R. part – R[no rak] . [area]`**

| Bagian kode | Arti |
|---|---|
| `R. part` | Lokasi berada di ruang sparepart |
| `R1` | Rak nomor 1 |
| `A / B / C` | Area di dalam rak |

Contoh: `R. part – R1 . A` = ruang sparepart, rak 1, area A.
(source: SOP-EBI-EN-005.03 ...pdf)

## Jadwal Pemantauan Inventori

Petugas/administrasi suku cadang memantau ketersediaan stok setiap **Senin, Rabu, dan Jumat**.
(source: SOP-EBI-EN-005.03 ...pdf)

## Kontrol Inventori

- Inventori dikontrol menggunakan **sistem program di komputer**.
- **Limit Order Parts** (suku cadang bernilai tinggi/sporadis):
  - Pemesanan harus minimalis dan terukur.
  - Tidak boleh melebihi **alokasi anggaran (budget) yang disetujui**.
  - Kelebihan pesanan dari batas anggaran harus disetujui manajemen.

## Aturan Akses dan Penggantian

- Hanya **personel yang berkepentingan** yang boleh berada di ruang suku cadang.
- Penggantian spare part harus sesuai **spesifikasi dan fungsi** aslinya.
- Perubahan spesifikasi **critical spare part** → wajib **Change Control**.

## Tanggung Jawab

| Peran | Tanggung Jawab |
|---|---|
| Petugas/Administrasi Suku Cadang | Pelaksanaan SOP; buat Part Code; update database; penyimpanan |
| Teknisi Engineering | Beri masukan jika ada penambahan item |
| Supervisor Engineering | Kontrol dan pastikan pelaksanaan |
| Manager Engineering | Evaluasi SOP; tentukan kategori Critical vs Non-Critical |

## Related pages

- [[sop-en-005-suku-cadang]]
- [[sop-en-004-perawatan-mesin]]
- [[sop-en-014-perbaikan-mesin]]
- [[maintenance-types]]
