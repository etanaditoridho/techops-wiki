# TechOpsKM — Engineering Knowledge Management Wiki
A structured, interlinked knowledge base for PT Etana Biotechnologies Indonesia.
Maintained by Codex (OpenAI) as an AI-powered wiki pipeline.
Based on Andrej Karpathy's LLM Wiki pattern.

## Company context
- **Company**: PT Etana Biotechnologies Indonesia (PT EBI)
- **Industry**: Bioteknologi / pharmaceutical manufacturing (GxP environment)
- **Regulatory framework**: CPOB (BPOM Indonesia), EU GMP, FDA 21 CFR
- **Key departments**: Engineering, QA (Quality Assurance), QS (Quality System), Production
- **Owner**: Dito Wibowo — Digital Transformation Lead
- **Stakeholder**: Pak Miles (CTO)

## Purpose
This wiki converts raw SOP documents from SharePoint into structured, interlinked wiki articles
that Engineers can query via AI (ChatGPT Business + Microsoft MCP).
The goal is a "second brain" for the Engineering team — query SOP knowledge in natural language
without manually searching through hundreds of PDF documents.

## Pipeline architecture
```
SharePoint PTEBIIntranet (PDF SOP asli)
       ↓ Microsoft Graph API (Sites.Selected)
MarkItDown (convert PDF → raw Markdown)
       ↓
SharePoint equipment.engineering / Projects / AI Knowledge / Markdown (buffer MD)
       ↓
Codex CLI (proses raw MD → structured wiki)
       ↓
SharePoint equipment.engineering / Projects / AI Knowledge / Wiki (output)
       ↓
ChatGPT Business + Microsoft MCP (user Q&A)
```

## Folder structure
```
raw/               -- source documents (immutable — never modify)
wiki/              -- markdown wiki pages; source of truth
wiki/index.md      -- table of contents
wiki/log.md        -- append-only operation log
wiki/engineering/  -- Engineering SOP wiki pages
wiki/qa/           -- QA SOP wiki pages
scripts/           -- pipeline automation scripts
```

## SharePoint structure
```
PTEBIIntranet (Site ID: 78d158e2-b13f-4d92-9235-12f054517ee9)
└── PTEBI SOP Library / SOP / Departement R&D  ← PDF SOP asli

equipment.engineering (Site ID: 9ab69ba7-f523-4c27-ae1b-c11ddc4f74b2)
└── Projects / AI Knowledge /
    ├── Markdown /   ← raw MD hasil MarkItDown (buffer)
    ├── Wiki /       ← output wiki terstruktur
    ├── Chunks /     ← chunked content untuk RAG
    ├── Summaries /  ← ringkasan per dokumen
    └── Metadata /   ← metadata per dokumen
```

## SOP naming convention
SOP Etana menggunakan format: `SOP/EBI/[DEPT]-[NUMBER]`
- `EN` = Engineering
- `FF` = Filling & Finishing (Production)
- `QA` = Quality Assurance
- `QS` = Quality System

Contoh: `SOP/EBI/EN-065` = SOP Engineering nomor 065

## Wiki page format
Setiap wiki page harus mengikuti struktur ini:

```markdown
---
title: [Judul halaman]
source: sharepoint
sop_number: [nomor SOP jika ada, misal SOP/EBI/EN-065]
department: [Engineering / QA / QS / Production]
status: wiki
last_processed: [YYYY-MM-DD]
---

# [Judul]

**Summary**: Satu hingga dua kalimat yang mendeskripsikan halaman ini.
**SOP Reference**: [Nomor SOP dan judul]
**Effective Date**: [Tanggal efektif SOP]
**Department**: [Departemen]
**Last updated**: [Tanggal update wiki]

---

## Tujuan
[Isi dari section tujuan SOP]

## Ruang lingkup
[Isi dari section ruang lingkup]

## Tanggung jawab
[Isi dari section tanggung jawab]

## Prosedur
[Prosedur dalam numbered list]

> **Critical step**: [Tandai step kritis dengan blockquote]

> **Safety note**: [Tandai safety notes dengan blockquote]

## Definisi
[Daftar definisi dan singkatan yang relevan]

## Dokumen terkait
- [[nama-wiki-page-terkait]]
- [Nomor SOP referensi]

## Related pages
- [[related-concept-1]]
- [[related-concept-2]]
```

