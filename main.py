"""
Titik masuk utama untuk program N-Queens CSP.
Mendukung Menu Utama bernomor jika dijalankan tanpa argumen (misal tombol Run di VS Code)
serta eksekusi langsung baris perintah jika diberikan argumen --input.
"""

import argparse
import datetime
import json
import os
import sys
import time

from algorithms import solve_backtracking, solve_backtracking_forward_checking

# Pastikan encoding terminal mendukung UTF-8 di Windows
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

DEFAULT_CONFIG = {
    "variable_order": "left_to_right",
    "default_value_order": "ascending",
    "repeat_waktu": 5,
    "n_pilihan_menu": [4, 8, 12, 16],
    "pilihan_repeat_waktu": [5, 10, 20]
}


class CustomArgumentParser(argparse.ArgumentParser):
    """Parser argumen kustom untuk menangani pesan kesalahan tanpa traceback."""
    def error(self, message):
        print(f"Kesalahan Argumen: {message}", file=sys.stderr)
        self.print_help(sys.stderr)
        sys.exit(2)


def load_config(config_path="config.json"):
    """
    Membaca dan memvalidasi file konfigurasi parameter terpusat.
    Jika file tidak ada atau tidak valid, menggunakan konfigurasi default dengan peringatan.
    """
    config = dict(DEFAULT_CONFIG)
    if not os.path.exists(config_path):
        print(f"Peringatan: File konfigurasi '{config_path}' tidak ditemukan. Menggunakan konfigurasi default.")
        return config

    try:
        with open(config_path, "r", encoding="utf-8") as f:
            cfg_data = json.load(f)
            if isinstance(cfg_data, dict):
                config.update(cfg_data)
            else:
                print(f"Peringatan: Isi file konfigurasi '{config_path}' bukan objek JSON valid. Menggunakan konfigurasi default.")
    except Exception as e:
        print(f"Peringatan: Gagal membaca file konfigurasi '{config_path}' ({e}). Menggunakan konfigurasi default.")

    return config


