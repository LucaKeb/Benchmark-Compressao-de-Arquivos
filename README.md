# Benchmark de Desempenho de Algoritmos de Compressão

Este repositório contém um script em Python para realizar um benchmark de desempenho entre diferentes algoritmos de compressão de arquivos (`zip`, `7z`, `rar`).

O script mede e compara:
- **Tempo de compressão**
- **Tempo de descompressão**
- **Taxa de compressão**

Os testes são executados em múltiplos datasets (texto, imagens, misto) para avaliar o comportamento dos algoritmos em diferentes cenários. Os resultados são salvos em um arquivo CSV para fácil análise.

## Funcionalidades

- Compara os algoritmos **ZIP**, **7-Zip (7z)** e **RAR**.
- Executa múltiplas repetições para garantir a consistência estatística dos resultados.
- Inclui execuções de "aquecimento" (warm-up) para mitigar efeitos de cache do sistema.
- Detecta automaticamente os executáveis dos compressores no `PATH` do sistema ou em locais de instalação padrão.
- Gera um arquivo `resultados_compressao.csv` com dados detalhados de cada execução.
- Suporta o modo de compressão "não-sólido" para uma comparação justa entre os formatos.

## Pré-requisitos

Antes de executar o script, certifique-se de que você tem:

1.  **Python 3.x** instalado.
2.  **7-Zip**: O executável (`7z.exe` ou `7zz`) deve estar no `PATH` do sistema ou em `C:\Program Files\7-Zip\`.
    - Download: www.7-zip.org
3.  **WinRAR**: O executável (`Rar.exe`) deve estar no `PATH` do sistema ou em `C:\Program Files\WinRAR\`.
    - Download: www.win-rar.com

> **Nota**: O script tentará encontrar esses programas automaticamente. Se eles não forem encontrados, os algoritmos correspondentes serão ignorados.

## Estrutura de Diretórios

O projeto espera a seguinte estrutura de diretórios para funcionar corretamente:

```
seu-repositorio/
├── comprimir.py
├── datasets/
│   ├── Dataset_Texto/
│   │   ├── arquivo1.txt
│   │   └── ...
│   ├── Dataset_Imagens/
│   │   ├── imagem1.jpg
│   │   └── ...
│   └── Dataset_Misto/
│       ├── documento.pdf
│       ├── foto.png
│       └── ...
└── resultados/
    └── (será criado pelo script)
```

Coloque os arquivos de cada tipo de dado dentro das respectivas pastas em `datasets/`.

## Configuração

Você pode customizar o comportamento do benchmark editando as constantes no início do arquivo `comprimir.py`:

- `NUM_REPETICOES`: Número de vezes que cada teste (compressão + descompressão) será executado e medido. (Padrão: `10`)
- `WARMUP_RUNS`: Número de execuções iniciais que serão descartadas para "aquecer" o cache do sistema. (Padrão: `1`)
- `DATASETS`: Um dicionário que mapeia o nome do dataset para o nome da pasta correspondente dentro de `datasets/`. Você pode adicionar ou remover datasets aqui.

```python
# Exemplo de configuração no script
NUM_REPETICOES = 10
WARMUP_RUNS = 1

DATASETS = {
    "Texto Puro": "Dataset_Texto",
    "Imagens": "Dataset_Imagens",
    "Misto": "Dataset_Misto",
}
```

## Como Usar

1.  Clone este repositório.
2.  Instale os pré-requisitos.
3.  Popule as pastas dentro do diretório `datasets/` com os arquivos que você deseja testar.
4.  Abra um terminal na pasta raiz do projeto e execute o script:

    ```bash
    python comprimir.py
    ```

5.  Aguarde a conclusão do experimento. O progresso será exibido no terminal.

## Saída

Ao final da execução, um arquivo chamado `resultados_compressao.csv` será criado no diretório `resultados/`.

As colunas do CSV são:

- **Dataset**: Nome do conjunto de dados testado.
- **Algoritmo**: `ZIP`, `7Z` ou `RAR`.
- **Repeticao**: O número da repetição do teste para aquele algoritmo e dataset.
- **Arquivos no Dataset**: Quantidade total de arquivos no dataset original.
- **Tamanho Original (MB)**: Tamanho total do dataset antes da compressão.
- **Tamanho Comprimido (MB)**: Tamanho do arquivo gerado após a compressão.
- **Taxa de Compressao (%)**: Percentual de redução de tamanho.
- **Tempo de Compressao (s)**: Tempo gasto para comprimir os arquivos.
- **Tempo de Descompressao (s)**: Tempo gasto para extrair os arquivos.