# jnkie payload

Main script delivered by the key system after redeeming a key in `folk.luau`.

- Source: https://cdn.jnkie.com/912611b5afd3a66af4f7be78100c43c2668a9936f0317ee2dcf6ccd02cba8055.lua
- Observed flow (request log from the executor): `POST api.jnkie.com/api/v1/whitelist/verifyOpen` -> `POST api.jnkie.com/api/v1/luascripts/delivery/...` -> `GET cdn.jnkie.com/<hash>.lua`
- Header: "protected using Luraph Obfuscator v15.1"
- Size: 1223219 bytes, sha256: 912611b5afd3a66af4f7be78100c43c2668a9936f0317ee2dcf6ccd02cba8055
- Still obfuscated. Not executed outside a sandbox. Do NOT run in a real client unless you trust it.
