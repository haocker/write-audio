# write-audio

[![Agent Skill](https://img.shields.io/badge/Agent-Skill-blueviolet)](#-作为一个-skill-使用)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python](https://img.shields.io/badge/python-3.8%2B-blue.svg)](https://www.python.org/)

**用代码写乐谱，渲染成品音乐。** 曲式、和弦、旋律、织体全部在 Python 乐谱脚本里显式写出，
引擎忠实渲染。纯 Python + numpy + FFmpeg，零外部素材、波形现场合成——**开箱即用、逐样本可复现**。

> **这是一个 Agent Skill（智能体技能）**。放进 `~/.codebuddy/skills/write-audio/`，
> AI 就能"用代码写乐谱 → 渲染出成品音乐"。Python 包名为 `write_audio`。

### 亮点

- **零素材、自包含**：不依赖任何音色库，`numpy` + FFmpeg 两个依赖即可开跑，体积小、部署简单。
- **逐样本可复现**：同一乐谱两次渲染完全相等，改一个音符只改一个音符，结果确定可控。
- **侧链闪避**：`s.sidechain("kick", "bass")` 一行得到电子舞曲的"抽泵感"，鼓点一响贝斯自动让位。
- **19 种音效**：whoosh / impact / glitch / typing… 适合电子乐、视频配乐、UI 音效。
- **流媒体级母带**：自动响度归一化到 -14 LUFS、真峰值 ≤ -1 dBTP，可直接发布。
- **12 乐器 + 19 音效**：覆盖电子、舞曲、氛围、Lo-fi 等合成风格。

```python
import write_audio as ca

s = ca.Song(bpm=124)
kick = s.track("kick")
kick.grid("x...x...x...x...", step=0.25)
bass = s.track("bass", gain_db=-4)
bass.notes([(0, "A1", 1), (1, "A1", 0.5), (1.5, "C2", 0.5)])
s.sidechain("kick", "bass")
s.length(bars=4)
s.render("out.mp3")
```

## 作为一个 Skill 使用

把整个目录放到 `~/.codebuddy/skills/write-audio/`（或任何兼容的 `skills/` 目录）。
AI 检测到"写一段音乐 / 生成一段曲子 / 做个某风格配乐"等意图时会自动加载 `SKILL.md`，
按其中的乐谱 DSL、编曲方法与工作流程创作。

## 安装（作为 Python 库）

```bash
pip install numpy          # 唯一必需依赖
# 另需 FFmpeg（mp3 编码与响度测量）：winget install ffmpeg / brew install ffmpeg / apt install ffmpeg
# 或在环境变量 CA_FFMPEG / CF_FFMPEG 中指定完整路径
```

## 30 秒上手

```bash
python examples/night-drive/make.py    # 渲染示例曲《Night Drive》（3 分钟，≈35 秒）
python examples/two-tigers/make.py     # 童谣二创《两只老虎 · 午夜电波》（2 分 37 秒，≈39 秒）
```

或在你的乐谱脚本目录（先让 `write_audio` 可被导入，例如 `pip install -e .`，
或把 `runtime/` 加进 `PYTHONPATH`）：

```bash
PYTHONPATH=/path/to/write-audio/runtime \
python -m write_audio song.py --out D:/music/track.mp3 --stems D:/music/stems
PYTHONPATH=/path/to/write-audio/runtime python -m write_audio song.py --check   # 只打印乐谱摘要
```

## 目录结构

```
write-audio/
├─ SKILL.md              # Agent Skill 主文件（AI 读这个来创作）
├─ README.md             # 本文件
├─ HANDOFF.md            # 项目状态 / 开发交接记录
├─ runtime/write_audio/  # 运行时（纯 Python，可读源码学手艺）
│  ├─ song.py            # Song / Track / 渲染引擎（核心）
│  ├─ audio.py           # 音源层：12 乐器 + 19 音效 + INST 注册表
│  ├─ theory.py          # 乐理：音名/MIDI/频率、和弦、音阶
│  ├─ mix.py             # 输出链：wav/mp3/loudnorm/母带/fade
│  └─ __main__.py        # CLI：python -m write_audio
├─ knowledge/            # 给 AI 的知识文档
│  ├─ write-music.md     # 写乐谱指南（写法/编曲/母带/套路/避坑）
│  └─ instruments.md     # 乐器参考表（音域/时值/增益建议）
└─ examples/             # 示例曲（含成曲、分轨与分析）
   ├─ night-drive/       # 原创电子曲 3 分钟
   └─ two-tigers/        # 童谣二创示范
```

## 核心理念：分工

| 层 | 是谁的事 | 说明 |
|---|---|---|
| 曲式、和弦、旋律、织体、每个音符 | **你（AI）** | 在乐谱脚本里显式写出；用 Python 循环/函数组织重复与变奏 |
| 音源合成、多轨混音、侧链、母带、输出 | **引擎** | `song.py`：忠实渲染，把乐谱精确变成声音 |

- **结果是确定的**：同乐谱两次渲染逐样本相等；想改哪就改哪，不会"跑偏"。
- **每小节、每一轨都是显式音符事件**：重复与变奏是你在乐谱里写的循环，结构一目了然。
- **可验收**：-14 LUFS / 真峰值 ≤ -1 dBTP（流媒体标准）；输出 MP3 / WAV / 任意轨分轨。
- **自包含**：零外部素材，全部波形现场合成（numpy）；只要 Python 3.8+ / numpy / FFmpeg。

## 库用法全表

```python
import write_audio as ca

# ——— 乐谱 ———
s = ca.Song(bpm=124, beats_per_bar=4, tail=1.5)      # tail = 乐尾缓冲（秒）

t = s.track("pluck", name="lead", gain_db=-6, pan=0.2, seed=1)
# name 可省（默认=乐器名，重名自动 _2）；pan -1..1 等功率声像（默认 0 居中）

t.note(0, "A4", 1.0, 1.0)              # (拍, 音名/MIDI, 时值[拍], 力度)
t.note(4)                               # 打击乐：无音高
t.notes([                               # 批量（三种写法混合均可）
    (0, "E5", 0.7), 12,                 # 元组 / 纯数字(t=打击)
    {"at": 2, "pitch": "C5", "dur": 1},
])
t.hit(2)                                # 打击乐：一击
t.hits([0, 1, 2, 3])                    # 打击乐：批量
t.grid("x...x...x...x...", step=0.25)   # 网格谱（'|' 分隔不推进）

s.length(bars=93)                       # 曲长；渲染输出 = 曲长 + tail
s.sidechain("kick", "bass", depth_db=-7, release=0.18)   # 侧链闪避
s.fade(in_seconds=None, out_seconds=3.5)                 # 整曲渐入/渐出

# ——— 渲染 ———
rep = s.render(
    out="track.mp3",     # 输出 mp3（或 .wav；全省略时默认 track.mp3）
    wav=None,            # 额外/指定 wav 路径
    stems=None,          # 分轨目录（每轨一个 <轨名>.wav，未母带、不含增益/声像/侧链）
    lufs=-14.0,          # 响度目标（流媒体标准）
    bitrate=192,         # mp3 码率
    fade_in=None, fade_out=None,   # 可在这里覆盖 song.fade(...)
    tail=None,           # 覆盖 Song.tail
    title="标题", keep_wav=False,
)
print(rep["lufs"], rep["tp"], rep["render_seconds"])
for tr in rep["tracks"]:          # 每轨音符数/峰值（峰值帮助校准增益）
    print(tr["name"], tr["notes"], tr["peak_db"])

# ——— 乐理工具 ———
ca.midi("A3")            # -> 57（音名 → MIDI；也接受 MIDI 数值）
ca.freq("A3")            # -> 220.0（音名/MIDI → Hz）
ca.chord("Am7", 3)       # -> [57, 60, 64, 67]（和弦名 → MIDI 列表；支持 C/E 斜杠低音）
ca.chord("Cmaj7", 4)     ca.chord("F#m7b5")   ca.chord("Bb7")  ...
ca.scale("A", "minor", 3)  # -> 音阶 8 个音（MIDI）
ca.resolve_scale("harmonic minor")   # 音阶名 → 半音偏移
```

**乐器**（`s.track(name)`）：`kick` `hat` `clap` `snare` `crash` `bass` `pluck` `bell`
`rhodes` `pad` `riser` `vinyl` + 19 种音效（`impact` `whoosh` `ding` `riser` `bassdrop` …）。
详见 `knowledge/instruments.md`。

## 命令行

```
python -m write_audio song.py                          # 渲染（脚本里定义 song = ca.Song(...))
python -m write_audio song.py --out x.mp3 --stems stems/
python -m write_audio song.py --lufs -14 --bitrate 192
python -m write_audio song.py --fade-out 3 --keep-wav
python -m write_audio song.py --check                  # 只打印乐谱摘要，不渲染
```

## 输出说明

| 产物 | 说明 |
|---|---|
| `*.mp3` | 默认 192kbps；响度 -14 LUFS（可改） |
| `*.wav` | 48kHz 立体声 16-bit（指定时才保留） |
| `stems/` | 分轨（pre-master，不含增益/声像/侧链，可进 DAW） |

## 示例曲

| 曲目 | 说明 | 时长 |
|---|---|---|
| `examples/night-drive/` | 《Night Drive》原创电子曲，A 小调 / 124 BPM，13 轨全显式 | ≈ 3:01 |
| `examples/two-tigers/` | 《两只老虎 · 午夜电波》童谣二创，C→A 小调电子舞曲编配 | ≈ 2:37 |

## FAQ

- **和 write-audio-pro 什么关系？** 两者同源、共用一套乐谱 DSL。本仓库是**纯合成引擎**
  （零素材、逐样本可复现、体积小、开箱即用），适合电子/舞曲/音效与轻量部署；
  [write-audio-pro](https://github.com/haocker/write-audio-pro) 用 **FluidSynth + SoundFont
  真实采样**音源，真钢琴/真弦乐，适合抒情与古典编制。
- **旋律怎么来？** 你（AI/作者）写：`lead.notes([(0, "E5", 0.7), ...])`，或用 Python
  循环把和弦/音阶工具（`ca.chord` / `ca.scale`）组织成乐句。
- **想换风格？** 换乐器、换鼓型、换和声、换织体、换速度——你写的乐谱就是风格。
- **能生成多长？** 任意：`s.length(bars=...)` / `seconds=` / `beats=`；不设则自动取音符实长。
- **怎么做结尾？** 参考示例：逐层退出 + 最后两个小节只留 pad/长音 + `s.fade(out_seconds=3.5)`。
- **能商用吗？** 生成结果无版权采样，可自由使用。

## 许可

[MIT](LICENSE) © 2026 write-audio contributors

