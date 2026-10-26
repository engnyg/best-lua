# folk.luau decoded layers

Layers recovered from `folk.luau` (Femboy Obfuscator v16.3 -> Luraph VM).
Nothing here was executed against a real game; the outer decoder was run in a stub environment.

- `inner.luau`   - 164214 B, Luraph VM source (layer 2). Takes `data.bin` as its argument.
- `data.bin`     - 277567 B, VM bytecode buffer passed to layer 2.
- `combined.lua` - layer 2 + `data.bin` embedded, calls the decoded main function. Do NOT run in a real client.
