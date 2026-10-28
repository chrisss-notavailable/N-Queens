"""
Modul Algoritma CSP N-Queens: Backtracking vs Backtracking + Forward Checking.

DEFINISI HITUNGAN:
Assignment = nilai yang lolos cek konsistensi dan disimpan.
Backtrack  = assignment yang kemudian dibatalkan.

Backtracking polos:
Untuk kolom c, coba nilai r sesuai value_order. Cek konflik HANYA terhadap ratu yang sudah diletakkan
di kolom 1..c-1. Jika lolos: assignment += 1, simpan, lanjut ke kolom c+1. Jika kolom berikutnya gagal:
batalkan nilai itu, backtrack += 1, coba nilai berikutnya. Jika semua nilai habis: gagal, mundur ke kolom sebelumnya.

Backtracking + Forward Checking:
Setiap kolom punya domain (awal penuh {1..N}). Untuk kolom c, iterasi nilai sesuai value_order,
HANYA nilai yang masih ada di domain kolom c; nilai yang sudah dicoret dilewati dan tidak dihitung apa pun.
Saat nilai r diambil dari domain: assignment += 1 LANGSUNG (dihitung SEBELUM pencoretan), simpan ratu.
Lalu untuk setiap kolom j > c, coret dari domain[j] nilai r, r-(j-c), dan r+(j-c). Catat semua pencoretan
(j, nilai) dalam sebuah list agar bisa dikembalikan persis. Jika ada domain kolom yang menjadi kosong:
kembalikan semua pencoretan, backtrack += 1, coba nilai berikutnya. Jika tidak ada domain kosong, lanjut
ke kolom c+1; jika kolom berikutnya gagal: kembalikan pencoretan, backtrack += 1.

Tabel Angka Acuan (value_order ascending):
| N  | BT assign/backtrack | BT+FC assign/backtrack | Solusi pertama                           |
| 4  | 8 / 4               | 8 / 4                  | (2, 4, 1, 3)                             |
| 8  | 113 / 105           | 88 / 80                | (1, 5, 8, 6, 3, 7, 2, 4)                 |
| 12 | 261 / 249           | 193 / 181              | (1, 3, 5, 8, 10, 12, 6, 11, 2, 7, 9, 4) |
"""


def solve_backtracking(n, value_order="ascending", trace=False):
    """
    Menyelesaikan N-Queens CSP menggunakan algoritma Backtracking polos.

    Parameter:
        n (int): Ukuran papan dan jumlah ratu.
        value_order (str): Urutan nilai ('ascending' atau 'descending').
        trace (bool): Jika True, cetak jejak langkah proses pencarian.

    Return:
        dict: Hasil berupa solution, assignments, backtracks, feasible.
    """
    val_range = list(range(1, n + 1)) if value_order == "ascending" else list(range(n, 0, -1))
    queens = {}
    assignments = 0
    backtracks = 0
    step_count = 0

    def backtrack(col):
        nonlocal assignments, backtracks, step_count

        # Basis: seluruh kolom 1..n telah terisi ratu tanpa konflik
        if col > n:
            return tuple(queens[c] for c in range(1, n + 1))

        # Coba nilai r pada kolom col sesuai urutan nilai
        for r in val_range:
            conflict = None
            # Cek konflik HANYA terhadap ratu yang sudah diletakkan pada kolom 1..col-1
            for prev_c in range(1, col):
                prev_r = queens[prev_c]
                # Konflik baris sama atau diagonal sama (|r1 - r2| == |c1 - c2|)
                if prev_r == r or abs(prev_r - r) == abs(prev_c - col):
                    conflict = (prev_c, prev_r)
                    break

            # Jika terjadi konflik, nilai ditolak
            if conflict is not None:
                if trace:
                    step_count += 1
                    print(f"Langkah {step_count}: TOLAK X{col}={r} (bentrok dengan X{conflict[0]}={conflict[1]})")
                continue

            # Nilai lolos uji konsistensi: assignment disimpan dan dicatat
            assignments += 1
            queens[col] = r
            if trace:
                step_count += 1
                print(f"Langkah {step_count}: ASSIGN X{col}={r}")

            # Rekursi ke kolom berikutnya
            res = backtrack(col + 1)
            if res is not None:
                return res

            # Jika penempatan di kolom-kolom berikutnya gagal, batalkan assignment ini
            backtracks += 1
            if trace:
                step_count += 1
                print(f"Langkah {step_count}: BACKTRACK X{col}={r}")
            del queens[col]

        # Seluruh nilai habis dan tidak ada yang menghasilkan solusi
        return None

    solution = backtrack(1)
    return {
        "solution": solution,
        "assignments": assignments,
        "backtracks": backtracks,
        "feasible": solution is not None
    }


