# Tenant Security Skills

> Buktikan isolasi tenant melalui konten respons dan status database, bukan hanya kode status HTTP.

Tenant Security Skills adalah Agent Skill yang mengaudit aplikasi SaaS multi-tenant untuk menemukan bug isolasi otorisasi. Alat ini menyediakan kerangka pengujian yang kuat untuk membuktikan isolasi dengan menganalisis konten respons dan status database, memastikan tidak ada kebocoran data bahkan ketika akses ditolak.

## Masalah

Sebagian besar pengujian BOLA (Broken Object Level Authorization) dan IDOR (Insecure Direct Object Reference) hanya memeriksa kode status HTTP seperti 403 Forbidden atau 404 Not Found. Namun, respons 403 tidak menjamin bahwa data sensitif tidak bocor di badan respons. Demikian pula, permintaan PUT yang ditolak tidak membuktikan bahwa database tidak benar-benar diubah sebelum kesalahan dikembalikan. Keamanan tenant yang nyata memerlukan verifikasi tingkat konten dan tingkat status untuk memastikan isolasi lengkap.

## Apa yang Dilakukan Skill Ini

- Memetakan batas otorisasi dengan matriks Principal-Action-Resource.
- Menguji akses lintas tenant dengan memeriksa konten respons, bukan hanya kode status.
- Memverifikasi integritas status database setelah upaya mutasi ditolak.
- Menghasilkan pengujian regresi yang menegaskan konten respons.
- Memberikan remediasi berbasis bukti dengan verifikasi sebelum/sesudah.

## Mulai Cepat

### Instalasi

```bash
npx skills add MhmmdFaizal04/tenant-security-skills
```

### Contoh Prompt

```text
Use tenant-security-skills to audit the /api/projects endpoints for cross-tenant data leaks.
```

```text
Verify if the PUT /api/users/{id} endpoint allows cross-tenant database mutations.
```

```text
Generate a regression test suite for the tenant authorization boundaries on the /api/reports endpoints.
```

## Cara Kerjanya

1. **Map** -> Bangun matriks otorisasi
2. **Baseline** -> Verifikasi akses yang sah berfungsi
3. **Probe** -> Uji batas lintas tenant
4. **Evidence** -> Tangkap konten respons + status database
5. **Regress** -> Hasilkan test suite
6. **Fix** -> Terapkan dan verifikasi remediasi

## Coba Secara Lokal

```bash
# Start the vulnerable test API
cd fixtures/vulnerable-api
pip install -r requirements.txt
python app.py  # Runs on port 5001

# In another terminal, try a cross-tenant request:
curl -H "X-API-Key: acme-admin-key-001" http://localhost:5001/api/projects/3
# Returns Globex's project data - this is the vulnerability!

# Now try the secure version:
cd fixtures/secure-api
python app.py  # Runs on port 5002
curl -H "X-API-Key: acme-admin-key-001" http://localhost:5002/api/projects/3
# Returns 404 - tenant boundary enforced
```

## Detail Fixture

| Tenant | Pengguna | ID Proyek | Versi Aplikasi | Status |
|---|---|---|---|---|
| Acme | Alice (Admin) | 1, 2 | Vulnerable | Mengizinkan akses lintas tenant |
| Acme | Bob (User) | 1, 2 | Secure | Menolak akses lintas tenant |
| Globex | Charlie (Admin)| 3, 4 | Vulnerable | Mengizinkan akses lintas tenant |
| Globex | Dave (User) | 3, 4 | Secure | Menolak akses lintas tenant |

## Kompatibilitas

- Agent Skills CLI (`npx skills`)
- Claude Code / Antigravity / agen pengkodean yang kompatibel dengan Agent Skills
- Fixtures memerlukan Python 3.11+ dan Flask

## Tingkat Bukti

| Bukti | Apa yang Dibuktikan |
|----------|---------------|
| Hanya kode status HTTP | Permintaan ditolak (tetapi data mungkin telah bocor) |
| Pemeriksaan konten respons | Tidak ada data tenant dalam badan respons |
| Verifikasi status database | Mutasi yang ditolak tidak mengubah status |
| Regression test suite | Batas bertahan di seluruh perubahan kode |

## Perbandingan

| Fitur | Pengujian BOLA Tradisional | Skill Ini |
|---------|------------------------|------------|
| Pemeriksaan kode status | Ya | Ya |
| Analisis konten respons | Jarang | Selalu |
| Verifikasi status database | Tidak | Ya |
| Pengujian regresi otomatis | Manual | Dihasilkan |
| Laporan berbasis bukti | Checklist | Bundel bukti lengkap |

## Lisensi

MIT

## Berkontribusi

Lihat [CONTRIBUTING.md](../CONTRIBUTING.md) untuk panduan.