def load_and_validate_input(input_path, config, exit_on_error=True):
    """
    Membaca dan memvalidasi file input skenario masalah N-Queens.
    Jika exit_on_error=True (mode CLI), langsung keluar saat error.
    Jika exit_on_error=False (mode Menu), cetak pesan error dan kembalikan (None, None).
    """
    def handle_error(msg):
        if exit_on_error:
            print(msg, file=sys.stderr)
            sys.exit(1)
        else:
            print(msg)
            return None, None

    if not os.path.exists(input_path):
        return handle_error(f"Kesalahan: File input tidak ditemukan pada path '{input_path}'.")

    try:
        with open(input_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        return handle_error(f"Kesalahan: File JSON '{input_path}' rusak pada baris {e.lineno}, kolom {e.colno}: {e.msg}")
    except Exception as e:
        return handle_error(f"Kesalahan saat membaca file input '{input_path}': {e}")

    if not isinstance(data, dict):
        return handle_error("Kesalahan: Format isi file JSON harus berupa objek/dictionary.")

    # Validasi kunci 'n'
    if "n" not in data:
        return handle_error("Kesalahan: Kunci 'n' tidak ditemukan dalam file input JSON.")

    n = data["n"]
    if isinstance(n, bool) or not isinstance(n, int) or n <= 0:
        return handle_error(f"Kesalahan: N tidak valid ({n!r}). N harus berupa bilangan bulat positif (contoh: 4, 8, ...).")

    # Validasi urutan nilai (value_order)
    value_order = data.get("value_order")
    if value_order is None:
        value_order = config.get("default_value_order", "ascending")

    if value_order not in ("ascending", "descending"):
        return handle_error(f"Kesalahan: Nilai 'value_order' tidak valid ('{value_order}'). Nilai yang diterima hanya 'ascending' atau 'descending'.")

    return n, value_order


def run_experiment(solve_func, algo_name, n, value_order, repeat_waktu, trace):
    """
    Menjalankan algoritma, mengukur waktu eksekusi rata-rata, dan mengumpulkan metrik.
    Trace hanya dijalankan satu kali jika diaktifkan.
    """
    if trace:
        print(f"\n--- Jejak Langkah (Trace) Algoritma {algo_name} (N={n}, value_order={value_order}) ---")
        first_result = solve_func(n, value_order=value_order, trace=True)
        print("----------------------------------------------------------------------")
        execution_times = []
        for _ in range(repeat_waktu):
            t_start = time.perf_counter()
            solve_func(n, value_order=value_order, trace=False)
            t_end = time.perf_counter()
            execution_times.append(t_end - t_start)
    else:
        execution_times = []
        first_result = None
        for i in range(repeat_waktu):
            t_start = time.perf_counter()
            res = solve_func(n, value_order=value_order, trace=False)
            t_end = time.perf_counter()
            execution_times.append(t_end - t_start)
            if i == 0:
                first_result = res

    avg_time = sum(execution_times) / len(execution_times) if execution_times else 0.0

    return {
        "name": algo_name,
        "n": n,
        "value_order": value_order,
        "solution": first_result["solution"],
        "solution_str": str(first_result["solution"]) if first_result["solution"] is not None else "Tidak ditemukan solusi",
        "assignments": first_result["assignments"],
        "backtracks": first_result["backtracks"],
        "feasible": first_result["feasible"],
        "avg_time": avg_time,
        "repeat_waktu": repeat_waktu
    }


def print_summary(res):
    """Mencetak ringkasan hasil eksperimen per algoritma."""
    print("=" * 60)
    print("RINGKASAN EKSPERIMEN N-QUEENS")
    print("=" * 60)
    print(f"Algoritma           : {res['name']}")
    print(f"Ukuran Papan (N)    : {res['n']}")
    print(f"Urutan Nilai        : {res['value_order']}")
    print(f"Solusi Pertama      : {res['solution_str']}")
    print(f"Jumlah Assignment   : {res['assignments']}")
    print(f"Jumlah Backtrack    : {res['backtracks']}")
    if not res["feasible"]:
        print("Constraint Dilanggar: Tidak ada penempatan yang memenuhi semua constraint (konflik baris dan diagonal pada seluruh kombinasi)")
    keterangan = "Feasible" if res["feasible"] else "Tidak feasible"
    print(f"Keterangan          : {keterangan}")
    print(f"Waktu Eksekusi      : {res['avg_time']:.6f} detik (rata-rata dari {res['repeat_waktu']} pengulangan)")
    print("=" * 60)


def write_log(command_str, input_file, n, value_order, results, same_solution=None, results_dir="results"):
    """
    Menyimpan catatan hasil eksperimen ke dalam file terpisah per eksekusi
    (misal: results/eksperimen_1.txt, results/eksperimen_2.txt, dst).
    """
    os.makedirs(results_dir, exist_ok=True)

    # Menghitung nomor urut eksperimen berikutnya
    existing_files = os.listdir(results_dir)
    max_num = 0
    for fname in existing_files:
        if fname.startswith("eksperimen_") and fname.endswith(".txt"):
            part = fname[len("eksperimen_"):-len(".txt")]
            if part.isdigit():
                max_num = max(max_num, int(part))

    exp_num = max_num + 1
    log_file_path = os.path.join(results_dir, f"eksperimen_{exp_num}.txt")

    now_str = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(log_file_path, "w", encoding="utf-8") as f:
        f.write("=" * 70 + "\n")
        f.write(f"EKSPERIMEN {exp_num}\n")
        f.write(f"Waktu Eksekusi : {now_str}\n")
        f.write(f"Perintah       : {command_str}\n")
        f.write(f"File Input     : {input_file}\n")
        f.write(f"Parameter      : N={n}, value_order={value_order}\n")
        for res in results:
            f.write("-" * 50 + "\n")
            f.write(f"Algoritma      : {res['name']}\n")
            f.write(f"Keterangan     : {'Feasible' if res['feasible'] else 'Tidak feasible'}\n")
            f.write(f"Solusi Pertama : {res['solution_str']}\n")
            f.write(f"Assignment     : {res['assignments']}\n")
            f.write(f"Backtrack      : {res['backtracks']}\n")
            f.write(f"Waktu Rata-rata: {res['avg_time']:.6f} detik ({res['repeat_waktu']} pengulangan)\n")
        if same_solution is not None:
            f.write("-" * 50 + "\n")
            f.write(f"Solusi kedua algoritma sama? {same_solution}\n")
        f.write("=" * 70 + "\n")

    # Salin juga ke log_eksperimen.txt agar file ringkasan tunggal tetap menyimpan data eksekusi terakhir
    fallback_path = os.path.join(results_dir, "log_eksperimen.txt")
    try:
        with open(fallback_path, "w", encoding="utf-8") as f_last:
            with open(log_file_path, "r", encoding="utf-8") as f_src:
                f_last.write(f_src.read())
    except Exception:
        pass

    return log_file_path, exp_num


# ==============================================================================
# FUNGSI-FUNGSI MENU INTERAKTIF
# ==============================================================================

def get_menu_choice(prompt_text, min_val, max_val):
    """
    Meminta input pilihan angka dari pengguna antara min_val dan max_val.
    Jika input berupa huruf, kosong, atau di luar jangkauan:
    cetak 'Pilihan tidak valid. Masukkan angka 0-X.' lalu ulangi pertanyaan.
    Jika Ctrl+C atau EOF: cetak 'Program dihentikan.' dan keluar bersih.
    """
    while True:
        try:
            raw = input(prompt_text).strip()
        except (KeyboardInterrupt, EOFError):
            print("\nProgram dihentikan.")
            sys.exit(0)

        if not raw.isdigit():
            print(f"Pilihan tidak valid. Masukkan angka {min_val}-{max_val}.")
            continue

        val = int(raw)
        if min_val <= val <= max_val:
            return val
        else:
            print(f"Pilihan tidak valid. Masukkan angka {min_val}-{max_val}.")


def get_manual_n():
    """
    Meminta pengguna mengetik angka N secara bebas.
    Validasi: harus bilangan bulat >= 1.
    Jika salah (huruf, desimal, nol, negatif, kosong) cetak pesan error dan ulangi.
    """
    while True:
        try:
            raw = input("Ketik angka N: ").strip()
        except (KeyboardInterrupt, EOFError):
            print("\nProgram dihentikan.")
            sys.exit(0)

        if not raw.isdigit():
            print("N tidak valid (harus bilangan bulat >= 1)")
            continue

        n_val = int(raw)
        if n_val < 1:
            print("N tidak valid (harus bilangan bulat >= 1)")
            continue

        return n_val


def print_active_settings(active_settings):
    """Menampilkan baris status pengaturan aktif di atas setiap menu."""
    algo_map = {
        "all": "Keduanya",
        "bt": "Backtracking (BT)",
        "bt_fc": "BT+FC"
    }
    algo_str = algo_map.get(active_settings["algo"], "Keduanya")
    trace_str = "Nyala" if active_settings["trace"] else "Tidak"
    repeat_str = f"{active_settings['repeat_waktu']}x"
    print("\n" + "-" * 65)
    print(f"Pengaturan: Algoritma={algo_str} | Trace={trace_str} | Pengulangan waktu={repeat_str}")
    print("-" * 65)


def pause_and_return():
    """Menjeda eksekusi agar pengguna dapat membaca ringkasan sebelum kembali."""
    try:
        input("\nTekan Enter untuk kembali...")
    except (KeyboardInterrupt, EOFError):
        print("\nProgram dihentikan.")
        sys.exit(0)


def execute_and_display(source_desc, n, value_order, active_settings):
    """Menjalankan algoritma berdasarkan pengaturan aktif dan mencetak ringkasan serta log."""
    sys.setrecursionlimit(max(10000, n * 20))
    algo = active_settings["algo"]
    trace = active_settings["trace"]
    repeat_waktu = active_settings["repeat_waktu"]

    algorithms_to_run = []
    if algo in ("bt", "all"):
        algorithms_to_run.append((solve_backtracking, "Backtracking"))
    if algo in ("bt_fc", "all"):
        algorithms_to_run.append((solve_backtracking_forward_checking, "Backtracking + Forward Checking"))

    print("\nMenjalankan eksperimen...\n")
    results = []
    for solve_func, algo_name in algorithms_to_run:
        res = run_experiment(solve_func, algo_name, n, value_order, repeat_waktu, trace)
        results.append(res)
        print_summary(res)

    same_solution = None
    if algo == "all" and len(results) == 2:
        is_same = results[0]["solution"] == results[1]["solution"]
        same_solution = "Ya" if is_same else "Tidak"
        print(f"Solusi kedua algoritma sama? {same_solution}")

    cmd_desc = f"Menu: {source_desc} | Algo: {algo}" + (" | Trace" if trace else "")
    log_file_path, exp_num = write_log(cmd_desc, source_desc, n, value_order, results, same_solution)
    print(f"\n[Info] Hasil eksperimen telah dicatat ke: {log_file_path}")


def menu_run_from_file(config, active_settings):
    """PILIHAN 1 - Jalankan dari file skenario pada folder inputs/."""
    inputs_dir = "inputs"
    while True:
        print_active_settings(active_settings)
        print("PILIHAN 1 - JALANKAN DARI FILE SKENARIO")

        if not os.path.exists(inputs_dir) or not os.path.isdir(inputs_dir):
            print("Pesan: Folder 'inputs/' tidak ditemukan.")
            pause_and_return()
            return

        json_files = sorted([f for f in os.listdir(inputs_dir) if f.endswith(".json")])
        if not json_files:
            print("Pesan: Folder 'inputs/' kosong (tidak ada file .json).")
            pause_and_return()
            return

        print("\nDaftar file skenario:")
        for idx, fname in enumerate(json_files, start=1):
            fpath = os.path.join(inputs_dir, fname)
            info = ""
            try:
                with open(fpath, "r", encoding="utf-8") as f:
                    data = json.load(f)
                if isinstance(data, dict) and "n" in data:
                    n_val = data["n"]
                    vo_val = data.get("value_order", config.get("default_value_order", "ascending"))
                    info = f" (N={n_val}, {vo_val})"
            except Exception:
                info = " (Format file tidak valid)"
            print(f"  {idx}. {fname}{info}")
        print("  0. Kembali")

        choice = get_menu_choice(f"\nPilihan Anda [0-{len(json_files)}]: ", 0, len(json_files))
        if choice == 0:
            return

        selected_file = os.path.join(inputs_dir, json_files[choice - 1])
        n, value_order = load_and_validate_input(selected_file, config, exit_on_error=False)
        if n is None:
            # File tidak valid; pesan kesalahan telah dicetak, ulangi daftar file
            print("\nSilakan perbaiki file tersebut atau pilih file skenario lain.")
            continue

        execute_and_display(selected_file, n, value_order, active_settings)
        pause_and_return()


def menu_run_manual(config, active_settings):
    """PILIHAN 2 - Jalankan dengan input manual (pilih N cepat atau ketik sendiri)."""
    quick_n_list = config.get("n_pilihan_menu", [4, 8, 12, 16])

    while True:
        print_active_settings(active_settings)
        print("PILIHAN 2 - INPUT MANUAL: LANGKAH 1 (Pilih N)")
        for idx, val in enumerate(quick_n_list, start=1):
            print(f"  {idx}. N = {val}")
        custom_idx = len(quick_n_list) + 1
        print(f"  {custom_idx}. Ketik N sendiri")
        print("  0. Kembali")

        choice = get_menu_choice(f"\nPilihan Anda [0-{custom_idx}]: ", 0, custom_idx)
        if choice == 0:
            return

        if choice == custom_idx:
            n = get_manual_n()
        else:
            n = quick_n_list[choice - 1]

        # Langkah 2: Urutan nilai
        print_active_settings(active_settings)
        print(f"PILIHAN 2 - INPUT MANUAL: LANGKAH 2 (Urutan Nilai untuk N={n})")
        print("  1. Naik (1 -> N)  = ascending")
        print("  2. Turun (N -> 1) = descending")
        print("  0. Kembali")

        order_choice = get_menu_choice("\nPilihan Anda [0-2]: ", 0, 2)
        if order_choice == 0:
            continue  # Kembali ke pemilihan N

        value_order = "ascending" if order_choice == 1 else "descending"

        execute_and_display(f"Manual (N={n}, {value_order})", n, value_order, active_settings)
        pause_and_return()
        return


def menu_settings(config, active_settings):
    """PILIHAN 3 - Pengaturan algoritma, trace, dan pengulangan pengukuran waktu."""
    while True:
        print_active_settings(active_settings)
        print("PILIHAN 3 - PENGATURAN")
        print("  1. Algoritma")
        print("  2. Mode trace")
        print("  3. Pengulangan pengukuran waktu")
        print("  4. Kembalikan ke bawaan config.json")
        print("  0. Kembali")

        choice = get_menu_choice("\nPilihan Anda [0-4]: ", 0, 4)
        if choice == 0:
            return

        if choice == 1:
            print_active_settings(active_settings)
            print("PENGATURAN: PILIH ALGORITMA")
            print("  1. Backtracking (BT)")
            print("  2. Backtracking + Forward Checking (BT+FC)")
            print("  3. Keduanya")
            print("  0. Kembali")
            sub_choice = get_menu_choice("\nPilihan Anda [0-3]: ", 0, 3)
            if sub_choice == 1:
                active_settings["algo"] = "bt"
            elif sub_choice == 2:
                active_settings["algo"] = "bt_fc"
            elif sub_choice == 3:
                active_settings["algo"] = "all"

        elif choice == 2:
            print_active_settings(active_settings)
            print("PENGATURAN: PILIH MODE TRACE")
            print("  1. Mati")
            print("  2. Nyala")
            print("  0. Kembali")
            sub_choice = get_menu_choice("\nPilihan Anda [0-2]: ", 0, 2)
            if sub_choice == 1:
                active_settings["trace"] = False
            elif sub_choice == 2:
                active_settings["trace"] = True

        elif choice == 3:
            pilihan_repeat = config.get("pilihan_repeat_waktu", [5, 10, 20])
            cfg_repeat = config.get("repeat_waktu", 5)
            print_active_settings(active_settings)
            print("PENGATURAN: PENGULANGAN PENGUKURAN WAKTU")
            for idx, val in enumerate(pilihan_repeat, start=1):
                bawaan_tag = " (bawaan)" if val == cfg_repeat else ""
                print(f"  {idx}. {val}x{bawaan_tag}")
            print("  0. Kembali")
            sub_choice = get_menu_choice(f"\nPilihan Anda [0-{len(pilihan_repeat)}]: ", 0, len(pilihan_repeat))
            if sub_choice > 0:
                active_settings["repeat_waktu"] = pilihan_repeat[sub_choice - 1]

        elif choice == 4:
            active_settings["algo"] = "all"
            active_settings["trace"] = False
            active_settings["repeat_waktu"] = config.get("repeat_waktu", 5)
            print("\nPengaturan berhasil dikembalikan ke bawaan config.json.")


def menu_view_last_log(active_settings):
    """PILIHAN 4 - Lihat log eksperimen terakhir."""
    print_active_settings(active_settings)
    print("PILIHAN 4 - LIHAT LOG EKSPERIMEN TERAKHIR\n")
    results_dir = "results"

    if not os.path.exists(results_dir):
        print("Belum ada log eksperimen yang tercatat.")
        pause_and_return()
        return

    # Cari file eksperimen dengan nomor urut tertinggi
    exp_files = []
    for fname in os.listdir(results_dir):
        if fname.startswith("eksperimen_") and fname.endswith(".txt"):
            part = fname[len("eksperimen_"):-len(".txt")]
            if part.isdigit():
                exp_files.append((int(part), fname))

    if exp_files:
        exp_files.sort(key=lambda x: x[0])
        latest_num, latest_fname = exp_files[-1]
        latest_path = os.path.join(results_dir, latest_fname)
        try:
            with open(latest_path, "r", encoding="utf-8") as f:
                content = f.read().strip()
            print(f"[{latest_fname}]")
            print(content)
        except Exception as e:
            print(f"Gagal membaca file log '{latest_fname}': {e}")
    else:
        fallback_path = os.path.join(results_dir, "log_eksperimen.txt")
        if os.path.exists(fallback_path):
            try:
                with open(fallback_path, "r", encoding="utf-8") as f:
                    content = f.read().strip()
                if content:
                    print(content)
                else:
                    print("Belum ada log eksperimen yang tercatat.")
            except Exception as e:
                print(f"Gagal membaca file log: {e}")
        else:
            print("Belum ada log eksperimen yang tercatat.")

    pause_and_return()


def run_main_menu(config):
    """Menjalankan loop menu utama saat program dipanggil tanpa argumen."""
    active_settings = {
        "algo": "all",
        "trace": False,
        "repeat_waktu": config.get("repeat_waktu", 5)
    }

    while True:
        print_active_settings(active_settings)
        print("MENU UTAMA")
        print("  1. Jalankan dari file skenario")
        print("  2. Jalankan dengan input manual (ketik N sendiri)")
        print("  3. Pengaturan")
        print("  4. Lihat log eksperimen terakhir")
        print("  0. Keluar")

        choice = get_menu_choice("\nPilihan Anda [0-4]: ", 0, 4)

        if choice == 1:
            menu_run_from_file(config, active_settings)
        elif choice == 2:
            menu_run_manual(config, active_settings)
        elif choice == 3:
            menu_settings(config, active_settings)
        elif choice == 4:
            menu_view_last_log(active_settings)
        elif choice == 0:
            print("\nTerima kasih. Program selesai.")
            sys.exit(0)


# ==============================================================================
# ENTRY POINT
# ==============================================================================

def main():
    """Fungsi utama program."""
    # Jika dijalankan tanpa argumen apa pun (misal tombol Play/Run di VS Code), tampilkan Menu Utama
    if len(sys.argv) == 1:
        config = load_config("config.json")
        run_main_menu(config)
        return

    # Mode baris perintah (CLI) jika dijalankan dengan argumen
    parser = CustomArgumentParser(
        description="Penyelesaian Masalah N-Queens CSP: Backtracking vs Backtracking + Forward Checking"
    )
    parser.add_argument("--input", required=False, help="Path ke file input JSON skenario masalah")
    parser.add_argument("--algo", choices=["bt", "bt_fc", "all"], default="all", help="Pilihan algoritma: bt, bt_fc, atau all (default: all)")
    parser.add_argument("--trace", action="store_true", help="Cetak proses pencarian langkah demi langkah")
    parser.add_argument("--config", default="config.json", help="Path ke file konfigurasi parameter terpusat (default: config.json)")

    args = parser.parse_args()

    if not args.input:
        print("Kesalahan Argumen: Argumen '--input <file>' wajib disertakan pada mode baris perintah.", file=sys.stderr)
        sys.exit(1)

    # Baca konfigurasi terpusat
    config = load_config(args.config)

    # Validasi urutan variabel dari konfigurasi (hanya 'left_to_right' yang didukung)
    variable_order = config.get("variable_order", "left_to_right")
    if variable_order != "left_to_right":
        print(f"Kesalahan: Nilai 'variable_order' pada config ('{variable_order}') tidak didukung. Hanya 'left_to_right' yang didukung.", file=sys.stderr)
        sys.exit(1)

    # Jumlah pengulangan waktu
    repeat_waktu = config.get("repeat_waktu", 5)
    if not isinstance(repeat_waktu, int) or repeat_waktu <= 0:
        repeat_waktu = 5

    # Baca dan validasi file input skenario
    n, value_order = load_and_validate_input(args.input, config, exit_on_error=True)

    # Menyesuaikan batas rekursi untuk nilai N yang besar
    sys.setrecursionlimit(max(10000, n * 20))

    # Tentukan algoritma yang akan dijalankan
    algorithms_to_run = []
    if args.algo in ("bt", "all"):
        algorithms_to_run.append((solve_backtracking, "Backtracking"))
    if args.algo in ("bt_fc", "all"):
        algorithms_to_run.append((solve_backtracking_forward_checking, "Backtracking + Forward Checking"))

    results = []
    for solve_func, algo_name in algorithms_to_run:
        res = run_experiment(solve_func, algo_name, n, value_order, repeat_waktu, args.trace)
        results.append(res)
        print_summary(res)

    same_solution = None
    if args.algo == "all" and len(results) == 2:
        is_same = results[0]["solution"] == results[1]["solution"]
        same_solution = "Ya" if is_same else "Tidak"
        print(f"Solusi kedua algoritma sama? {same_solution}")

    # Catat log eksperimen
    command_str = "python " + " ".join([os.path.basename(sys.argv[0])] + sys.argv[1:])
    log_file_path, exp_num = write_log(command_str, args.input, n, value_order, results, same_solution)
    print(f"\n[Info] Hasil eksperimen telah dicatat ke: {log_file_path}")


if __name__ == "__main__":
    main()