def solve_backtracking_forward_checking(n, value_order="ascending", trace=False):
    """
    Menyelesaikan N-Queens CSP menggunakan Backtracking dengan Forward Checking.

    Parameter:
        n (int): Ukuran papan dan jumlah ratu.
        value_order (str): Urutan nilai ('ascending' atau 'descending').
        trace (bool): Jika True, cetak jejak langkah proses pencarian beserta domain sisa.

    Return:
        dict: Hasil berupa solution, assignments, backtracks, feasible.
    """
    val_range = list(range(1, n + 1)) if value_order == "ascending" else list(range(n, 0, -1))
    # Domain awal untuk setiap kolom: {1..N}
    domains = {c: set(range(1, n + 1)) for c in range(1, n + 1)}
    queens = {}
    assignments = 0
    backtracks = 0
    step_count = 0

    def format_domains(start_col):
        """Memformat domain kolom yang belum terisi untuk tampilan trace."""
        parts = []
        for c in range(start_col, n + 1):
            sorted_vals = sorted(domains[c])
            vals_str = ", ".join(map(str, sorted_vals))
            parts.append(f"D{c}={{{vals_str}}}")
        return " ".join(parts)

    def backtrack_fc(col):
        nonlocal assignments, backtracks, step_count

        # Basis: semua kolom 1..n berhasil diisi
        if col > n:
            return tuple(queens[c] for c in range(1, n + 1))

        # Iterasi HANYA nilai yang masih ada di domain kolom col sesuai value_order
        # Nilai yang sudah dicoret otomatis dilewati dan tidak dihitung apa pun
        current_domain = [v for v in val_range if v in domains[col]]
        for r in current_domain:
            # Saat nilai r diambil dari domain: assignment += 1 LANGSUNG (sebelum pencoretan)
            assignments += 1
            queens[col] = r
            if trace:
                step_count += 1
                print(f"Langkah {step_count}: ASSIGN X{col}={r}")

            # Forward Checking: coret nilai tidak konsisten dari domain kolom j > col
            pruned = []
            empty_col = None
            for j in range(col + 1, n + 1):
                # Nilai yang melanggar: baris sama r, diagonal r-(j-col), diagonal r+(j-col)
                to_remove = (r, r - (j - col), r + (j - col))
                for rem in to_remove:
                    if rem in domains[j]:
                        domains[j].remove(rem)
                        # Catat semua pencoretan (j, nilai) agar bisa dikembalikan persis
                        pruned.append((j, rem))
                # Cek jika domain menjadi kosong
                if len(domains[j]) == 0 and empty_col is None:
                    empty_col = j

            # Cetak domain semua kolom yang belum terisi setelah pencoretan
            if trace and col < n:
                print(f"           {format_domains(col + 1)}")

            # Jika ada domain kolom yang menjadi kosong:
            if empty_col is not None:
                if trace:
                    print(f"           DOMAIN KOSONG pada kolom {empty_col} -> mundur")
                # Kembalikan semua pencoretan dari list
                for col_idx, val in pruned:
                    domains[col_idx].add(val)
                backtracks += 1
                if trace:
                    step_count += 1
                    print(f"Langkah {step_count}: BACKTRACK X{col}={r} (pencoretan domain dikembalikan)")
                del queens[col]
                continue

            # Rekursi ke kolom berikutnya
            res = backtrack_fc(col + 1)
            if res is not None:
                return res

            # Jika langkah berikutnya gagal: kembalikan pencoretan dan lakukan backtrack
            for col_idx, val in pruned:
                domains[col_idx].add(val)
            backtracks += 1
            if trace:
                step_count += 1
                print(f"Langkah {step_count}: BACKTRACK X{col}={r} (pencoretan domain dikembalikan)")
            del queens[col]

        return None

    solution = backtrack_fc(1)
    return {
        "solution": solution,
        "assignments": assignments,
        "backtracks": backtracks,
        "feasible": solution is not None
    }

