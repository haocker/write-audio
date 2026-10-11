# 写乐谱指南（write_audio v0.2）

引擎只做渲染；这支曲子好不好听，全看你写的乐谱。本文是方法与套路。

---

## 1. 时间模型

- 一切以**拍（beat）**为单位。`bpm=124` → 1 拍 = 60/124 = 0.4839 秒；一小节（4 拍）= 1.9355 秒。
- 第 n 小节（1 基）的起点 = `(n - 1) * beats_per_bar` 拍。建议在脚本里定义：

```python
def beat(bar, b=0.0):
    return (bar - 1) * 4 + b      # 4 = beats_per_bar
```

- 时长控制：`s.length(bars=93)` → 输出 = 93 × 小节秒数 + `tail`（默认 1.5s，乐尾释放缓冲）。
- 不设 length 时：自动取“最后一个音符的结束拍”。注意**音符 dur 会撑长曲长**（最后一小节的 pad 若 dur=8 拍，可能多用一小节）。

## 2. 音符写法

```python
t = s.track("bass")
t.note(0, "A1", 1.0, 1.0)          # at, pitch, dur（拍）, vel（0~1）
t.note(4)                           # 打击乐：在 4 拍处一击（无音高）
t.notes([
    (0, "A1", 0.5),                 # 元组
    (0.5, "A1"),                    # dur 缺省 = 乐器默认时值
    12,                              # 纯数字 = 打击乐音符
    {"at": 13, "pitch": "C2", "vel": 0.8},   # dict 写法
])
t.hit(2, vel=0.9)                   # 打击乐快捷
t.hits([0, 1, 2, 3])                # 打击乐批量
t.grid("x...x...x...x...", step=0.25)   # 网格谱
```

- `pitch`：音名（`"A3"` `"F#2"` `"Bb"`）或 MIDI 数值；`pad` 还可给列表（`ca.chord("Am7", 3)`）。
- 音效轨（`ding`/`whoosh` 等）的 `pitch` 是**半音移调**（数值，0 = 原位），不是音名。
- `grid` 谱面：每字符一步（`step` 拍），`x`/`X`/`1`/`*` = 击发；`|` 只做视觉分隔不推进；其他字符 = 空拍。

```python
kick.grid("x...|x...|x...|x...", step=0.25)   # 4/4 底鼓
hat.grid("x.x.x.x.x.x.x.x.", step=0.25)      # 8 分闭镲
```

## 3. 乐理工具

```python
ca.midi("A3")            # 57；也接受 MIDI 数值
ca.freq(57)              # 220.0
ca.chord("Am7", 3)       # [57, 60, 64, 67]（和弦名→MIDI；支持 C/E、F#m7b5、G7sus4、add9…）
ca.scale("A", "minor", 3)  # [57,59,60,62,64,65,67,69]（音阶 8 音，含高八度主音）
```

- 写贝斯/旋律时用 `ca.midi()` / `ca.scale()` / 和弦列表的索引运算（`ch[0]+12` 等）构造音高。
- 写 pad 时直接 `ca.chord(和弦名, 八度)`。

## 4. 编曲方法（各轨怎么写）

### 4.1 鼓组（kick / clap / snare / hat / crash）

常用模板（可直接改）：

```python
# 4/4 四踩（house/techno 地基）
for b in range(4):
    kick.hit(beat(bar, b))

# 2/4 拍拍手
clap.hit(beat(bar, 1)); clap.hit(beat(bar, 3))

# offbeat 闭镲（反拍强、正拍弱 = house 律动）
for b in range(4):
    hat.hit(beat(bar, b), 0.38)
    hat.hit(beat(bar, b + 0.5), 0.9)

# 16 分闭镲（强弱交替）
for i in range(16):
    hat.hit(beat(bar, i * 0.25), 0.62 if i % 2 == 0 else 0.3)
```

- 段落头（chorus/大段回归）用 `crash.hit(beat(bar))`。
- 进入副歌前用 snare roll：`for i in range(16): snare.hit(beat(bar, 2 + i * 0.125), 0.2 + 0.8*(i/15))`。
- 鼓 fill 只在小节末 1 拍，勿滥。

### 4.2 贝斯

- 八分滚动（电子乐主力）：

```python
def bass_8(bar, root_midi, patt=None):
    patt = patt or [0,0,0,0,0,0,0,12]      # 8 个半音偏移（最后一拍八度跳）
    for i, v in enumerate(patt):
        bass.note(beat(bar, i * 0.5), root_midi + v, 0.42)
```

- 根音建议 A1~C2 区（MIDI 29~36）；跳音用 +7（五度）/ +12（八度）。
- 副歌可换更有劲的型：`[0,0,0,12,0,0,7,0]`（第 4 个八度跳、第 7 个五度）。
- 全曲基调：跟和弦根音走（每小节换根）。

### 4.3 和声（pad）

- **每小节一个 pad，与和弦循环逐小节对齐**（踩过坑：2 小节长音 pad 会盖错和弦）。

```python
PROG = ["Am", "F", "C", "G"]          # 每小节一个，循环
ch = ca.chord(PROG[(bar - 1) % 4], 3)
pad.note(beat(bar), ch + [ch[0] + 12], 4)   # 4 拍；加高八度根音更满
```

- 不同段落可用不同八度（intro/break 低八度 soundbed，主段中八度）。

### 4.4 琶音（arp，用 pluck）

音型用“索引”表示：`0/1/2` = 低区三和弦音，`3/4/5` = 高八度，`6/7/8` = 再高八度，`None` = 休止：

