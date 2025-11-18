# -*- coding: utf-8 -*-
import os
import subprocess
import time
import csv
import shutil
import re
from shutil import which
from pathlib import Path

# ==============================================================================
# --- CONFIGURAÇÃO ---
# ==============================================================================

NUM_REPETICOES = 10
WARMUP_RUNS = 1

BASE_DIR = Path(__file__).resolve().parent
DATASETS_DIR = BASE_DIR / "datasets"
OUTPUT_DIR = BASE_DIR / "resultados"

DATASETS = {
    "Texto Puro": "Dataset_Texto",
    "Imagens": "Dataset_Imagens",
    "Misto": "Dataset_Misto",
}

# ==============================================================================
# --- FUNÇÕES AUXILIARES ---
# ==============================================================================

def resolve_executable(candidates):
    for c in candidates:
        p = Path(c)
        if p.is_absolute() and p.exists():
            return str(p)
        w = which(c)
        if w:
            return w
    return None

def get_dir_size_bytes(path: Path) -> int:
    total_size = 0
    for dirpath, _, filenames in os.walk(path):
        for f in filenames:
            try:
                fp = os.path.join(dirpath, f)
                if not os.path.islink(fp):
                    total_size += os.path.getsize(fp)
            except FileNotFoundError:
                pass
    return total_size

def count_files(path: Path) -> int:
    n = 0
    for _, _, filenames in os.walk(path):
        n += len(filenames)
    return n

def format_mb(size_bytes: int) -> float:
    return size_bytes / (1024 * 1024)

def run_timed(command, cwd=None):
    start = time.perf_counter()
    cp = subprocess.run(
        command,
        check=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=cwd,
    )
    end = time.perf_counter()
    return end - start

def ensure_clean(path: Path):
    if path.is_file():
        try:
            path.unlink()
        except FileNotFoundError:
            pass
    elif path.is_dir():
        shutil.rmtree(path, ignore_errors=True)

def get_rar_version(rar_path: str):
    try:
        cp = subprocess.run([rar_path], stdout=subprocess.PIPE, stderr=subprocess.STDOUT, check=False)
        out = cp.stdout.decode(errors="ignore")
        m = re.search(r"RAR\s+(\d+)\.(\d+)", out)
        if m:
            return int(m.group(1)), int(m.group(2))
    except Exception:
        pass
    return None

# ==============================================================================
# --- LÓGICA PRINCIPAL (NÃO-SÓLIDO)
# ==============================================================================

