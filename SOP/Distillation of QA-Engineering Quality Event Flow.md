---
title: "Distillation of QA-Engineering Quality Event Flow"
status: verified
folder: CROSS-FUNCTIONAL
owner: ""
version: 1
review_date: 
confidence: 
tags:
  - Qa/Manajemen Capa
  - Qa/Manajemen Perubahan
  - Engineering/Engineering Responsibilities
  - Engineering/Permintaan Jasa Engineering
  - Qa/Penanganan Deviasi
  - Engineering/Operasional Sistem Hvac
  - Engineering/Monitoring Bms Ems
  - Engineering/Spare Parts Management
  - SOP EN-004
  - SOP EN-005
notion_id: 371664a8-3e24-811c-a2b9-ea365f44cef0
synced: 2026-07-22
---

﻿---
tags: ["qa-engineering", "change-control", "deviation", "capa", "maintenance", "monitoring"]
**Summary**: Hub lintas departemen yang menghubungkan SOP QA (Change Control, Deviasi, CAPA) dengan SOP Engineering (maintenance, repair, monitoring, spare parts, PJE).
**Sources**: `SOP-EBI-QA-004`, `SOP-EBI-QA-008`, `SOP-EBI-QA-035`, `SOP-EBI-EN-004`, `SOP-EBI-EN-005`, `SOP-EBI-EN-014`, `SOP-EBI-EN-055`
**Department**: Cross-functional
**Last updated**: 2026-05-31
## Kapan Engineering Harus Terhubung ke QA
| Trigger di Engineering | Rujukan Engineering | Rujukan QA | Output yang Diharapkan |
|---|---|---|---|
| Parameter EMS/BMS, HVAC, cold storage, atau utility kritis keluar batas | [[engineering/monitoring-harian-engineering]], [[engineering/monitoring-bms-ems]], [[engineering/operasional-sistem-hvac]] | [[qa/penanganan-deviasi]] | Event dinilai sebagai event comment, non-conformity, atau laporan penyimpangan |
| Perbaikan mesin atau utility berdampak ke proses GMP, produk, area, atau status mesin | [[engineering/penanganan-perbaikan-mesin]], [[engineering/preventive-maintenance-mesin]] | [[qa/penanganan-deviasi]], [[qa/manajemen-capa]] | Deviasi dan/atau CAPA jika akar masalah sistemik |
| Perubahan/modifikasi mesin, utility, parameter operasi, metode kerja, atau spesifikasi spare part kritikal | [[engineering/permintaan-jasa-engineering]], [[engineering/spare-parts-management]] | [[qa/manajemen-perubahan]] | Change Control sebelum perubahan permanen |
| Breakdown berulang, PM tidak efektif, atau spare part kritikal tidak tersedia | [[engineering/maintenance-types]], [[engineering/spare-parts-management]] | [[qa/manajemen-capa]] | CAPA untuk menghilangkan akar masalah dan mencegah pengulangan |
| Pekerjaan PJE berubah menjadi modifikasi berdampak GMP/validasi | [[engineering/permintaan-jasa-engineering]] | [[qa/manajemen-perubahan]], [[qa/penanganan-deviasi]] | PJE tetap berjalan sebagai work request, tetapi keputusan mutu mengikuti QA |
## Alur Keputusan Ringkas
1. Engineering mendeteksi trigger dari monitoring, PM, breakdown, PJE, atau spare part.
1. Bukti awal dicatat: waktu, area, parameter, mesin/sistem, tindakan sementara, PIC, dan dampak awal.
1. Supervisor/Manager Engineering menentukan jalur teknis: monitoring lanjut, perbaikan, PJE, atau modifikasi.
1. QA dilibatkan jika ada dampak GMP, kualitas produk, validasi, fasilitas kritis, sistem kritis, atau keterulangan.
1. Jalur QA dipilih:
- [[qa/manajemen-perubahan]] untuk perubahan terencana.
- [[qa/penanganan-deviasi]] untuk event atau penyimpangan yang sudah terjadi.
- [[qa/manajemen-capa]] untuk akar masalah sistemik atau pencegahan keterulangan.
1. Engineering melaksanakan tindakan teknis dan menyediakan bukti implementasi.
1. QA/Engineering melakukan verifikasi efektivitas sesuai jalur dokumen yang dipilih.
## Prinsip Penghubung Knowledge Base
- PJE bukan pengganti Change Control jika pekerjaan berubah menjadi modifikasi berdampak GMP, validasi, atau kualitas produk.
- Preventive Maintenance bukan pengganti CAPA jika masalah berulang karena akar masalah sistemik.
- Deviasi harus punya bukti teknis dari Engineering agar QA dapat menilai dampak dan klasifikasi dengan benar.
- Spare part kritikal yang berbeda dari spesifikasi asli perlu dikaji melalui Change Control.
- Monitoring harian adalah sumber sinyal awal untuk deviasi, bukan hanya aktivitas pencatatan.
## Related pages
- [[qa/manajemen-perubahan]]
- [[qa/penanganan-deviasi]]
- [[qa/manajemen-capa]]
- [[engineering/monitoring-harian-engineering]]
- [[engineering/engineering-responsibilities]]
- [[engineering/preventive-maintenance-mesin]]
- [[engineering/penanganan-perbaikan-mesin]]
- [[engineering/spare-parts-management]]
- [[engineering/permintaan-jasa-engineering]]
- [[engineering/monitoring-bms-ems]]