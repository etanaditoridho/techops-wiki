---
title: "📚 Concept: Manajemen Suku Cadang Engineering"
status: verified
folder: ENGINEERING
owner: ""
version: 2
review_date: 
confidence: 
tags:
  - Pje Permintaan Jasa Engineering
  - Penanganan Perbaikan Mesin
  - Pengelolaan Suku Cadang
  - Maintenance Types
  - Engineering Responsibilities
  - SOP EN-005
notion_id: 34c664a8-3e24-817f-a21d-d33a0f98537c
synced: 2026-04-29
---

## LLM Summary
- System: Manajemen Suku Cadang Engineering
- Equipment: Critical part, non-critical part, part code, stok suku cadang
- Symptoms: []
- Keywords: [suku cadang, spare part, critical part, part code, stok, inventori]
- Severity: N/A
**Summary**: Klasifikasi, identifikasi, penyimpanan, dan pengendalian stok suku cadang Engineering PT EBI — mencakup perbedaan critical vs non-critical, sistem Part Code, dan prosedur inventori.
**Sources**: `SOP-EBI-EN-005.03 Penyimpanan Dan Pengolahan Suku Cadang_OFC.pdf`
**Last updated**: 2026-04-22
## Klasifikasi Suku Cadang
| Jenis | Definisi | Contoh |
|---|---|---|
| **Critical Part** | Dampak langsung ke kualitas produk ATAU lead time pengiriman panjang (sulit didapat cepat) | HEPA filter, seal mesin filling, komponen chiller |
| **Non-Critical Part (General Part)** | Tidak berkaitan langsung ke kualitas produk; umumnya tersedia di pasar lokal; dapat digunakan untuk lebih dari satu mesin | Baut, kabel, lampu, filter umum |
**Aturan klasifikasi**: ditentukan oleh **Manager Engineering**.
## Sistem Part Code
Setiap suku cadang diberikan **Part Code** unik:
- Dibuat oleh administrasi suku cadang
- Dimasukkan ke **Database Inventory**
- Memudahkan pengenalan, pencarian, dan tracking stok
## Sistem Kode Lokasi Penyimpanan
Format lokasi: `R. part – R1 . A/B/C`
- `R. part` = Ruang spare parts
- `R1` = Rak nomor 1 (dst.)
- `A/B/C` = Kolom/posisi di rak
## Prosedur Pengelolaan
### Penerimaan Suku Cadang
1. Verifikasi kesesuaian dengan Purchase Order
1. Periksa kondisi fisik dan spesifikasi
1. Daftarkan ke Database Inventory dengan Part Code
1. Tempatkan di lokasi penyimpanan sesuai kode lokasi
### Pengeluaran / Penggunaan
1. Teknisi meminta suku cadang dengan F03B (Formulir Permintaan Barang)
1. Administrasi keluarkan dan catat pengeluaran
1. Penggantian harus sesuai spesifikasi asli
1. Perubahan spesifikasi spare parts **kritikal** wajib membuat **change control**
### Pemantauan Stok
- Jadwal pemantauan: **Senin / Rabu / Jumat**
- Administrasi memverifikasi stok fisik vs database
- Stok minimum critical parts harus selalu terpenuhi
### Pemesanan Ulang
- Trigger pemesanan: stok mencapai batas minimum (reorder point)
- Inisiasi oleh administrasi suku cadang
- Disetujui Supervisor/Manager Engineering
- Lead time pemesanan diperhitungkan terutama untuk critical parts
## Aturan Keselamatan
- Gunakan **APD** saat memindahkan suku cadang ke tempat lebih tinggi atau menggunakan tangga
- Hanya personel berkepentingan yang boleh berada di ruang spare parts
- Suku cadang berat harus diangkat dengan alat bantu yang memadai
## Tanggung Jawab
| Peran | Tanggung Jawab |
|---|---|
| Manager Engineering | Tentukan klasifikasi Critical vs Non-Critical; setujui change control spesifikasi |
| Supervisor Engineering | Kontrol dan pastikan pelaksanaan SOP; evaluasi kebutuhan stok |
| Administrasi Suku Cadang | Kelola Part Code dan Database Inventory; pantau stok Senin/Rabu/Jumat; proses penerimaan dan pengeluaran |
| Teknisi Engineering | Berikan masukan kebutuhan spare parts baru; gunakan spare parts sesuai spesifikasi |
## Hubungan dengan Change Control
Setiap kali spesifikasi spare parts **kritikal** diubah (berbeda dari spesifikasi asli):
- Wajib membuat dokumen **change control**
- Dikoordinasikan oleh Manager Engineering
- Melibatkan QA untuk validasi dampak terhadap kualitas produk
## Related pages
- [[pengelolaan-suku-cadang]]
- [[maintenance-types]]
- [[pje-permintaan-jasa-engineering]]
- [[engineering-responsibilities]]
- [[penanganan-perbaikan-mesin]]