def main():
    print("Iniciando experimento...")

    OUTPUT_DIR.mkdir(exist_ok=True, parents=True)

    sevenzip = resolve_executable([
        "7z", "7zz",
        r"C:\Program Files\7-Zip\7z.exe",
        r"C:\Program Files (x86)\7-Zip\7z.exe",
    ])
    rar = resolve_executable([
        "rar",
        r"C:\Program Files\WinRAR\Rar.exe",
        r"C:\Program Files (x86)\WinRAR\Rar.exe",
    ])

    algoritmos = []
    if sevenzip:
        algoritmos += ["zip", "7z"]
    else:
        print("AVISO: 7-Zip não encontrado; ZIP e 7Z serão ignorados.")
    if rar:
        algoritmos += ["rar"]
    else:
        print("AVISO: RAR/WinRAR não encontrado; RAR será ignorado.")

    if not algoritmos:
        print("ERRO: Nenhum compressor encontrado no PATH ou nos caminhos padrão.")
        return

    rar_version = get_rar_version(rar) if rar else None
    if rar_version:
        print(f"RAR detectado: versão {rar_version[0]}.{rar_version[1]}")
    elif "rar" in algoritmos:
        print("AVISO: Não foi possível detectar a versão do RAR; assumindo compatibilidade básica.")

    csv_path = OUTPUT_DIR / "resultados_compressao.csv"
    csv_headers = [
        "Dataset", "Algoritmo", "Repeticao",
        "Arquivos no Dataset",
        "Tamanho Original (MB)", "Tamanho Comprimido (MB)", "Taxa de Compressao (%)",
        "Tempo de Compressao (s)", "Tempo de Descompressao (s)"
    ]

    rows = []

    for dataset_name, dataset_folder in DATASETS.items():
        source_path = DATASETS_DIR / dataset_folder
        if not source_path.is_dir():
            print(f"AVISO: Pasta do dataset não encontrada: {source_path}. Pulando...")
            continue

        original_size_bytes = get_dir_size_bytes(source_path)
        if original_size_bytes == 0:
            print(f"AVISO: Dataset vazio: {source_path}. Pulando...")
            continue

        original_size_mb = format_mb(original_size_bytes)
        nfiles = count_files(source_path)
        print(f"\n--- Dataset: {dataset_name} ({original_size_mb:.2f} MB; {nfiles} arquivos) ---")

        for algoritmo in algoritmos:
            print(f"  Algoritmo: {algoritmo.upper()} (Modo Não-Sólido)") 

            total_runs = NUM_REPETICOES + WARMUP_RUNS
            for i in range(1, total_runs + 1):
                archive_name = f"{dataset_folder}_{algoritmo}_rep{i}.{algoritmo}"
                archive_path = OUTPUT_DIR / archive_name
                extract_path = OUTPUT_DIR / f"{dataset_folder}_{algoritmo}_rep{i}_extracao"

                ensure_clean(archive_path)
                ensure_clean(extract_path)

                try:
                    if algoritmo == "zip":
                        cmd_compress = [
                            sevenzip, "a", "-tzip",
                            "-mx=9", "-mmt=on", "-bd", "-y",
                            str(archive_path), "."
                        ]
                        tempo_compressao = run_timed(cmd_compress, cwd=str(source_path))

                    elif algoritmo == "7z":
                        cmd_compress = [
                            sevenzip, "a", "-t7z",
                            "-mx=9", "-mmt=on", 
                            "-ms=off",  # <-- Força modo não-sólido
                            "-bd", "-y",
                            str(archive_path), "."
                        ]
                        tempo_compressao = run_timed(cmd_compress, cwd=str(source_path))

                    elif algoritmo == "rar":
                        rar_switches = [
                            "-ep1", "-idq", "-y", "-r",
                            "-s-"  # <-- Força modo não-sólido
                        ]
                        if rar_version and rar_version[0] >= 5:
                            rar_switches.insert(0, "-ma5")
                        
                        cmd_compress = [rar, "a"] + rar_switches + [str(archive_path), "."]
                        tempo_compressao = run_timed(cmd_compress, cwd=str(source_path))

                except subprocess.CalledProcessError as e:
                    print(f"ERRO: {algoritmo.upper()} falhou (retcode {e.returncode}). Comando: {e.cmd}")
                    if algoritmo == "rar" and e.returncode == 7:
                        try:
                            print("Tentando novamente RAR com switches mínimos...")
                            cmd_compress = [
                                rar, "a", "-r", "-idq", "-y", 
                                "-s-",  # <-- Modo não-sólido (fallback)
                                str(archive_path), "."
                            ]
                            tempo_compressao = run_timed(cmd_compress, cwd=str(source_path))
                        except subprocess.CalledProcessError as e2:
                            print(f"ERRO: RAR voltou a falhar (retcode {e2.returncode}). Pulando RAR neste dataset.")
                            ensure_clean(archive_path)
                            ensure_clean(extract_path)
                            break
                    else:
                        ensure_clean(archive_path)
                        ensure_clean(extract_path)
                        break

                # Métricas de tamanho
                if not archive_path.exists():
                    print("AVISO: Arquivo de saída não foi criado. Pulando linha.")
                    ensure_clean(extract_path)
                    continue

                compressed_size_bytes = archive_path.stat().st_size
                compressed_size_mb = format_mb(compressed_size_bytes)
                taxa_compressao = (1 - (compressed_size_bytes / original_size_bytes)) * 100.0

                # ------------------ DESCOMPRESSÃO ------------------
                extract_path.mkdir(parents=True, exist_ok=True)
                try:
                    if algoritmo in ["zip", "7z"]:
                        cmd_decompress = [sevenzip, "x", "-bd", "-y", str(archive_path), f"-o{extract_path}"]
                    elif algoritmo == "rar":
                        cmd_decompress = [rar, "x", "-o+", "-idq", "-y", str(archive_path), str(extract_path)]
                    tempo_descompressao = run_timed(cmd_decompress)
                except subprocess.CalledProcessError as e:
                    print(f"ERRO na descompressão {algoritmo.upper()} (retcode {e.returncode}). Pulando linha.")
                    ensure_clean(archive_path)
                    ensure_clean(extract_path)
                    continue

                if i <= WARMUP_RUNS:
                    ensure_clean(archive_path)
                    ensure_clean(extract_path)
                    continue

                rows.append({
                    "Dataset": dataset_name,
                    "Algoritmo": algoritmo.upper(),
                    "Repeticao": i - WARMUP_RUNS,
                    "Arquivos no Dataset": nfiles,
                    "Tamanho Original (MB)": f"{original_size_mb:.4f}",
                    "Tamanho Comprimido (MB)": f"{compressed_size_mb:.4f}",
                    "Taxa de Compressao (%)": f"{taxa_compressao:.4f}",
                    "Tempo de Compressao (s)": f"{tempo_compressao:.4f}",
                    "Tempo de Descompressao (s)": f"{tempo_descompressao:.4f}",
                })

                ensure_clean(archive_path)
                ensure_clean(extract_path)

    if rows:
        with open(csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=csv_headers)
            writer.writeheader()
            writer.writerows(rows)
        print(f"\nResultados salvos em: {csv_path}")
    else:
        print("\nNenhum resultado gerado (verifique a presença dos datasets e das ferramentas).")

    print("\nExperimento concluído!")

if __name__ == "__main__":
    main()