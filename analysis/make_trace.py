#!/usr/bin/env python3
"""Build a sandbox trace runner (Luau) from ../decoded/inner.luau + data.bin.

  python3 make_trace.py log  > trace_log.luau   # stage1 decode, stage2 run, log every global/call the VM touches
  python3 make_trace.py pc   > trace_pc.luau    # also record pc:opcode of the interpreter loop (window at n=3,000,000)

Run with an official Luau build:  luau -O2 --codegen trace_log.luau      (use `timeout`, it never finishes by itself)
All Roblox APIs are fake logging proxies; only string/table/math/bit32/buffer/... are real.
"""
import os, sys
here = os.path.dirname(os.path.abspath(__file__))
inner = open(os.path.join(here, '..', 'decoded', 'inner.luau'), 'rb').read().decode('latin1')
data = open(os.path.join(here, '..', 'decoded', 'data.bin'), 'rb').read()
mode = sys.argv[1] if len(sys.argv) > 1 else 'log'

lvl = 4
while ']' + '=' * lvl + ']' in inner: lvl += 1
eq = '=' * lvl
if mode == 'pc':
    needle = 'while true do local k,R=I[b];if k>=85 then'   # interpreter loop variant #38
    assert inner.count(needle) == 1
    inner = inner.replace(needle, 'while true do local k,R=I[b];__P(b,k);if k>=85 then', 1)

lua = f'local INNER = [{eq}[{inner}]{eq}]\nlocal DATA = buffer.fromstring("' + ''.join('\\%03d' % x for x in data) + '")\n'
lua += r'''
local ops, MAXOPS, printed = 0, 400000, 0
local function out(s) if printed < 800 then printed += 1; print(s) end end
local last
local function L(s) ops += 1; if ops > MAXOPS then error("STOP", 0) end; if s ~= last then last = s; out(s) end end
local function fmt(v)
    local t = type(v)
    if t == "string" then return string.format("%q", #v > 300 and v:sub(1, 300) .. "..." or v)
    elseif t == "number" or t == "boolean" or t == "nil" then return tostring(v)
    elseif t == "table" and rawget(v, "__path") then return rawget(v, "__path") else return t end
end
local mk
mk = function(path)
    local p = {}; rawset(p, "__path", path)
    return setmetatable(p, {
        __index = function(_, k) local np = path .. "." .. tostring(k); L("get " .. np); return mk(np) end,
        __newindex = function(_, k, v) L("set " .. path .. "." .. tostring(k) .. " = " .. fmt(v)) end,
        __call = function(_, ...) local a = table.pack(...); local parts = {}
            for i = 1, a.n do parts[i] = fmt(a[i]) end
            L("call " .. path .. "(" .. table.concat(parts, ", ") .. ")"); return mk(path .. "()") end,
        __tostring = function() return path end, __len = function() L("len"); return 0 end,
        __eq = function() ops += 1; return false end, __lt = function() L("cmp"); return false end, __le = function() L("cmp"); return false end,
        __add = function() L("arith"); return 0 end, __sub = function() L("arith"); return 0 end,
        __mul = function() L("arith"); return 0 end, __div = function() L("arith"); return 0 end,
    })
end
local std = {string=string, table=table, math=math, bit32=bit32, buffer=buffer, type=type, typeof=typeof, tostring=tostring,
 tonumber=tonumber, select=select, pairs=pairs, ipairs=ipairs, next=next, pcall=pcall, xpcall=xpcall, error=error, assert=assert,
 setmetatable=setmetatable, getmetatable=getmetatable, rawget=rawget, rawset=rawset, rawequal=rawequal, rawlen=rawlen,
 unpack=table.unpack, coroutine=coroutine, utf8=utf8, vector=vector, os={time=os.time, clock=os.clock}, debug=debug,
 UDim=UDim, UDim2=UDim2, Vector3=Vector3, Vector2=Vector2, Color3=Color3, Rect=Rect}
std.wait = function() L("wait"); return 0 end
std.task = {wait=function() L("task.wait"); return 0 end, spawn=function() L("task.spawn") end, defer=function() L("task.defer") end, delay=function() L("task.delay") end}
std.loadstring = function(s) L("loadstring"); return function() end end
std.load = std.loadstring
std.setfenv = function() end
std.identifyexecutor = function() return "Wave", "1.0.0" end
local env
env = setmetatable({}, {
    __index = function(_, k)
        if k == "getfenv" then return function() return env end end
        local v = std[k]; if v ~= nil then return v end
        L("global " .. tostring(k)); return mk(tostring(k))
    end,
    __newindex = function(_, k, v) L("setglobal " .. tostring(k)); std[k] = v end,
})
'''
if mode == 'pc':
    lua += r'''
local n, seq = 0, {}
function __P(pc, op)
    n += 1
    if n >= 3000000 and n < 3000320 then seq[#seq+1] = pc .. ":" .. op
    elseif n == 3000320 then print("SEQ " .. table.concat(seq, " ")); error("STOP", 0) end
end
std.__P = __P
'''
lua += r'''
local fn = loadstring(INNER)
setfenv(fn, env)
print("== stage1: decode ==")
local ok, main = xpcall(fn, tostring, DATA)
print("stage1", ok, type(main) == "function" and "function" or tostring(main))
if ok and type(main) == "function" then
    print("== stage2: run main ==")
    print("stage2", xpcall(main, tostring))
end
'''
sys.stdout.write(lua)
