# HANDOFF — write-audio（通用版）

> 项目状态文件：新会话先读这里。主记忆只存索引行。
> **这是一个 Agent Skill**：目录名 `write-audio`，Python 包名 `write_audio`。

## 状态

- 阶段：**v0.2.0 已交付并验证（2026-10-09）**。
- 定位转变（用户要求）：**“当前版本归档，重新升级：只管渲染，其他的都交给 AI，不要随机预设”**。
  v0.1.2（自动作曲路线：风格预设/随机旋律）完整归档于 `_dev/_snapshots/v0.1.2-final/`（39 文件，含旧 zip 与全部测试）。
- 位置：`~/.codebuddy/skills/write-audio/`（作为 Agent Skill；也兼容任意 `skills/` 目录）
- 一句话：**乐谱进 → 成品出**。曲式/和弦/旋律/织体全由乐谱脚本显式给出；引擎无创作决策、无随机。
- 示例库：`examples/night-drive/`（原创电子曲 3 分钟）、`examples/two-tigers/`（童谣二创示范 2 分 37 秒，含能量图）。

## v0.2.0 架构

```
runtime/write_audio/
├─ audio.py   音源层：合成工具 / 19 音效 / 12 乐器 / INST 注册表（六类 kind：perc/tone/poly/riser/texture/sfx）
├─ theory.py  乐理：音名/MIDI/频率、和弦解析（含斜杠低音）、音阶（新增）
├─ song.py    Song / Track / 渲染引擎（新核心；替代旧的 music.py + track.py，旧文件已删）
├─ mix.py     输出链：find_ffmpeg / decode_audio / write_wav / write_mp3 / measure_loudness / master / fade 工具
│             （本版升级：支持立体声 (n,2)，新增 _fade_in/_fade_out）
├─ __init__.py  导出：Song, Track, midi, freq, chord, scale, INST, SFX, SR ...（v0.2.0）
└─ __main__.py  CLI：python -m write_audio song.py [--out/--stems/--check/...]
```

乐谱 = Python 脚本，里内定义 `song = ca.Song(...)`；`python song.py` 或 `python -m write_audio song.py` 渲染。

## 核心 API（稳）

```python
s = ca.Song(bpm=124, beats_per_bar=4, tail=1.5)
t = s.track(inst, name=None, gain_db=0.0, pan=0.0, seed=1)
t.note(at, pitch=None, dur=None, vel=1.0)     # at/dur 单位=拍
t.notes([...]) / t.hit(at) / t.hits([...]) / t.grid("x...x...", step=0.25)
s.length(bars=/seconds=/beats=)               # 渲染输出 = 曲长 + tail
s.sidechain(src, dst, depth_db=-7, release=0.18)
s.fade(in_seconds=, out_seconds=)
rep = s.render(out=/wav=/stems=, lufs=-14, ceiling=0.72, bitrate=192, tail=1.0, title=)
ca.midi("A3") / ca.freq / ca.chord("Am7",3) / ca.scale("A","minor",3)
```

## 验证记录（可复现）

- `_dev/t_theory.py`：**33 项 PASS**（音名/频率/音阶/和弦，含错误路径）。
- `_dev/mini31.py`：**24 项 PASS** —— 音符精确落位（时值后完全静音）/ grid（'|' 不推进）/ 确定性（两次渲染逐样本相等）/
  声像（pan=-1 → R 完全静音）/ 侧链起点深度=-7dB 精确/1s 恢复/长度=音乐+tail/空谱与缺失音高报错/分轨/
  fade_out/stats/端到端 mp3/参数校验/无削波。
- 示例《Night Drive》（`examples/night-drive/make.py`）：93 小节 = 181.0s（含 tail 1.0）；
  **-14.0 LUFS / -0.6 dBTP**；渲染 **34.6s**；音符：kick 312 / hat 888 / arp 842 / bass 599 / pad 89 / lead 96 …（13 轨）。
- `_dev/check_night.py`：段落能量 + 结尾平滑度。**结尾 3 秒 -63→-84dB 单调渐零，安静段无打击突现**
  （对比：v0.1.1 用户反馈的结尾是“静 -32.9dB → kick+crash 猛击 -11.6dB”）。
- 示例《两只老虎 · 午夜电波》（`examples/two-tigers/make.py`，童谣二创）：81 小节 ≈ 157.8s；
  C 大调 → A 小调（下行小三度）、Am-F-C-C-F-Dm7-E7-Am 八小节循环；**-14.0 LUFS / -0.4 dBTP**；
  渲染 38.6s；段落 RMS：intro 渐入 -31.5→-15 / drop A·B·C ≈ -15.3 / break **-24.1**（较 drop 低 8.8dB）/
  bridge -17.2（爬升）/ outro 渐退；`_dev/check_two.py`：**结尾 8 秒无正向突跳**（单调至 -90dB）、峰值 -1.72 dBFS。
  编排经验：drop A 先不给 clap（把 clap 留给副歌，层次更清晰）；break 前 4 小节全撤鼓（只留电钢+垫+贝斯长音）。

