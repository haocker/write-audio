# -*- coding: utf-8 -*-
"""《Night Drive》— write_audio v0.2 示例：AI 手写乐谱（引擎只管渲染）。

93 小节 / A 小调 / 124 BPM ≈ 3 分钟。全部音符、和弦、织体都在本文件里
显式写出（无自动作曲、无随机）：把这支曲子交给任何渲染器都能复现。

结构：intro 8 → build 8 → verse 16 → chorus 16 → break 8 → verse 16 → chorus 16 → outro 5

运行：
    python make.py                       # 渲染到 out/night-drive.mp3
    python -m write_audio make.py --check  # 只看乐谱摘要
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "runtime"))

import write_audio as ca

# ================================================================ 总设定

BPM = 124.0
BPB = 4
BARS = 93

song = ca.Song(bpm=BPM, beats_per_bar=BPB, tail=1.0)

# 和弦进行：每小节一个（4 小节循环）—— Am - F - C - G
PROG = ["Am", "F", "C", "G"]
# 低音根音（MIDI）：A1 / F1 / C2 / G1
ROOTS = {"Am": 33, "F": 29, "C": 36, "G": 31}


def beat(bar, b=0.0):
    """第 bar 小节（1 基）内第 b 拍的绝对拍位置。"""
    return (bar - 1) * BPB + b


def chord_of(bar):
    return PROG[(bar - 1) % len(PROG)]


# ================================================================ 轨道

kick = song.track("kick", gain_db=0.0)
clap = song.track("clap", gain_db=-4.0)
hat = song.track("hat", gain_db=-10.0)
snare = song.track("snare", gain_db=-8.0)
crash = song.track("crash", gain_db=-9.0)
bass = song.track("bass", gain_db=-3.0)
arp = song.track("pluck", name="arp", gain_db=-8.0, pan=-0.25)
lead = song.track("pluck", name="lead", gain_db=-6.0, pan=0.2)
rh = song.track("rhodes", name="rhodes", gain_db=-9.0, pan=-0.15)
bell = song.track("bell", name="bell", gain_db=-9.0, pan=0.3)
pad = song.track("pad", gain_db=-14.0)
vinyl = song.track("vinyl", gain_db=-22.0)
riser = song.track("riser", gain_db=-7.0)

# 侧链：底鼓压低低音/和声/琶音（电子乐呼吸感）
song.sidechain("kick", "bass", depth_db=-6.5, release=0.16)
song.sidechain("kick", "pad", depth_db=-5.0, release=0.22)
song.sidechain("kick", "arp", depth_db=-4.5, release=0.14)

song.length(bars=BARS)
song.fade(out_seconds=3.5)      # 结尾 3.5 秒渐出（平顺收场）

# ================================================================ 编曲工具箱


def kicks_4(bar, vel=1.0):
    for b in range(BPB):
        kick.hit(beat(bar, b), vel)


def claps_24(bar, vel=1.0):
    clap.hit(beat(bar, 1), vel)
    clap.hit(beat(bar, 3), vel)


def hats_8(bar, hi=0.75, lo=0.4):
    for i in range(8):
        hat.hit(beat(bar, i * 0.5), hi if i % 2 else lo)


def hats_16(bar, hi=0.62, lo=0.3):
    for i in range(16):
        hat.hit(beat(bar, i * 0.25), hi if i % 2 == 0 else lo)


def hats_off(bar, hi=0.9, lo=0.38):
    """House 律动：主拍弱、反拍强。"""
    for b in range(BPB):
        hat.hit(beat(bar, b), lo)
        hat.hit(beat(bar, b + 0.5), hi)


def bass_8(bar, cn=None, patt=None):
    """八分滚动贝斯；patt 逐位置给相对根音的半音偏移。"""
    base = ROOTS[cn or chord_of(bar)]
    if patt is None:
        patt = [0, 0, 0, 0, 0, 0, 0, 12]
    for i, v in enumerate(patt):
        bass.note(beat(bar, i * 0.5), base + v, 0.42)


def bass_hold(bar, dur=3.5, dn=None):
    bass.note(beat(bar), dn if dn is not None else ROOTS[chord_of(bar)], dur)


def arp_play(bar, patt, step):
    """按音型弹琶音。音型值：0/1/2=低区三和弦音，3/4/5=高八度，6/7/8=再高八度；None=休止。"""
    ch = ca.chord(chord_of(bar), 3)
    for i, v in enumerate(patt):
        if v is None:
            continue
        octv, idx = divmod(int(v), 3)
        arp.note(beat(bar, i * step), ch[idx] + 12 * octv, step * 1.1)


def pad_bar(bar, octv=3):
    """一小节长的 pad（含高八度根音）——逐小节精确对齐和弦进行。"""
    ch = ca.chord(chord_of(bar), octv)
    pad.note(beat(bar), ch + [ch[0] + 12], BPB)


def play_melody(track, bar0, cycles, mdict):
    """把 {循环内小节: [(小节内拍, 音名, 时值), ...]} 循环数遍（每遍覆盖 len(mdict) 小节）。"""
    for k in range(cycles * len(mdict)):
        for (b, name, dur) in mdict[k % len(mdict)]:
            track.note(beat(bar0 + k, b), name, dur)


# ================================================================ 段落编配

# ---------------- intro（1-8）：氛围铺垫，无鼓 ----------------
for n in range(1, 9):
    pad_bar(n, octv=2)
vinyl.note(beat(1))                       # 黑胶底噪：从开场铺到曲终
for n in range(1, 9):
    arp_play(n, [1, 2, 4, 2], 1.0)         # 4 分缓慢琶音

# ---------------- build（9-16）：渐强 ----------------
for n in range(9, 17):
    kicks_4(n)
    if n <= 12:
        hats_8(n)
        claps_24(n, 0.7 if n % 2 else 0.5)
    else:
        hats_16(n)
        claps_24(n)
    bass_8(n)
    if n <= 12:
        arp_play(n, [0, 1, 2, 1, 0, 1, 2, 1], 0.5)
for n in range(9, 17):
    pad_bar(n, octv=3)
# 15-16：滚奏渐强 + 扫频
for i in range(16):
    snare.hit(beat(15, 2 + i * 0.125), 0.22 + 0.78 * (i / 15.0))
riser.note(beat(15), None, 8)

# ---------------- verse（17-32）：主歌 ----------------
for n in range(17, 33):
    kicks_4(n)
    claps_24(n, 0.8)
    hats_off(n)
    bass_8(n)
    arp_play(n, [1, 2, 4, 2, 1, 2, 4, 5], 0.5)
for n in range(17, 33):
    pad_bar(n, octv=3)

M_VERSE = [
    [(0.5, "A4", 1.5), (2.0, "C5", 1.8)],
    [(0.0, "C5", 1.5), (2.0, "A4", 1.8)],
    [(0.5, "E5", 1.5), (2.0, "D5", 1.8)],
    [(0.0, "B4", 1.5), (2.0, "G4", 1.8)],
]
play_melody(rh, 17, 3, M_VERSE)
play_melody(rh, 29, 1, [
    [(0.5, "A4", 1.5), (2.0, "C5", 1.8)],
    [(0.0, "C5", 1.5), (2.0, "A4", 1.8)],
    [(0.5, "E5", 1.5), (2.0, "D5", 1.8)],
    [(0.0, "B4", 1.0), (1.5, "A4", 2.0)],      # 第四遍收主音
])
# 32 小节末：鼓花
for i in range(4):
    snare.hit(beat(32, 3 + i * 0.25), 0.4 + i * 0.2)

# ---------------- chorus（33-48）：副歌（全开） ----------------
crash.hit(beat(33))
crash.hit(beat(41))
for n in range(33, 49):
    kicks_4(n)
    claps_24(n)
    hats_16(n)
    bass_8(n, patt=[0, 0, 0, 12, 0, 0, 7, 0])
    arp_play(n, [3, 4, 5, 4, 3, 4, 5, 4, 3, 4, 5, 4, 3, 4, 5, 6], 0.25)
for n in range(33, 49):
    pad_bar(n, octv=3)

HOOK = [
    [(0.0, "E5", 0.7), (0.75, "C5", 0.7), (1.5, "A4", 2.4)],
    [(0.0, "C5", 0.7), (0.75, "B4", 0.7), (1.5, "C5", 2.4)],
    [(0.0, "D5", 0.7), (0.75, "C5", 0.7), (1.5, "B4", 0.45), (2.0, "A4", 1.9)],
    [(0.0, "B4", 0.9), (1.0, "G4", 2.9)],
    [(0.0, "A4", 0.7), (0.75, "C5", 0.7), (1.5, "E5", 2.4)],
    [(0.0, "F5", 0.7), (0.75, "E5", 0.7), (1.5, "D5", 2.4)],
    [(0.0, "C5", 0.7), (0.75, "E5", 0.7), (1.5, "D5", 0.45), (2.0, "C5", 1.9)],
    [(0.0, "B4", 0.9), (1.0, "A4", 2.9)],
]
play_melody(lead, 33, 2, HOOK)
bell.note(beat(36, 3.5), "A5", 1.0)     # 句尾亮色点缀
bell.note(beat(44, 3.5), "C6", 1.0)

# ---------------- break（49-56）：间奏（骤降） ----------------
crash.hit(beat(49))
for n in range(49, 53):
    pad_bar(n, octv=2)
for n in range(49, 53):
    bass_hold(n, 3.5)
BOSS = [
    [(0.0, "A4", 1.8), (2.0, "C5", 1.8)],
    [(0.0, "E5", 1.8), (2.0, "D5", 1.8)],
    [(0.0, "C5", 1.8), (2.0, "B4", 1.8)],
    [(0.0, "B4", 1.8), (2.0, "D5", 1.8)],
]
play_melody(bell, 49, 2, BOSS)
# 53-56：鼓逐级回归（避免从安静突然全奏）
for n in range(53, 57):
    kicks_4(n)
    if n >= 54:
        hats_8(n)
    if n >= 55:
        claps_24(n, 0.85)
        bass_8(n)
riser.note(beat(56), None, 4)

# ---------------- verse2（57-72）：主歌再现 ----------------
for n in range(57, 73):
    kicks_4(n)
    claps_24(n, 0.8)
    hats_off(n)
    bass_8(n)
    arp_play(n, [1, 2, 4, 2, 1, 2, 4, 5], 0.5)
for n in range(57, 73):
    pad_bar(n, octv=3)
play_melody(rh, 57, 4, M_VERSE)
bell.note(beat(60, 3.5), "E5", 1.0)      # 点缀
bell.note(beat(64, 3.5), "A5", 1.0)
bell.note(beat(68, 3.5), "E5", 1.0)
for i in range(4):
    snare.hit(beat(72, 3 + i * 0.25), 0.4 + i * 0.2)

# ---------------- chorus2（73-88）：副歌再现 ----------------
crash.hit(beat(73))
crash.hit(beat(81))
for n in range(73, 89):
    kicks_4(n)
    claps_24(n)
    hats_16(n)
    bass_8(n, patt=[0, 0, 0, 12, 0, 0, 7, 0])
    arp_play(n, [3, 4, 5, 4, 3, 4, 5, 4, 3, 4, 5, 4, 3, 4, 5, 6], 0.25)
for n in range(73, 89):
    pad_bar(n, octv=3)
play_melody(lead, 73, 2, HOOK)
bell.note(beat(76, 3.5), "A5", 1.0)
bell.note(beat(84, 3.5), "C6", 1.0)

# ---------------- outro（89-93）：收场 ----------------
for n in range(89, 94):
    pad_bar(n, octv=3)
kicks_4(89)
kicks_4(90)
bass_hold(89)
bass_hold(90)
bass_hold(91)
arp_play(89, [1, 2, 4, 2], 1.0)
arp_play(90, [1, 2, 4, 2], 1.0)
arp_play(91, [1, None, 4, None], 1.0)
bell.note(beat(89), "E5", 3.5)
bell.note(beat(90), "C5", 3.5)
bell.note(beat(91), "A4", 3.5)
bell.note(beat(92), "D5", 3.5)          # 92 = G 和弦
bell.note(beat(93), "A4", 3.5)          # 93 = Am 落定

# ================================================================ 渲染

if __name__ == "__main__":
    import time
    t0 = time.time()
    out_dir = os.path.join(HERE, "out")
    rep = song.render(out=os.path.join(out_dir, "night-drive.mp3"),
                      stems=os.path.join(out_dir, "stems"),
                      title="Night Drive (write_audio demo)")
    print("bars=%s seconds=%s lufs=%s tp=%s" % (rep["bars"], rep["seconds"], rep["lufs"], rep["tp"]))
    for t in rep["tracks"]:
        print("  %-8s %-7s %5d notes  peak %s dB" % (t["name"], t["inst"], t["notes"], t["peak_db"]))
    print("render %.1fs（含打包总计 %.1fs）" % (rep["render_seconds"], time.time() - t0))
