import pickle
from concurrent.futures import ProcessPoolExecutor
from itertools import chain

import pandas as pd


# --- top-level worker so it's picklable ---
def _rows_for_gene(args):
    gene, gene_cols, phen_cols, phen_key = args
    base = [gene[k] for k in gene_cols]
    return [base + [phen[k] for k in phen_cols] for phen in gene.get(phen_key, [])]


def build_gene_disease_parallel(
    data, gene_cols, phen_cols, phen_key="phenotypes", max_workers=None, chunksize=256
):
    """
    Parallel construction of the gene_disease table.

    Parameters
    ----------
    data : Iterable[dict]
        Each item is a gene dict containing `phen_key` list of phenotype dicts.
    gene_cols : Sequence[str]
    phen_cols : Sequence[str]
    phen_key : str
    max_workers : int | None
        Defaults to number of CPUs.
    chunksize : int
        Batch size per worker for lower overhead on large datasets.

    Returns
    -------
    list[list]
        Flattened list of [gene_fields..., phen_fields...]
    """
    # Tuples are slightly cheaper to pickle than lists
    gene_cols = tuple(gene_cols)
    phen_cols = tuple(phen_cols)

    with ProcessPoolExecutor(max_workers=max_workers) as ex:
        mapped = ex.map(
            _rows_for_gene,
            ((gene, gene_cols, phen_cols, phen_key) for gene in data),
            chunksize=chunksize,
        )
        return list(chain.from_iterable(mapped))


if __name__ == "__main__":
    gene_cols = ["mim_number", "approved_gene_symbol", "entrez_gene_id"]
    phen_cols = ["mim_number", "name", "mapping_key"]
    phen_key = "phenotypes"

    with open("output.pickle", "rb") as f:
        data = pickle.load(f)
    gene_disease = build_gene_disease_parallel(
        data, gene_cols, phen_cols, phen_key=phen_key, max_workers=None
    )

    df = pd.DataFrame(
        gene_disease,
        columns=["gene_mim_number"]
        + gene_cols[1:]
        + ["phen_mim_number"]
        + phen_cols[1:],
    )

    def report(step):
        """Print a formatted summary of dataset size and diversity."""
        print(f"\n🧩 {step}")
        print(f"{'-'*(len(step)+3)}")
        print(f"  Associations : {len(df):,}")
        print(f"  Unique genes : {df['gene_mim_number'].nunique():,}")
        print(f"  Unique diseases : {df['phen_mim_number'].nunique():,}")

    # Initial dataset
    report("Initial dataset")

    # 1) remove rows where phenotype name starts with '?'
    df = df[~df["name"].str.startswith("?", na=False)]
    report("After removing uncertain disease names ('?')")

    # 2) keep mapping == 1 or 3 (molecularly or positionally mapped)
    df = df[pd.to_numeric(df["mapping_key"], errors="coerce") == 3]
    report("After keeping mapping keys = 3")

    # 3) drop the phenotype name column
    df = df.drop(columns=["name"])

    # 4) keep phenotypes with ≥3 genes (count distinct gene_mim_number per phenotype)
    gene_counts = df.groupby("phen_mim_number")["entrez_gene_id"].transform("nunique")
    df = df[gene_counts >= 3].reset_index(drop=True)
    report("After keeping diseases with ≥3 associated genes")

    print("\n✅ Dataset filtering complete.")
