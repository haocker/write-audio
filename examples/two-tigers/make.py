# -*- coding: utf-8 -*-
"""《两只老虎 · 午夜电波》— 童谣《两只老虎》(Frère Jacques) 电子二创。

改编手法（全部显式写在本乐谱里，无自动作曲、无随机）：
  1. 调性   C 大调 → A 小调（旋律整体下行小三度：do re mi → la si do）
  2. 编配   合成器舞曲：鼓组 / 合成贝斯 / 和声垫 / 琶音 / 电钢 / 钟琴
  3. 节奏   副歌切分与句尾加花；bridge 拉宽成长音；收尾为原创下行终止式
  4. 和声   Am - F - C - C - F - Dm7 - E7 - Am（8 小节循环，E7 的 G# 给童谣一点夜色）

结构（80 小节 / 124 BPM ≈ 2 分 37 秒）：
  intro 1-8 | drop A 9-24 | break 25-32 | drop B 33-48
  bridge 49-56 | drop C 57-72 | outro 73-80

运行：
    python make.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "..", "runtime"))

import write_audio as ca

BPM = 124.0
BPB = 4
BARS = 81            # 80 小节结构 + 最后和声垫的自然释放

song = ca.Song(bpm=BPM, beats_per_bar=BPB, tail=1.0)

# 8 小节和声循环：句7 挂 E7（悬留）→ 句8 落 Am（解决）
PROG = ["Am", "F", "C", "C", "F", "Dm7", "E7", "Am"]
ROOTS = {"Am": 33, "F": 29, "C": 36, "Dm7": 38, "E7": 28}


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
rhodes = song.track("rhodes", name="rhodes", gain_db=-8.0, pan=-0.15)
bell = song.track("bell", name="bell", gain_db=-9.0, pan=0.3)
hint = song.track("bell", name="hint", gain_db=-12.0, pan=0.35)
pad = song.track("pad", gain_db=-14.0)
vinyl = song.track("vinyl", gain_db=-24.0)
riser = song.track("riser", gain_db=-7.0)
whoosh = song.track("whoosh", gain_db=-10.0)

song.sidechain("kick", "bass", depth_db=-6.5, release=0.16)
song.sidechain("kick", "pad", depth_db=-5.0, release=0.22)
song.sidechain("kick", "arp", depth_db=-4.5, release=0.14)

song.length(bars=BARS)
song.fade(out_seconds=4.0)               # 结尾 4 秒渐出（平顺收场）

# ================================================================ 编曲工具箱


def kicks_4(bar, vel=1.0):
    for b in range(BPB):
        kick.hit(beat(bar, b), vel)


def claps_24(bar, vel=1.0):
    clap.hit(beat(bar, 1), vel)
    clap.hit(beat(bar, 3), vel)


def hats_off(bar, hi=0.9, lo=0.38):
    """House 律动：主拍弱、反拍强。"""
    for b in range(BPB):
        hat.hit(beat(bar, b), lo)
        hat.hit(beat(bar, b + 0.5), hi)


def hats_16(bar, hi=0.62, lo=0.32):
    for i in range(16):
        hat.hit(beat(bar, i * 0.25), hi if i % 2 == 0 else lo)


def bass_8(bar, patt=None):
    """八分滚动贝斯；patt 为相对根音的半音偏移。"""
    base = ROOTS[chord_of(bar)]
    if patt is None:
        patt = [0, 0, 0, 0, 0, 0, 0, 12]
    for i, v in enumerate(patt):
        bass.note(beat(bar, i * 0.5), base + v, 0.42)


def bass_hold(bar, dur=3.5):
    bass.note(beat(bar), ROOTS[chord_of(bar)], dur)


def pad_bar(bar, octv=3):
    """一小节长的 pad（加高八度根音）—— 逐小节精确对齐和弦进行。"""
    ch = ca.chord(chord_of(bar), octv)
    pad.note(beat(bar), ch + [ch[0] + 12], BPB)


def arp_play(bar, patt, step):
    """音型值：0/1/2=低区和弦音，3/4/5=+1 八度，6/7/8=+2 八度；None=休止。"""
    ch = ca.chord(chord_of(bar), 3)
    for i, v in enumerate(patt):
        if v is None:
            continue
        octv, idx = divmod(int(v), 3)
        arp.note(beat(bar, i * step), ch[idx] + 12 * octv, step * 1.1)


def place(track, bar0, bars):
    """把旋律块 {相对小节: [(小节内拍, 音名, 时值), ...]} 放到 bar0 起的连续小节里。"""
    for k in sorted(bars):
        for (b, name, dur) in bars[k]:
            track.note(beat(bar0 + k - 1, b), name, dur)


# ================================================================ 主题旋律
# 原曲（C 大调）1 2 3 1 | … → 二创（A 小调）A B C A | …（音级保留、调性小调化）

T = {   # 主题：忠实原节奏
    1: [(0, "A4", 1), (1, "B4", 1), (2, "C5", 1), (3, "A4", 1)],
    2: [(0, "A4", 1), (1, "B4", 1), (2, "C5", 1), (3, "A4", 1)],
    3: [(0, "C5", 1), (1, "D5", 1), (2, "E5", 2)],
    4: [(0, "C5", 1), (1, "D5", 1), (2, "E5", 2)],
    5: [(0, "E5", 0.5), (0.5, "F5", 0.5), (1, "E5", 0.5), (1.5, "D5", 0.5),
        (2, "C5", 0.5), (2.5, "A4", 1)],
    6: [(0, "E5", 0.5), (0.5, "F5", 0.5), (1, "E5", 0.5), (1.5, "D5", 0.5),
        (2, "C5", 0.5), (2.5, "A4", 1)],
    7: [(0, "A4", 1), (1, "E4", 1), (2, "A4", 2)],
    8: [(0, "A4", 1), (1, "E4", 1), (2, "A4", 2)],
}

T_PLUS = {   # 副歌花版：切分 + 句尾延伸 + 加花
    1: [(0, "A4", 1), (1, "B4", 1), (2, "C5", 1), (3, "A4", 1)],
    2: [(0, "A4", 1), (1, "B4", 1), (2, "C5", 0.5), (2.5, "D5", 0.5), (3, "C5", 1)],
    3: [(0, "C5", 1), (1, "D5", 1), (2, "E5", 1), (3, "G5", 1)],
    4: [(0, "C5", 0.5), (0.5, "D5", 0.5), (1, "E5", 2), (3, "G5", 1)],
    5: [(0, "E5", 0.5), (0.5, "F5", 0.5), (1, "E5", 0.5), (1.5, "D5", 0.5),
        (2, "C5", 0.5), (2.5, "A4", 0.5), (3, "B4", 0.5), (3.5, "C5", 0.5)],
    6: [(0, "E5", 0.5), (0.5, "F5", 0.5), (1, "E5", 0.5), (1.5, "D5", 0.5),
        (2, "C5", 0.5), (2.5, "D5", 0.5), (3, "E5", 1)],
    7: [(0, "A4", 1), (1, "E4", 1), (2, "A4", 1), (3, "B4", 1)],
    8: [(0, "C5", 1), (1, "B4", 1), (2, "A4", 2)],
}

T_SOFT = {   # 电钢抒情宽版（breakdown）
    1: [(0, "A4", 2), (2, "C5", 2)],
    2: [(0, "B4", 2), (2, "A4", 2)],
    3: [(0, "C5", 2), (2, "E5", 2)],
    4: [(0, "D5", 1), (1, "C5", 1), (2, "E5", 2)],
    5: [(0, "E5", 1), (1, "F5", 1), (2, "E5", 1), (3, "D5", 1)],
    6: [(0, "C5", 1), (1, "A4", 1), (2, "C5", 2)],
    7: [(0, "A4", 2), (2, "E4", 2)],
    8: [(0, "A4", 3)],
}

T_STRETCH = {   # bridge：拉伸成长音（保留轮廓）
    1: [(0, "A4", 2.5), (2.5, "B4", 1.5)],
    2: [(0, "C5", 2.5), (2.5, "A4", 1.5)],
    3: [(0, "C5", 2.5), (2.5, "D5", 1.5)],
    4: [(0, "E5", 4)],
    5: [(0, "E5", 2.5), (2.5, "F5", 1.5)],
    6: [(0, "E5", 2.5), (2.5, "D5", 1.5)],
    7: [(0, "C5", 2.5), (2.5, "A4", 1.5)],
    8: [(0, "B4", 4)],
}

T_FINAL = {   # 收尾：加花 + 原创下行终止式
    1: [(0, "A4", 1), (1, "B4", 1), (2, "C5", 1), (3, "A4", 1)],
    2: [(0, "A4", 1), (1, "B4", 1), (2, "C5", 1), (3, "A4", 1)],
    3: [(0, "C5", 1), (1, "D5", 1), (2, "E5", 1), (3, "G5", 1)],
    4: [(0, "C5", 0.5), (0.5, "D5", 0.5), (1, "E5", 3)],
    5: [(0, "E5", 0.5), (0.5, "F5", 0.5), (1, "E5", 0.5), (1.5, "D5", 0.5),
        (2, "C5", 0.5), (2.5, "A4", 0.5), (3, "B4", 0.5), (3.5, "C5", 0.5)],
    6: [(0, "D5", 0.5), (0.5, "C5", 0.5), (1, "B4", 0.5), (1.5, "A4", 0.5), (2, "C5", 2)],
    7: [(0, "A4", 1), (1, "E4", 1), (2, "A4", 2)],
    8: [(0, "D5", 0.5), (0.5, "C5", 0.5), (1, "B4", 0.5), (1.5, "A4", 2.5)],
}

T_OUTRO = {   # outro：下行远去
    1: [(0, "E5", 2), (2, "D5", 2)],
    2: [(0, "C5", 2), (2, "A4", 2)],
    3: [(0, "A4", 4)],
}

# ================================================================ 段落编配

# ---------------- intro（1-8）：氛围渐入 ----------------
vinyl.note(beat(1))                      # 黑胶底噪，铺到曲终
for n in range(1, 9):
    pad_bar(n, octv=2 if n <= 4 else 3)
for n in range(1, 5):
    arp_play(n, [1, 2, 4, 2], 1.0)       # 四分缓慢琶音
place(hint, 5, {                         # 主题残影（八音盒）
    1: [(0, "A4", 2), (2, "B4", 2)],
    2: [(0, "C5", 2), (2, "A4", 2)],
    3: [(0, "C5", 2), (2, "D5", 2)],
    4: [(0, "B4", 1.5), (1.5, "C5", 1), (2.5, "D5", 1.5)],
})
for n in range(5, 7):
    kick.hit(beat(n, 0), 0.6)
    kick.hit(beat(n, 2), 0.6)
for n in range(7, 9):
    kicks_4(n, 0.75)
    hats_off(n, 0.5, 0.25)
riser.note(beat(7), None, 8)
whoosh.note(beat(8, 3))

# ---------------- drop A（9-24）：主题呈现 ----------------
crash.hit(beat(9), 0.9)
crash.hit(beat(17), 0.85)
for n in range(9, 25):
    kicks_4(n)
    bass_8(n)
    pad_bar(n)
    if n < 21:
        hats_off(n, 0.85, 0.35)
    else:
        hats_16(n, 0.55, 0.28)           # 后半：16 分爬升
for n in range(9, 25):
    arp_play(n, [1, 2, 4, 2, 1, 2, 4, 5], 0.5)
place(lead, 9, T)
place(lead, 17, T)
bell.note(beat(16, 3), "C5", 1)
bell.note(beat(24, 3), "E5", 1)

# ---------------- break（25-32）：电钢抒情（半能量） ----------------
place(rhodes, 25, T_SOFT)
for n in range(25, 33):
    pad_bar(n, octv=2 if n <= 28 else 3)
for n in range(25, 29):
    bass_hold(n)                         # 前 4 小节撤鼓：只剩电钢 + 和声垫 + 贝斯长音
for n in range(29, 31):
    kicks_4(n, 0.75)                     # 鼓逐层回归
    hats_off(n, 0.5, 0.22)
for n in range(31, 33):
    kicks_4(n, 0.85)
    claps_24(n, 0.7)
    hats_off(n, 0.6, 0.28)
    bass_8(n)
for i in range(8):                       # 滚奏推入 drop B
    snare.hit(beat(32, 2 + i * 0.25), 0.2 + 0.75 * (i / 7.0))
riser.note(beat(31), None, 8)

# ---------------- drop B（33-48）：副歌全开 ----------------
crash.hit(beat(33), 1.0)
crash.hit(beat(41), 0.95)
for n in range(33, 49):
    kicks_4(n)
    claps_24(n)
    hats_16(n, 0.6, 0.32)
    bass_8(n, patt=[0, 0, 12, 0, 0, 0, 7, 0])
    pad_bar(n)
    arp_play(n, [3, 4, 5, 4, 3, 4, 5, 6, 3, 4, 5, 6, 5, 4, 3, 2], 0.25)
place(lead, 33, T_PLUS)
place(lead, 41, T_PLUS)
bell.note(beat(33), "A5", 0.8)
bell.note(beat(40, 3), "A5", 1)
bell.note(beat(44, 3), "G5", 1)
bell.note(beat(48, 3), "E5", 1)

# ---------------- bridge（49-56）：拉伸变奏 + 渐强 ----------------
for n in range(49, 57):
    kicks_4(n, 0.9)
    pad_bar(n)
place(lead, 49, T_STRETCH)
for n in range(49, 53):
    bass_hold(n)
    arp_play(n, [1, 2, 4, 2], 1.0)
for n in range(53, 57):
    bass_8(n)
bell.note(beat(52, 3), "A5", 1)
riser.note(beat(55), None, 8)
for i in range(16):                      # 32 分滚奏推入 drop C
    snare.hit(beat(56, 2 + i * 0.125), 0.15 + 0.8 * (i / 15.0))

# ---------------- drop C（57-72）：最强 + 收尾 ----------------
crash.hit(beat(57), 1.0)
crash.hit(beat(65), 0.95)
for n in range(57, 73):
    kicks_4(n)
    claps_24(n)
    hats_16(n, 0.62, 0.32)
    bass_8(n, patt=[0, 0, 12, 0, 0, 0, 7, 0])
    pad_bar(n)
    arp_play(n, [4, 5, 7, 5, 4, 5, 7, 5, 4, 5, 7, 5, 7, 5, 4, 2], 0.25)
place(lead, 57, T)
place(lead, 65, T_FINAL)
bell.note(beat(65), "A5", 0.8)
bell.note(beat(71, 3), "B5", 1)
bell.note(beat(72, 2), "A5", 1.5)

# ---------------- outro（73-80）：逐层退出 ----------------
for n in range(73, 81):
    pad_bar(n)
place(lead, 73, T_OUTRO)
for n in range(73, 75):
    kicks_4(n, 0.95)
    bass_hold(n)
kick.hit(beat(75, 0), 0.8)
kick.hit(beat(75, 2), 0.7)
bass_hold(75)
kick.hit(beat(76, 0), 0.6)
hint.note(beat(76), "A5", 2)
hint.note(beat(78), "E5", 2)

# ================================================================ 渲染

if __name__ == "__main__":
    import time
    t0 = time.time()
    out_dir = os.path.join(HERE, "out")
    rep = song.render(out=os.path.join(out_dir, "two-tigers.mp3"),
                      stems=os.path.join(out_dir, "stems"),
                      title="两只老虎（二创：午夜电波）")
    print("bars=%s seconds=%s lufs=%s tp=%s" % (rep["bars"], rep["seconds"], rep["lufs"], rep["tp"]))
    for t in rep["tracks"]:
        print("  %-8s %-7s %5d notes  peak %s dB" % (t["name"], t["inst"], t["notes"], t["peak_db"]))
    print("render %.1fs（含打包总计 %.1fs）" % (rep["render_seconds"], time.time() - t0))
