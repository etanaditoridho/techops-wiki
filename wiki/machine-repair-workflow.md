# Alur Perbaikan Mesin (Machine Repair Workflow)

**Summary**: Alur kerja lengkap perbaikan mesin di PT EBI — mulai dari commissioning mesin baru, pelaporan breakdown, proses PJE, hingga pencatatan di buku riwayat mesin.

**Sources**: `SOP-EBI-EN-014.01 Penanganan Perbaikan Terhadap Semua Mesin-mesin ...docx`, `SOP-EBI-EN-014 ...DOC`

**Last updated**: 2026-04-14

---

## 1. Commissioning Mesin Baru

Sebelum mesin baru dioperasikan secara resmi:

1. **Verifikasi penerimaan**: Cek jumlah mesin dan komponen vs Packing List/surat jalan.
2. **Pelajari dokumentasi**: Baca buku instalasi dan buku pengoperasian.
3. **Siapkan area test run** yang memadai.
4. **Verifikasi grounding**: ≤ 7 Ω (umum), ≤ 1 Ω (elektronik).
5. **Gunakan connector** yang sesuai dengan female connector-nya.
6. **Siapkan APAR** tipe CO2/Dry Powder (kelas B dan C) di area uji coba.
7. **Test run dan catat**: arus listrik, RPM, temperatur motor, voltage, pressure gauge, nomor serial, tahun pembuatan → formulir data mesin baru.
8. **Serah terima** dengan kepala bagian/supervisor terkait.
(source: SOP-EBI-EN-014.01 ...docx)

## 2. Pelaporan Breakdown oleh Operator

Saat mesin rusak/gagal beroperasi:

1. Operator **menghentikan penggunaan** mesin.
2. Operator **melaporkan** ke Engineering via **formulir PJE** `SOP/EBI/EN-014-F02`.
3. Engineering menerima PJE dan menugaskan teknisi.

Lihat juga: [[pje-permintaan-jasa-engineering]]

## 3. Pelaksanaan Perbaikan oleh Engineering

1. Teknisi menerima dan menindaklanjuti PJE.
2. Jika memerlukan material → buat **formulir permintaan barang**.
3. Lakukan perbaikan.
4. Jika melibatkan **critical parts** (pompa, motor, dll) → mesin harus **dikualifikasi ulang**.
5. Jika ada perubahan yang memengaruhi kinerja/mutu produk → gunakan **Change Control Form** (disetujui semua Manager dan Plant Manager).
6. Catat kegiatan perbaikan di **buku/kartu riwayat mesin**.

## 4. Pekerjaan Vendor

- Jika perbaikan dilimpahkan ke vendor, Engineering menyiapkan **laporan pekerjaan vendor**.
- Label mesin harus dipasang: "Sedang Diperbaiki oleh Vendor".
- Engineering tetap mengawasi dan mendokumentasikan pekerjaan vendor.

## 5. Label Mesin

| Status | Label |
|---|---|
| Diperbaiki oleh Engineering | Label: "Sedang Diperbaiki oleh Engineering" |
| Diperbaiki oleh Vendor | Label: "Sedang Diperbaiki oleh Vendor" |

## Ketentuan Khusus: Pickling dan Passivating

Untuk peralatan dari **stainless steel** atau wadah kontak produk yang telah dilakukan **pengelasan ulang** → wajib dilakukan **Pickling dan Passivating** sebelum digunakan kembali.

## Related pages

- [[sop-en-014-perbaikan-mesin]]
- [[pje-permintaan-jasa-engineering]]
- [[maintenance-types]]
- [[spare-parts-management]]
- [[engineering-responsibilities]]
