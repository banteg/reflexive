# Reflexive Downloads

## Source Record

- Source id: `reflexive_downloads`
- Repo-local path: `artifacts/sources/reflexive_downloads`
- Original path: `/Users/banteg/Downloads/Reflexive`
- Source type: suspected original installer corpus
- Status: registered, pending readable access

## Initial Analysis

This source is promising because it is separate from the known 2008 Florian/TopBancuri repack and
may contain original Reflexive-distributed installers.

What is confirmed so far:

- `/Users/banteg/Downloads/Reflexive` exists and is a directory.
- A repo-local symlink at `artifacts/sources/reflexive_downloads` points to that location.
- The current process still cannot enumerate the directory contents. Both shell `ls` and Python
  `Path.iterdir()` fail with `Operation not permitted`.

What is not confirmed yet:

- file count
- filename scheme
- installer formats
- publisher signatures or PE version metadata
- overlap or divergence relative to the `archive_org_repack` source

## Working Implications

The source should be treated as registered but not yet ingested. The symlink gives the repo a
stable local path for future scripts and notes, but it does not bypass macOS privacy controls on
`Downloads`.

## Next Steps Once Readable

- inventory filenames, extensions, and hashes
- compare title coverage against the repack bundles and extracted game list
- classify installer technologies such as MSI, Inno Setup, InstallShield, NSIS, or custom
  Reflexive stubs
- extract signer, version, and timestamp metadata from representative installers
- prioritize titles that can improve the remaining unsupported unwrapper cases
