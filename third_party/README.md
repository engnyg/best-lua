# Third-party: Deobfuscator-Luraph-V15

- Source: https://github.com/caomod2077/Deobfuscator-Luraph-V15  (commit 892b48ac200e9deda6cd6fd3142bf66abed393c6)
- License: MIT (see Deobfuscator-Luraph-V15/LICENSE)
- Copied unmodified, except the following were left out: `.git`, `bin/*.exe` (Windows binaries), the five donation images (`*.jpg`).
- To run on Linux put official Luau builds `luau` and `luau-ast` into `bin/` (https://github.com/luau-lang/luau/releases), then:
  `node deob.js ../../decoded/combined.lua -o out.lua`

Result on `decoded/combined.lua`: detected as "unknown obfuscator (behaviour trace only)"; the run timed out (90 s and 400 s) with an empty output.
