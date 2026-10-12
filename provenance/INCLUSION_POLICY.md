# Private-library inclusion policy

This tree was created from a deliberate allowlist. The initial private Git
history was authorized only after the L1 snapshot and local validation. New
files remain subject to explicit review before staging.

## Included in L1

- `src/reversede/` and the temporary compatibility adapter `src/reverseda_ai/`;
- deterministic library tests under `tests/`;
- package metadata and preserved MIT license;
- library-focused documentation and minimal synthetic examples;
- curated synthetic notebooks and IDE-neutral environment configuration;
- CI configuration with no publication step;
- snapshot and policy documents under `provenance/`.

## Excluded by default

- `.venv/`, `work/`, caches, build directories, `dist/`, and `egg-info`;
- raw or processed datasets;
- supplied PDFs, ZIP archives, extracted document text, and templates;
- study notebooks, notebooks with private data, and unreviewed stored outputs;
- frozen splits, predictions, metrics, profiling reports, and scientific logs;
- manuscript sources, PDFs, figures, and compilation logs;
- files containing personal absolute paths or environment-specific executables;
- credentials, secrets, private keys, local `.env` files, or access tokens.

## Separate preserved source

The excluded study remains in the sibling source directory recorded in
`SOURCE_SNAPSHOT.json`. Exclusion from this library is not deletion. Scientific
reproduction material requires a separate provenance and licensing review.

## Gate before any private remote

1. Review every staged path against this allowlist.
2. Run a specialized secret scan with values suppressed in reports.
3. Confirm authorship, contribution, copyright, and third-party licenses.
4. Confirm the destination is GitHub **Private** and access is least-privilege.
5. Obtain explicit user authorization before repository creation and again
   before the first push.