## GxP terminology yang sering muncul
- **GMP** = Good Manufacturing Practice
- **CPOB** = Cara Pembuatan Obat yang Baik (Indonesian GMP)
- **SOP** = Standard Operating Procedure
- **PM** = Preventive Maintenance
- **CM** = Corrective Maintenance
- **ORABS** = Open Restricted Access Barrier System
- **LAF** = Laminar Air Flow
- **HEPA** = High Efficiency Particulate Air filter
- **WFI** = Water for Injection
- **PW** = Purified Water
- **CIP** = Clean In Place
- **SIP** = Sterilization In Place
- **IPC** = In Process Control
- **PJE** = Permintaan Jasa Engineering
- **CC** = Change Control
- **CAPA** = Corrective Action Preventive Action
- **URS** = User Requirement Specification
- **DQ/IQ/OQ/PQ** = Design/Installation/Operational/Performance Qualification
- **BMS** = Building Management System
- **EMS** = Environmental Monitoring System
- **HVAC** = Heating, Ventilation, and Air Conditioning

## Ingest workflow
Ketika ada file MD baru di buffer (SharePoint Markdown folder):
1. Baca full konten MD
2. Identifikasi nomor SOP, departemen, dan scope dokumen
3. Buat wiki page terstruktur sesuai page format di atas
4. Buat atau update concept pages untuk setiap konsep teknis utama
5. Tambahkan wiki-links ([[page-name]]) untuk menghubungkan halaman terkait
6. Update `wiki/index.md` dengan halaman baru dan deskripsi satu baris
7. Append entry ke `wiki/log.md` dengan tanggal, nama SOP, dan apa yang berubah

Satu SOP bisa menyentuh 5-15 wiki pages. Itu normal.

## Language rules
- **Bilingual awareness**: SOP Etana ditulis dalam Bahasa Indonesia dan Inggris secara paralel
- Output wiki boleh dalam Bahasa Indonesia, Inggris, atau campuran — ikuti bahasa dominan SOP
- Terminologi teknis (GxP, equipment names) pertahankan dalam bahasa aslinya
- Jangan terjemahkan nama equipment atau singkatan teknis

## Citation rules
- Setiap klaim faktual harus referensikan source file-nya
- Gunakan format `(source: SOP/EBI/EN-065)` setelah klaim
- Jika dua sumber tidak konsisten, catat kontradiksi secara eksplisit
- Jika klaim tidak ada sumbernya, tandai sebagai `[needs verification]`

## Question answering
Ketika user bertanya:
1. Baca `wiki/index.md` dulu untuk temukan halaman yang relevan
2. Baca halaman tersebut dan synthesize jawaban
3. Cite specific wiki pages dalam jawaban
4. Jika jawaban tidak ada di wiki, katakan secara eksplisit
5. Jika jawaban bernilai, tawarkan untuk disimpan sebagai wiki page baru

## Rules
- Jangan pernah modifikasi apapun di folder `raw/`
- Selalu update `wiki/index.md` dan `wiki/log.md` setelah ada perubahan
- Nama halaman lowercase dengan hyphens (contoh: `perawatan-orabs.md`)
- Tulis dalam bahasa yang jelas dan teknikal tapi mudah dipahami engineer
- Selalu sertakan nomor SOP sebagai referensi
- Critical steps dan safety notes HARUS ditandai dengan blockquote
- Ketika tidak yakin cara kategorisasi sesuatu, tanya user dulu