## 开发中实际踩到并修复的（都留了测试或注释）

1. `song.py` 忘记 import `_norm`（stems 写出时 NameError）——被 mini31 逼出。
2. 示例 `play_melody` 循环上界写错（应 `cycles * len(mdict)`）→ lead 只弹了 12 个音符；修后 96。
3. **pad 与和弦循环错位**：2 小节长音 pad 会盖过下一小节（Am F C G 循环时 C 盖住 G）——
   改为 **每小节一个 pad**，和声精确对齐；结尾安静段也因此更平滑。
4. **结尾安全做法**（示例实践）：逐层退出（kick 先停、bass 长音、arp 稀疏）→ 最后两小节只留 pad+bell →
   `s.fade(out_seconds=3.5)` 渐出到真正静音。bell 长音不要在极静背景上“突现”。
5. break 的鼓回归要**逐级**（kick → +hat → +clap/bass），避免一步全奏的 -40→-14dB 跳变。

## 已验证的设计要点（改动前先读）

1. **渲染管线**：每轨独立 buffer → 侧链 duck（源轨音符时刻 + 指数恢复）→ 立体声等功率声像混音 →
   fade → `mix.master`（loudnorm 测量 → 增益 → tanh 软限幅 → 复测 → 边缘淡化）→ wav/mp3；
   stems = 每轨 pre-master 原始信号（不含增益/声像/侧链）。
2. **确定性纪律**：引擎里无任何随机决策；每音符 seed = `track.seed + round(at*331)`（确定性）。
   任何“让输出更丰富”的想法都必须变成乐谱里的显式音符，不能在引擎里加随机。
3. **时间模型**：at/dur 一律拍（float）；第 n 小节头 = `(n-1)*beats_per_bar`；输出时长 = max(音符末, length) + tail。
4. **侧链**：`amount = 1 - 10^(depth_db/20)`；起点压到 10^(depth/20) 倍；release 秒控制恢复曲线（exp）。
5. **声像**：等功率（center = 0.7071/0.7071；极左 = 1/0）。mix/stems/master 全链支持 (n,) 与 (n,2)。
6. **母带**：ceiling 默认 **0.72**（v0.2 从 0.76 调低；示例 tp -0.6 dBTP，符合 ≤ -1 附近的流媒体惯例±）。
   响度测量用 loudnorm JSON；mp3 编码 libmp3lame 192kbps（回退内置 mp3）。
7. **乐器 kind 语义**（audio.INST）：perc（忽略音高/dur）、tone（pitch 必填）、poly（pitch 可列表）、
   riser（dur=扫频长）、texture（dur 缺省=到曲终）、sfx（pitch=**半音移调**，不是音名！）。
8. **兼容性**：Python 3.8（不用 3.9+ 语法）；numpy 1.16+；旧 API（Track/build_music/style/seed 自动作曲）
   已移除——别在示例或文档里写旧写法。

## 环境事实（本机）

- Python 3.8.5 / numpy 1.24；FFmpeg：`D:\tools\ffmpeg\bin\ffmpeg.exe`（loudnorm/astats 可用）。
- 测试运行器：`_dev/pyrun.bat`（chcp 65001 + PYTHONUTF8=1）；cmd 引号坑：带引号直接跟双参数易错，
  可用 workDirectory + 相对路径调用。
- 写文件时确认路径拼写（曾把 `AppData\Local` 写成 `AppDataLocal` 写到错位置）。

## 路线图

- 母带链可选项：多段压缩/立体声拓宽/MS 处理（保持“显式开关”哲学）
- 更多音色：弦乐/风琴/合成拨弦变体、滤波开合（build 自动化）作为显式乐器参数
- MIDI 导出（note 事件 → .mid，供 DAW 二次编曲）
- 与 codingfilm 互通：`music="<rendered>.wav"` 直接用本库产物（已有入口）
- `_dev` 转正式 `tests/`；示例曲增补一段“只用手写音符”的极简样板

## 运行方式

```
python examples/night-drive/make.py        # 重渲示例曲（≈35 秒）
python -m write_audio <song.py> --check    # 乐谱摘要
python -m write_audio <song.py> --out x.mp3 --stems stems/
```

> 注：早期开发用的 `_dev/` 测试目录未随仓库分发；示例曲渲染即端到端验证。

## 归档

- `_dev/_snapshots/v0.1.2-final/` — v0.1.2 完整工作副本（含旧测试、旧文档、旧 zip）
- `_dev/_snapshots/v0.1.1/` — 更早快照