```python
def arp_play(bar, patt, step):
    ch = ca.chord(PROG[(bar - 1) % 4], 3)
    for i, v in enumerate(patt):
        if v is None: continue
        octv, idx = divmod(v, 3)
        arp.note(beat(bar, i * step), ch[idx] + 12 * octv, step * 1.1)

arp_play(bar, [1, 2, 4, 2], 1.0)                  # intro：4 分稀疏
arp_play(bar, [1, 2, 4, 2, 1, 2, 4, 5], 0.5)      # verse：8 分
arp_play(bar, [3,4,5,4,3,4,5,4,3,4,5,4,3,4,5,6], 0.25)  # chorus：16 分高八度
```

- 换段落换音型/密度/八度区 = 最直接的“织体推进”。

### 4.5 旋律（lead / bell / rhodes）

- 写**乐句**（2 或 4 小节一句），用 `play_melody` 式循环铺满段落：

```python
def play_melody(track, bar0, cycles, mdict):
    for k in range(cycles * len(mdict)):
        for (b, name, dur) in mdict[k % len(mdict)]:
            track.note(beat(bar0 + k, b), name, dur)
```

- 旋律设计原则：
  - 长音落在**和弦音**上，经过音只占弱拍/短时值；
  - 乐句有问答（前半上行、后半回落）；句尾留白；
  - 主歌音区低/稀疏（rhodes），副歌高/密集（lead=pluck），间奏换音色（bell）。
- 写 hook：3~5 个音的小动机 + 变奏，反复 2~4 遍。示例见 `examples/night-drive/make.py` 的 `HOOK`/`M_VERSE`。

### 4.6 过渡与点缀

```python
riser.note(beat(15), None, 8)     # 2 小节扫频（build 末尾）
crash.hit(beat(33))               # 段落头撞击
bell.note(beat(36, 3.5), "A5", 1.0)   # 句尾亮色（少量）
vinyl.note(beat(1))               # 黑胶底噪铺到曲终（texture，dur 缺省=到曲终）
```

- 音效单发也可用：`dings = s.track("ding"); dings.note(beat(64), 12)`（+12 半音）。

## 5. 结构与能量骨架

初学者直接照抄这个骨架改（93 小节 @124bpm = 3:00）：

| 段落 | 小节 | 内容 |
|---|---|---|
| intro | 8 | pad + 稀疏琶音 |
| build | 8 | kick/hat/bass 渐进 + 末 2 小节 roll + riser |
| verse | 16 | 主歌四件套（kick/clap/offbeat hat/bass）+ arp + rhodes 旋律 |
| chorus | 16 | 全开 + hook 旋律 + crash |
| break | 8 | 无鼓 4 小节（pad/bell）+ 鼓逐级回归 4 小节 + riser |
| verse2 | 16 | 同 verse（可加点缀） |
| chorus2 | 16 | 同 chorus |
| outro | 5 | 逐层退出 → 末 2 小节只留 pad/长音 |

能量推进的三大手段：**加层**（鼓组/音色层数）、**加密**（8 分→16 分）、**抬高**（八度/音区）。

## 6. 混音与母带

- `gain_db` 初始平衡（可按渲染报告的 peak_db 微调）：kick 0 / clap -4 / snare -8 / hat -10 / crash -9 /
bass -3 / arp -8 / lead -6 / rhodes -9 / bell -9 / pad -14 / vinyl -22 / riser -7。
- 侧链：`s.sidechain("kick", "bass", depth_db=-6.5, release=0.16)`；常配 pad（-5）/arp（-4.5）。
- 声像：pad 居左/右点缀（`:0.25`）、bell 稍右、arp 稍左，低音与打击乐居中。
- 母带自动完成：响度归一（默认 -14 LUFS）+ 软限幅（ceiling 0.72）+ 10ms 边缘淡化。
- 渲染报告里每轨 `peak_db` 可帮你发现过响/过轻的轨道。

## 7. 结尾安全做法（血泪教训）

不要在已渐弱的 outro 上让 bell/pad 突现，更不要放 kick/crash 重击。正确做法：

1. 逐层退出：kick 先停 → bass 转长音 → arp 变稀疏；
2. 最后 2 小节只留 pad（每小节）+ 一个长音 bell；
3. `s.fade(out_seconds=3.5)` 渐出到真正静音；
4. 验证：渲染后用 `_dev/check_night.py` 看最后 8 秒的 0.25s 窗口曲线——应该是单调下降。

## 8. 常见坑

- **长度计算**：最后一小节的长音 dur 会撑长曲长（不设 length 时）。设了 `s.length(bars=93)` 后，只要音符不超出该长度就不影响输出。
- **pad 与和弦错位**：见 4.3；不要让 pad 的时长跨越和弦变化。
- **`play_melody` 循环上界**：`cycles × len(mdict)`（不是 `cycles`）——示例开发中的真 bug。
- **sfx 的 pitch**：半音数值，不是音名（写 "A4" 会报错）。
- **空轨**：某轨没音符也能渲染（自动跳过），但至少一轨要有音符。
- **确定性**：不要用 `random`——所有“变化”都要写成显式音符/循环；引擎同乐谱逐样本可复现。

## 9. 从零写一支曲子的流程

1. `s = ca.Song(bpm=...)` + `s.length(bars=...)` 定规格；
2. 和弦循环 `PROG` + 根音表；
3. 逐段落编排：先鼓/贝斯骨架，后和声/琶音，最后旋律与过渡；
4. `--check` 看摘要（各轨音符数是否合理）；
5. 渲染听感检查（文件大小、响度、结尾曲线；用 `_dev/check_night.py` 的方法自查）；
6. 按渲染报告的 peak_db 校准 gain，反复 4~5 步直到满意。
