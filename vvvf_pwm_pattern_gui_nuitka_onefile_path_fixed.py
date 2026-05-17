# -*- coding: utf-8 -*-
"""
VVVF PWM Pattern Sound GUI

機能:
- Tkinter Canvasのみで描画。Matplotlib不使用
- 音声処理はGUIとは別プロセス。sounddevice/PortAudioが詰まってもGUIを巻き込みにくい
- GUIでPWMパターンプリセット選択・速度域ごとの行編集
- PWMパターンテーブル指定: 速度域ごとに ASYNC / SYNC / SHE / CHM / WIDE3 / ONEPULSE を自動切替
- 非同期PWM / 同期PWM / SHE-PWM / CHM-PWM / 広域3パルス / 1パルス
- マスコン P1〜P5 / N / B1〜B7
- スピードメーター
- PWMパターンのユーザープリセット保存/読込
- 高周波重畳・スイッチング周波数拡散方式
- 中立ノッチではインバータ音をOFF。速度が残っている間は走行ノイズ/転動音を鳴らせる
- N↔P/B遷移時に低速非同期PWMへ切替し、電圧を0↔既定電圧へ滑らかにランプ
- 拡散方式はPWM音声・波形表示のスイッチング周波数そのものを変調する
- 1パルス時は電圧利用率100%固定
- 棒ではなく、PWM軌跡を六角形空間へ投影して描画
- 波形表示は電流/基準波/ゲート電圧ではなく、オシロ固定表示の相間PWM電圧パルス
- SVPWM風 六角形パワー表示 + 疑似パワー表示
- 反響モードと共鳴フィルタをON/OFF可能
- ユーザー提供のモハラジオ録音/通常録音の差に合わせ、耳で聞こえる自然な共鳴帯と短い初期反射へ調整
- 転動音を追加。インバータOFF時でも速度に応じて走行/転動音を出せる
- 共鳴フィルタはPWM/モータ音にだけ掛け、走行ノイズ/転動音には掛けない
- 電圧指令によってPWM音の強さ・荒さが変化する
- 起動時の電圧を1〜5%程度に設定可能
- PWM音量は電圧指数カーブだけでなく、現在の疑似モーター電力にも比例して増加
- 最高速度、最高基本周波数、最高周波数到達速度を別々に設定可能
- 変調率100%時の相間電圧値を設定し、現在電圧/疑似電力を表示
- 2つの加速音（通常録音=耳、モハラジオ録音=磁界）を再解析し、通常録音寄りのマイルドでこもった音響フィルタへ再調整
- 音声 underflow 対策: 音声ブロック/レイテンシを安定寄りにし、共鳴フィルタを可能ならSciPyで高速処理
- PWMパターン行の「追加」と「選択行更新」を別ボタン化
- モーター電圧0%時/100%時のPWM音量をGUIで指定可能
- 六角形パワーベクトル表示を、PWMスイッチング波形(U/V/W)そのもの→Clarke αβ電圧→時間積分で磁束相当のベクトル軌跡として計算
- 参考サイトの「電圧を時間積分した磁束軌跡」方式に寄せ、同期PWM/低パルス時の多角形感とリプルを表示
- v25: 六角形ベクトル軌跡を電気角0〜2πの固定グリッドで厳密に1周期計算。終点重複をなくし、非同期PWMはキャリア初期位相を等間隔平均して、切り出しタイミング依存の歪みを低減
- v26: 同期PWMのベクトル軌跡を絶対変調率でスケーリング。複数周期/位相平均を追加し、電圧を変えても軌跡サイズが変わらない問題を修正
- v27: 広域3パルスを、ユーザー提示図に合わせて「主パルス＋両端の補助短パルス」になる位相ゲート波形へ修正
- v35: 基準周波数到達速度以降も基本波周波数が速度比例で上がり続けるよう修正。電圧は基準速度以降で頭打ち。
- v28: 広域3パルスを同一半周期内の「補助短パルス＋主パルス＋補助短パルス」へ再修正。低速加速度を強化、パターンテーブルのJSONインポート/エクスポート、現在位相/速度計矢印の非表示に対応
- v30: 走行加速度モデルを再設計。低速域で最大加速度、高速域に行くほど連続的に加速度が落ちる曲線へ修正し、現在加速度を表示
- v31: 広域3パルスを矩形変調波＋のこぎり波/三角搬送波の比較イメージに合わせ、相波形は中央主パルスだけ、相間電圧で両端補助パルスが出る方式へ修正
- v32: 広域3パルスを再修正。相波形を0を含む擬似3値ではなく、矩形状変調波と局所のこぎり状搬送波を比較した二値ゲートとして生成し、各半周期で「補助短パルス・主パルス・補助短パルス」になるように変更
- v26: 最大変調率100%対応。加速用/減速用の2種類のPWMパターンテーブルをGUIで編集可能
- PWMオシロ波形の横軸を電気角1周期ではなく固定時間[ms]表示へ変更
- 描画例外でメイン更新ループが停止しないようtickを保護し、六角形セクタ番号を0..5へ固定

必要ライブラリ:
    pip install numpy sounddevice

実行:
    python vvvf_pwm_pattern_gui.py

注意:
- v36: SHE/CHMを簡易高調波注入ではなく、四分波対称のプログラムドPWM角度テーブル方式に変更。
  SHEは低次非3倍高調波の消去、CHMは電流高調波重み付き最小化を狙う。
- v37: SHEのスイッチング角が変調率で枝飛びして波形が乱れる問題を修正。
  角度ROMを連続追跡＋補間方式に変更し、狭すぎるパルスを抑制。
- v45: v37をベースに、CHMは変更せず、SHEだけ半周期ごとに上側パルス列/下側パルス列になる2レベル半波パルス列へ修正。
- v48: SHE相間電圧の逆向き細パルスだけを、相間基本波半周期の極性へ合わせる補正を追加。
- v49: GUI負荷を軽量化。ベクトル軌跡/オシロ波形をキャッシュし、描画周期とサンプル数を抑制。
- v50: SHEの半波パルス区間をキャッシュして高速化。PWMオシロ波形はキャッシュ式をやめ、毎回直接計算へ戻す。
- v52: SHEのパルス数を7本固定相当から、SHE5/7/9/15/21/27/33/45など任意値に対応。
- v53: SHEの値を相間電圧の半周期パルス数として扱うよう修正。相脚側は(N-1)/2本にして、SHE7でUV波形が7パルスになるよう補正。
- v54: SHEのベクトル軌跡を相間電圧PWM波形から再計算し、スイッチングリプル平均で内側ループ状の歪みを抑制。
- v55: CHMの角度補間結果をキャッシュし、CHMベクトル軌跡の初期位相平均を省略して処理を軽量化。
- v56: CHM7とCHM9が同じ角数になっていた変換式を修正し、CHMの値で波形が変わるように変更。
- v57: 非同期PWMの値に 750-1050 のような範囲指定を追加し、速度域内でキャリア周波数を直線補間。
- v51: PWMオシロ波形をv48相当に戻し、サンプル数を700へ復帰。
- 実電力ではなく、速度・変調率・負荷率から計算した疑似パワー表示です。
"""

from __future__ import annotations

import json
import math
import re
from functools import lru_cache
import multiprocessing as mp
import os
import queue
import sys
import threading
import time
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

APP_VERSION = ""
TAU = math.tau
# 画面上の六角形表示は90°回転して、軌跡と六角形外枠を一致させる。
HEX_DISPLAY_ROT = math.pi / 2.0


# ============================================================
# Programmed PWM angle helpers for SHE/CHM
# ============================================================
# SHE/CHMはキャリア比較PWMではなく、四分波対称のスイッチング角を
# 変調率ごとにROM/テーブル化して使う「プログラムドPWM」として扱う。
# 本ソフトでは外部依存なしで動くよう、必要な角度を軽量な決定論的
# 座標探索で求め、0.5%刻みでキャッシュする。

def _ppwm_clamp(x: float, lo: float, hi: float) -> float:
    return lo if x < lo else hi if x > hi else x


def _ppwm_normalize_pulse_count(pulse_value: int) -> int:
    """SHE/CHM用のパルス数を2レベルPWMとして扱いやすい奇数へ正規化する。

    v78:
    SHE/CHMのスイッチング角方式では、半波対称・四分波対称の都合で
    3,5,7,9,13,15...のような奇数パルスとして扱う方が自然。
    偶数値をそのまま角数へ変換すると、パルス配置が非標準になり、
    磁束軌跡が片寄ったり歪んだりする原因になる。

    例:
      12 -> 13
      14 -> 15
    """
    p = max(1, int(round(float(pulse_value))))
    if p < 3:
        p = 3
    if p % 2 == 0:
        p += 1
    return p


def _ppwm_angle_count(pulse_value: int) -> int:
    """パルス数指定を四分周期あたりのスイッチング角数へ変換する。

    v78:
    旧式では最小角数を3に固定していたため、SHE/CHMの3パルス・5パルスが
    正しく表現できなかった。また、12のような偶数指定をそのまま6角として
    扱うと、2レベル半波対称PWMとしては非標準な配置になりやすかった。

    ここではパルス指定を奇数へ正規化してから、
      3 -> 1角
      5 -> 2角
      7 -> 3角
      9 -> 4角
      13 -> 6角
      15 -> 7角
    とする。
    """
    p = _ppwm_normalize_pulse_count(pulse_value)
    return max(1, min(7, (p - 1) // 2))


def _ppwm_polarity(n_angles: int) -> float:
    # 現在の相ゲート生成式では、角数が奇数のときに基本波極性が反転するため補正する。
    return -1.0 if (int(n_angles) % 2) else 1.0


def sync_cat_ear_required(pulse_value: int) -> bool:
    """通常三角波キャリアではなく低パルス/特殊同期ルートを使うか。

    原則として(3+6n)は通常同期三角キャリアでよいが、
    同期3パルスだけは低パルスすぎて普通の三角比較にすると
    細い逆向きパルスや不自然な磁束軌跡が出やすい。
    そのため3/5/7は相電圧ノッチ方式、12など(3+6n)以外は特殊同期として扱う。
    """
    try:
        p = max(1, int(round(float(pulse_value))))
    except Exception:
        p = 1
    if p == 3:
        return True
    return (p % 6) != 3


def _ppwm_switch_from_angles(theta: float, angles: list[float]) -> float:
    polarity = _ppwm_polarity(len(angles))
    x = theta % TAU
    half = x % math.pi
    q = half if half <= math.pi / 2.0 else math.pi - half
    sign = 1.0 if x < math.pi else -1.0
    state = 1.0
    for a in angles:
        if q >= a:
            state = -state
    return polarity * sign * state


def _ppwm_flux_shape_score(angles: list[float]) -> float:
    """三相PWM→Clarke αβ→積分磁束の簡易形状評価。

    重いので通常の探索ループには入れず、v79では角度ROMの後段微調整でだけ使う。
    """
    n_ang = len(angles)
    if n_ang <= 0:
        return 0.0

    ns = 48 if n_ang >= 4 else 36
    dth = TAU / ns
    rt3 = math.sqrt(3.0)

    va = []
    vb = []
    for i in range(ns):
        th = (i + 0.5) * dth
        u = _ppwm_switch_from_angles(th, angles)
        v = _ppwm_switch_from_angles(th - TAU / 3.0, angles)
        w = _ppwm_switch_from_angles(th + TAU / 3.0, angles)
        va.append((2.0 / 3.0) * (u - 0.5 * v - 0.5 * w))
        vb.append((2.0 / 3.0) * ((rt3 / 2.0) * (v - w)))

    ma = sum(va) / ns
    mb = sum(vb) / ns
    ia = 0.0
    ib = 0.0
    flux = []
    for a, b in zip(va, vb):
        flux.append((ia, ib))
        ia += (a - ma) * dth
        ib += (b - mb) * dth

    end_a = ia
    end_b = ib
    denom = max(1, ns - 1)
    pts = []
    for i, (a, b) in enumerate(flux):
        t = i / denom
        pts.append((a - end_a * t, b - end_b * t))

    ca = sum(a for a, _ in pts) / ns
    cb = sum(b for _, b in pts) / ns
    pts = [(a - ca, b - cb) for a, b in pts]

    r = [math.hypot(a, b) for a, b in pts]
    r_mean = sum(r) / ns
    if r_mean < 1e-9:
        return 0.0

    r_std = math.sqrt(sum((x - r_mean) ** 2 for x in r) / ns) / r_mean
    r_max = max(r) / r_mean

    cxx = sum(a * a for a, _ in pts) / ns
    cyy = sum(b * b for _, b in pts) / ns
    cxy = sum(a * b for a, b in pts) / ns
    tr = cxx + cyy
    disc = max(0.0, (cxx - cyy) ** 2 + 4.0 * cxy * cxy)
    lam1 = 0.5 * (tr + math.sqrt(disc))
    lam2 = 0.5 * (tr - math.sqrt(disc))
    ecc = 0.0 if lam1 <= 1e-12 else max(0.0, (lam1 - lam2) / lam1)
    spike = max(0.0, r_max - 1.72)
    return 2.0 * r_std * r_std + 1.0 * ecc * ecc + 0.55 * spike * spike


def _ppwm_raw_harmonic(n: int, angles: list[float]) -> float:
    # 正規化フーリエ係数。実係数は 4/(n*pi) 倍だが、消去/最小化には不要。
    return 1.0 + 2.0 * sum(((-1.0) ** k) * math.cos(n * a) for k, a in enumerate(angles, start=1))


def _ppwm_nontriplen_harmonics(count: int) -> list[int]:
    hs = []
    h = 5
    while len(hs) < max(0, count - 1):
        if h % 3 != 0:
            hs.append(h)
        h += 2
    return hs


def _ppwm_objective(kind: str, angles: list[float], target_m: float) -> float:
    """SHE/CHM用の角度評価関数。

    SHE: 基本波を合わせ、5,7,11,13...の低次非3倍高調波をゼロへ近づける。
    CHM: 基本波を合わせつつ、モータ電流に近い 1/h 重み付き高調波を広く下げる。
         厳密な車両メーカー固有のCHM表ではないが、SHEとは異なる
         「特定高調波ゼロ」より「電流高調波全体を下げる」形にする。
    """
    kind = str(kind).upper()
    n = len(angles)
    pol = _ppwm_polarity(n)
    err_f1 = pol * _ppwm_raw_harmonic(1, angles) - target_m
    if kind == "CHM":
        score = 64.0 * err_f1 * err_f1
        for h in range(5, 80, 2):
            if h % 3 == 0:
                continue
            # 誘導機/同期機の高調波電流はおおむね周波数が高いほど流れにくいため、
            # 電流高調波相当として1/h系で重み付けする。5/7/11/13次は強めに抑える。
            w = 9.0 if h in (5, 7) else 4.0 if h in (11, 13) else 1.0
            ih = _ppwm_raw_harmonic(h, angles) / (h ** 1.18)
            score += w * ih * ih
    else:
        score = 28.0 * err_f1 * err_f1
        for h in _ppwm_nontriplen_harmonics(n):
            score += _ppwm_raw_harmonic(h, angles) ** 2

    # 実機のプログラムドPWMでも極端な狭パルスはデッドタイム/素子保護で扱いにくいため抑制。
    gaps = [angles[0]] + [angles[i] - angles[i - 1] for i in range(1, n)] + [math.pi / 2.0 - angles[-1]]
    for g in gaps:
        if g < math.radians(1.2):
            score += 0.018 / ((g + 1e-4) ** 2)

    # v78:
    # これまでのSHE/CHM角度表は、高調波誤差だけを追いすぎて
    # 角度が一部に固まり、大きな空白と細い連続パルスを作ることがあった。
    # その結果、PWM相電圧は一応成立しても、αβ積分磁束が不自然ないびつ形になった。
    # 実機ROM風に連続・安定したパルス配置へ寄せるため、ギャップの均一性を弱く加える。
    if n >= 2:
        target_gap = (math.pi / 2.0) / (n + 1)
        gap_reg = sum(((g - target_gap) / target_gap) ** 2 for g in gaps) / (n + 1)
        # CHMは「全体の電流高調波を下げる」目的なので、SHEより均一配置を強める。
        # v79: v78より少し強め、角度の大きな偏りを減らす。
        reg_w = 0.055 if kind == "SHE" else 0.115
        score += reg_w * gap_reg

        max_gap = max(gaps)
        if max_gap > target_gap * 2.05:
            score += (0.080 if kind == "SHE" else 0.140) * ((max_gap / target_gap) - 2.05) ** 2

    return score


def _ppwm_initial_angle_sets(count: int, m: float) -> list[list[float]]:
    lo = math.radians(1.2)
    hi = math.pi / 2.0 - math.radians(1.2)
    span = hi - lo
    seeds = []
    # ほぼ等間隔
    seeds.append([lo + span * (i + 0.5) / count for i in range(count)])
    # 低変調ではスイッチング角をやや外側へ広げる
    seeds.append([lo + span * (i + 0.5) / count + math.radians(8.0) * (1.0 - m) * math.sin((i + 1) * math.pi / (count + 1)) for i in range(count)])
    # 中央寄り/端寄りの候補も試す
    seeds.append([lo + span * (math.sin((i + 1) * math.pi / (2.0 * (count + 1))) ** 1.35) for i in range(count)])
    seeds.append([lo + span * ((i + 1) / (count + 1)) ** 1.35 for i in range(count)])
    out = []
    for s in seeds:
        s = sorted(_ppwm_clamp(x, lo, hi) for x in s)
        # 最小間隔を確保
        for i in range(1, len(s)):
            if s[i] <= s[i - 1] + lo:
                s[i] = min(hi, s[i - 1] + lo)
        out.append(s)
    return out


def _ppwm_sanitize_angles(angles: list[float], count: int, sep: float) -> list[float]:
    """角度列を必ず 0 < a1 < a2 < ... < π/2 に整える。

    v37: SHE波形が乱れる主因は、オンライン探索が変調率ごとに別の解の枝へ
    飛ぶことと、隣り合うスイッチング角が近づきすぎて細いパルスが出ることだった。
    ここで最小間隔を確保し、実機ROMテーブルのような連続した角度列に近づける。
    """
    lo = sep
    hi = math.pi / 2.0 - sep
    if not angles:
        angles = [lo + (hi - lo) * (i + 0.5) / max(1, count) for i in range(count)]
    a = sorted(_ppwm_clamp(float(x), lo, hi) for x in angles[:count])
    while len(a) < count:
        a.append(lo + (hi - lo) * (len(a) + 0.5) / count)
    a = sorted(_ppwm_clamp(float(x), lo, hi) for x in a)

    # 前向き/後ろ向きの2パスで最小間隔を確保する。
    for i in range(count):
        a[i] = max(a[i], lo + i * sep)
    for i in range(count - 1, -1, -1):
        a[i] = min(a[i], hi - (count - 1 - i) * sep)
    for i in range(1, count):
        if a[i] < a[i - 1] + sep:
            a[i] = a[i - 1] + sep
    for i in range(count - 2, -1, -1):
        if a[i] > a[i + 1] - sep:
            a[i] = a[i + 1] - sep
    return [_ppwm_clamp(x, lo, hi) for x in a]


def _ppwm_refine_angles(kind: str, count: int, target_m: float, seed: list[float], prev: list[float] | None) -> list[float]:
    """前回角度を初期値にして、連続性を優先しながらSHE/CHM角度を微調整する。"""
    sep = math.radians(1.7)
    lo = sep
    hi = math.pi / 2.0 - sep
    a = _ppwm_sanitize_angles(seed, count, sep)

    def objective_with_continuity(aa: list[float]) -> float:
        score = _ppwm_objective(kind, aa, target_m)
        if prev is not None:
            # 枝飛び防止。SHE解は複数枝を持つので、電圧が少し変わっただけで
            # まったく別の角度列へジャンプしないように連続性を優先する。
            score += 0.014 * sum(((aa[i] - prev[i]) / math.radians(1.0)) ** 2 for i in range(count))
        # パルスが細すぎると表示上も音も「乱れ」に見えるので、余裕を持たせる。
        gaps = [aa[0]] + [aa[i] - aa[i - 1] for i in range(1, count)] + [math.pi / 2.0 - aa[-1]]
        for g in gaps:
            if g < math.radians(2.2):
                score += 0.06 * ((math.radians(2.2) - g) / math.radians(1.0)) ** 2

        # v79: 解の枝飛びだけでなく、極端なパルス偏りもここで抑える。
        # 磁束形状評価は重いため、探索中ではなく後段微調整だけで使う。
        if count >= 2:
            target_gap = (math.pi / 2.0) / (count + 1)
            score += 0.045 * sum(((g - target_gap) / target_gap) ** 2 for g in gaps) / (count + 1)
        return score

    best_score = objective_with_continuity(a)
    step = math.radians(3.8)
    for _ in range(56):
        improved = False
        for i in range(count):
            lower = (a[i - 1] + sep) if i > 0 else lo
            upper = (a[i + 1] - sep) if i < count - 1 else hi
            for direction in (-1.0, 1.0):
                b = list(a)
                b[i] = _ppwm_clamp(b[i] + direction * step, lower, upper)
                b = _ppwm_sanitize_angles(b, count, sep)
                s = objective_with_continuity(b)
                if s < best_score:
                    a, best_score = b, s
                    improved = True
        if not improved:
            step *= 0.56
            if step < math.radians(0.018):
                break
    return a


def _ppwm_post_optimize_flux(kind: str, count: int, target_m: float, angles: list[float]) -> list[float]:
    """三相磁束形状を見てSHE/CHM角度を軽く後段補正する。

    通常探索に磁束評価を入れると重くなりすぎるので、最終解の近傍だけを探索する。
    """
    if count < 2:
        return angles

    sep = math.radians(1.7)
    a = _ppwm_sanitize_angles(angles, count, sep)

    def score(aa: list[float]) -> float:
        # 基本波・高調波を壊しすぎないため元の目的関数も残す。
        return _ppwm_objective(kind, aa, target_m) + (0.18 if kind == "SHE" else 0.26) * _ppwm_flux_shape_score(aa)

    best = score(a)
    # 大きく動かすとSHE/CHMらしさが崩れるため±0.8°程度の近傍だけ。
    for step_deg in (0.80, 0.42, 0.22):
        step = math.radians(step_deg)
        improved = True
        loop_guard = 0
        while improved and loop_guard < 3:
            loop_guard += 1
            improved = False
            for i in range(count):
                lower = (a[i - 1] + sep) if i > 0 else sep
                upper = (a[i + 1] - sep) if i < count - 1 else math.pi / 2.0 - sep
                for direction in (-1.0, 1.0):
                    b = list(a)
                    b[i] = _ppwm_clamp(b[i] + direction * step, lower, upper)
                    b = _ppwm_sanitize_angles(b, count, sep)
                    s = score(b)
                    if s < best:
                        a = b
                        best = s
                        improved = True
    return a


@lru_cache(maxsize=128)
def _ppwm_continuous_table(kind: str, count: int) -> tuple[tuple[int, tuple[float, ...]], ...]:
    """SHE/CHM角度ROMを1%刻みで作る。

    v36では変調率ごとに独立して最適化していたため、複数あるSHE解の枝を
    行き来して波形が崩れることがあった。v37では低変調から高変調へ順番に
    解を追跡し、隣接する変調率の角度差が小さくなるようにする。
    """
    kind = str(kind).upper()
    if kind not in ("SHE", "CHM"):
        kind = "SHE"
    count = max(1, min(7, int(count)))
    bins = list(range(16, 201, 2))  # 8%〜100%、1%刻み。中間は線形補間。
    table: list[tuple[int, tuple[float, ...]]] = []
    prev: list[float] | None = None

    for mb in bins:
        m = _ppwm_clamp(mb / 200.0, 0.08, 1.0)
        if prev is None:
            # 初回だけ複数シードを比較する。以後は前回解からの追跡にする。
            candidates = _ppwm_initial_angle_sets(count, m)
            best = None
            best_score = float("inf")
            for seed in candidates:
                cand = _ppwm_refine_angles(kind, count, m, seed, None)
                score = _ppwm_objective(kind, cand, m)
                if score < best_score:
                    best = cand
                    best_score = score
            angles = best if best is not None else candidates[0]
        else:
            angles = _ppwm_refine_angles(kind, count, m, prev, prev)
        angles = _ppwm_post_optimize_flux(kind, count, m, angles)
        angles = _ppwm_sanitize_angles(angles, count, math.radians(1.7))
        table.append((mb, tuple(angles)))
        prev = angles

    return tuple(table)


def _ppwm_interp_from_table(kind: str, count: int, m: float) -> tuple[float, ...]:
    table = _ppwm_continuous_table(kind, count)
    mb = _ppwm_clamp(float(m), 0.08, 1.0) * 200.0
    if mb <= table[0][0]:
        return table[0][1]
    if mb >= table[-1][0]:
        return table[-1][1]
    # 1%刻みテーブルの間を補間し、変調率スライダーや加速で角度が階段状に
    # 変化して波形が跳ねるのを防ぐ。
    for i in range(len(table) - 1):
        b0, a0 = table[i]
        b1, a1 = table[i + 1]
        if b0 <= mb <= b1:
            t = (mb - b0) / max(1e-9, (b1 - b0))
            return tuple((1.0 - t) * a0[j] + t * a1[j] for j in range(count))
    return table[-1][1]


@lru_cache(maxsize=2048)
def _ppwm_programmed_angles_cached(kind: str, pulse_key: int, mod_key: int) -> tuple[float, ...]:
    """SHE/CHM角度補間結果のキャッシュ。

    v55:
    CHMが重くなる主因は、オシロ波形・ベクトル軌跡の各サンプルで
    ppwm_programmed_angles() が何度も呼ばれ、同じ変調率の角度補間を
    繰り返していたこと。変調率を0.1%刻みに量子化してキャッシュする。
    """
    kind = str(kind).upper()
    if kind not in ("SHE", "CHM"):
        kind = "SHE"
    pulse_key = _ppwm_normalize_pulse_count(pulse_key)
    count = _ppwm_angle_count(pulse_key)
    m = _ppwm_clamp(int(mod_key) / 1000.0, 0.0, 1.0)
    return _ppwm_interp_from_table(kind, count, m)


def ppwm_programmed_angles(kind: str, pulse_value: int, modulation: float) -> tuple[float, ...]:
    kind = str(kind).upper()
    if kind not in ("SHE", "CHM"):
        kind = "SHE"
    pulse_key = _ppwm_normalize_pulse_count(int(round(float(pulse_value))))
    mod_key = int(round(_ppwm_clamp(float(modulation), 0.0, 1.0) * 1000.0))
    return _ppwm_programmed_angles_cached(kind, pulse_key, mod_key)


# ============================================================
# v45: SHE half-wave pulse train helper
# ============================================================
@lru_cache(maxsize=768)
def _she_halfwave_intervals_cached(pulse_key: int, mod_key: int) -> tuple[tuple[float, float], ...]:
    """SHE半波ON区間のキャッシュ本体。

    v53:
    v52では「SHE値=相脚側の半周期パルス数」としていたため、
    相間電圧UV/VW/WUでは U相とV相のエッジが合成され、
    ほぼ 2*N + 1 本に見えてしまった。
    例: SHE7指定 → 相脚7本 → 相間電圧約15本。

    通常、画面で確認したい「SHE7」「SHE15」などは相間電圧側の
    半周期パルス数として見るほうが分かりやすいので、
    ここでは指定値を相間電圧の半周期パルス数とし、
    相脚側のパルス区間数を (指定値 - 1) / 2 に変換する。

    例:
      SHE7  -> 相脚3本  -> 相間電圧7パルス
      SHE15 -> 相脚7本  -> 相間電圧15パルス
      SHE21 -> 相脚10本 -> 相間電圧21パルス
      SHE27 -> 相脚13本 -> 相間電圧27パルス

    スイッチング角方式は維持し、半周期0..π内の
    (ON角, OFF角) テーブルとして生成する。
    """
    requested_line_pulses = max(1, min(127, int(round(float(pulse_key)))))
    # 相間電圧の半周期パルス数は通常奇数として扱う。
    # 偶数指定時は近い奇数相当に丸める。
    phase_pulses = max(1, min(63, int(round((requested_line_pulses - 1) / 2.0))))
    pulses = phase_pulses
    modulation = _ppwm_clamp(mod_key / 1000.0, 0.0, 1.0)

    # 端部に少し余白を作り、中心付近はやや太く、端部はやや細くする。
    # 高変調ではパルス幅が広がるが、隣接パルスがつながって本数が減って見えないように上限を抑える。
    margin = math.pi * (0.012 + 0.028 * (1.0 - modulation))
    usable = math.pi - 2.0 * margin
    pitch = usable / pulses

    # 低変調でも波形確認できる最小幅を持たせる。高変調でも1ピッチの約70%まで。
    duty_base = 0.105 + 0.525 * modulation

    intervals: list[tuple[float, float]] = []
    for i in range(pulses):
        center = margin + pitch * (i + 0.5)

        # SHEらしく中央付近を少し太く、端部を細くする。
        env = math.sin(center)
        width = pitch * duty_base * (0.72 + 0.28 * (max(0.0, env) ** 0.70))

        # 終端側に見える細パルス群を少しだけ強調。ただし本数が潰れないよう制限。
        if i >= pulses - max(2, pulses // 7):
            width *= 1.08

        width = _ppwm_clamp(width, pitch * 0.040, pitch * 0.700)

        a = max(0.0, center - width * 0.5)
        b = min(math.pi, center + width * 0.5)
        if b - a > math.radians(0.03):
            intervals.append((a, b))

    return tuple(intervals)


def she_halfwave_intervals_from_angles(pulse_value: int, modulation: float) -> tuple[tuple[float, float], ...]:
    """SHEの値を相間電圧の半周期パルス数として、相脚側ON角/OFF角テーブルを返す。

    v53ではSHE7指定ならUV/VW/WUの相間電圧で7パルスになるようにする。
    計算結果はキャッシュする。
    """
    pulse_key = max(1, int(round(float(pulse_value))))
    mod_key = int(round(_ppwm_clamp(float(modulation), 0.0, 1.0) * 1000.0))
    return _she_halfwave_intervals_cached(pulse_key, mod_key)


def she_halfwave_switch_scalar(theta: float, pulse_value: int, modulation: float) -> float:
    """SHE専用の2レベル半波パルス列。

    0〜π: ON区間は+1、OFF区間は-1
    π〜2π: ON区間は-1、OFF区間は+1

    各相脚は必ず+1/-1の2レベルで、0レベルは使わない。
    """
    x = theta % TAU
    positive_half = x < math.pi
    h = x if positive_half else x - math.pi
    intervals = she_halfwave_intervals_from_angles(pulse_value, modulation)
    on = any(a <= h < b for a, b in intervals)
    half_sign = 1.0 if positive_half else -1.0
    return half_sign if on else -half_sign


def she_halfwave_switch_np(theta, pulse_value: int, modulation: float, np):
    """SHE専用2レベル半波パルス列のnumpy版。"""
    x = theta % np.float32(TAU)
    positive_half = x < np.float32(math.pi)
    h = np.where(positive_half, x, x - np.float32(math.pi))
    intervals = she_halfwave_intervals_from_angles(pulse_value, modulation)

    on = np.zeros_like(theta, dtype=bool)
    for a, b in intervals:
        on = on | ((h >= np.float32(a)) & (h < np.float32(b)))

    half_sign = np.where(positive_half, np.float32(1.0), np.float32(-1.0))
    return np.where(on, half_sign, -half_sign).astype(np.float32)


def she_line_polarity_scalar(line_val: float, theta_line: float) -> float:
    """SHEの相間電圧パルス極性補正。

    v48:
    v45のSHEは相脚の2レベル波形としては成立しているが、相間電圧で見ると
    一部の細いパルスだけ、基本波半周期に対して上下が逆に見える。
    文献上のSHEはスイッチング角列を基本波半周期に対して配置するため、
    相間電圧として表示する細いパルスは、その相間基本波の半周期極性に
    揃えるのが自然。

    ここではSHEだけ、UV/VW/WUそれぞれの相間基本波角から期待極性を求め、
    逆向きの細いパルスだけを反転する。波形全体は反転しない。
    """
    if abs(line_val) < 1e-12:
        return 0.0
    target = 1.0 if math.sin(theta_line) >= 0.0 else -1.0
    return abs(line_val) * target


def she_line_polarity_np(line_val, theta_line, np):
    """SHE相間電圧パルス極性補正のnumpy版。"""
    target = np.where(np.sin(theta_line) >= np.float32(0.0), np.float32(1.0), np.float32(-1.0))
    return np.abs(line_val) * target


MODE_LABELS = {
    "ASYNC": "非同期PWM",
    "SYNC": "同期PWM",
    "SHE": "SHE-PWM",
    "CHM": "CHM-PWM",
    "WIDE3": "広域3パルス",
    "ONEPULSE": "1パルス",
}

MODE_ALIASES = {
    "ASYNC": "ASYNC", "ASYNCHRONOUS": "ASYNC", "非同期": "ASYNC", "非同期PWM": "ASYNC",
    "SYNC": "SYNC", "SYNCHRONOUS": "SYNC", "同期": "SYNC", "同期PWM": "SYNC",
    "SHE": "SHE", "SHEPWM": "SHE", "SHE-PWM": "SHE",
    "CHM": "CHM", "CHMPWM": "CHM", "CHM-PWM": "CHM",
    "WIDE3": "WIDE3", "WIDE": "WIDE3", "3PULSE": "WIDE3", "3パルス": "WIDE3", "広域3パルス": "WIDE3",
    "ONEPULSE": "ONEPULSE", "ONE": "ONEPULSE", "1PULSE": "ONEPULSE", "1パルス": "ONEPULSE",
}

HF_LABELS = {
    "OFF": "OFF",
    "SINE": "正弦重畳",
    "TRI": "三角重畳",
    "SQUARE": "矩形重畳",
    "CARRIER": "PMSM高周波注入",
}

SPREAD_LABELS = {
    "OFF": "OFF",
    "SINE": "SW周波数サイン拡散",
    "TRI": "SW周波数三角拡散",
    "RANDOM": "SW周波数ランダム拡散",
    "STEP": "SW周波数段階拡散",
}

HF_ALIASES = {
    "OFF": "OFF", "NONE": "OFF", "無し": "OFF", "なし": "OFF", "無": "OFF",
    "SINE": "SINE", "SIN": "SINE", "正弦": "SINE", "正弦波": "SINE", "正弦重畳": "SINE",
    "TRI": "TRI", "TRIANGLE": "TRI", "三角": "TRI", "三角波": "TRI", "三角重畳": "TRI",
    "SQUARE": "SQUARE", "SQ": "SQUARE", "矩形": "SQUARE", "方形": "SQUARE", "矩形重畳": "SQUARE",
    # v64: Combobox表示文字そのものを受け付ける。これが無いと「PMSM高周波注入」を選んだ時にOFFへ落ちる。
    "CARRIER": "CARRIER", "CARRIER_SIDE": "CARRIER",
    "PMSM": "CARRIER", "HFI": "CARRIER", "HF_INJECTION": "CARRIER",
    "PMSM高周波注入": "CARRIER", "PMSM高周波": "CARRIER", "PMSM高周波重畳": "CARRIER",
    "PMSM高周波電圧注入": "CARRIER", "高周波注入": "CARRIER", "高周波電圧注入": "CARRIER",
    "側帯": "CARRIER", "キャリア": "CARRIER", "キャリア側帯": "CARRIER",
}

SPREAD_ALIASES = {
    "OFF": "OFF", "NONE": "OFF", "無し": "OFF", "なし": "OFF", "無": "OFF",
    "SINE": "SINE", "SIN": "SINE", "正弦": "SINE", "サイン": "SINE", "サイン拡散": "SINE", "SW周波数サイン拡散": "SINE", "スイッチング周波数サイン拡散": "SINE",
    "TRI": "TRI", "TRIANGLE": "TRI", "三角": "TRI", "三角拡散": "TRI", "SW周波数三角拡散": "TRI", "スイッチング周波数三角拡散": "TRI",
    "RANDOM": "RANDOM", "RAND": "RANDOM", "ランダム": "RANDOM", "乱数": "RANDOM", "ランダム拡散": "RANDOM", "SW周波数ランダム拡散": "RANDOM", "スイッチング周波数ランダム拡散": "RANDOM",
    "STEP": "STEP", "段階": "STEP", "ステップ": "STEP", "段階拡散": "STEP", "SW周波数段階拡散": "STEP", "スイッチング周波数段階拡散": "STEP",
}

DEFAULT_PATTERN_TEXT = """# 上限km/h, 方式, 値, 名前, 高周波重畳, 重畳量%, 重畳Hz, 拡散方式, 拡散量%, 拡散Hz
# 方式: ASYNC / SYNC / SHE / CHM / WIDE3 / ONEPULSE
# 値: ASYNC=キャリアHz。750-1050 のように書くと速度域内で上昇/下降。SYNC=同期パルス数, CHM=CHMパルス数, SHE=相間電圧の半周期パルス数, WIDE3=3, ONEPULSE=1
# 高周波重畳: OFF / SINE / TRI / SQUARE / CARRIER(PMSM高周波注入), 重畳Hz=20〜2000
# 拡散方式: OFF / SINE / TRI / RANDOM / STEP
8,   ASYNC,    2300, 起動 非同期,      SINE,    8, RANDOM, 4
25,  SYNC,       45, 同期45,           SINE,    5, TRI,    3
45,  SYNC,       33, 同期33,           TRI,     5, SINE,   3
65,  CHM,        27, CHM27,            CARRIER, 6, SINE,   4
88,  CHM,        21, CHM21,            CARRIER, 5, TRI,    4
108, SHE,        15, SHE15,            SQUARE,  4, STEP,   3
124, WIDE3,       3, 広域3パルス,      OFF,     0, OFF,    0
999, ONEPULSE,    1, 1パルス,          OFF,     0, OFF,    0
"""


PATTERN_PRESETS = {
    "標準: 非同期→同期→CHM→SHE→広域3→1P": [
        {"vmax": 8.0, "kind": "ASYNC", "value": 2300.0, "name": "起動 非同期", "hf_mode": "CARRIER", "hf_amount": 8.0, "spread_mode": "RANDOM", "spread_amount": 4.0},
        {"vmax": 25.0, "kind": "SYNC", "value": 45.0, "name": "同期45", "hf_mode": "SINE", "hf_amount": 5.0, "spread_mode": "TRI", "spread_amount": 3.0},
        {"vmax": 45.0, "kind": "SYNC", "value": 33.0, "name": "同期33", "hf_mode": "TRI", "hf_amount": 5.0, "spread_mode": "SINE", "spread_amount": 3.0},
        {"vmax": 65.0, "kind": "CHM", "value": 27.0, "name": "CHM27", "hf_mode": "CARRIER", "hf_amount": 6.0, "spread_mode": "SINE", "spread_amount": 4.0},
        {"vmax": 88.0, "kind": "CHM", "value": 21.0, "name": "CHM21", "hf_mode": "CARRIER", "hf_amount": 5.0, "spread_mode": "TRI", "spread_amount": 4.0},
        {"vmax": 108.0, "kind": "SHE", "value": 15.0, "name": "SHE15", "hf_mode": "SQUARE", "hf_amount": 4.0, "spread_mode": "STEP", "spread_amount": 3.0},
        {"vmax": 124.0, "kind": "WIDE3", "value": 3.0, "name": "広域3パルス", "hf_mode": "OFF", "hf_amount": 0.0, "spread_mode": "OFF", "spread_amount": 0.0},
        {"vmax": 999.0, "kind": "ONEPULSE", "value": 1.0, "name": "1パルス", "hf_mode": "OFF", "hf_amount": 0.0, "spread_mode": "OFF", "spread_amount": 0.0},
    ],
    "非同期重視: 低速を丸い音にする": [
        {"vmax": 12.0, "kind": "ASYNC", "value": 1800.0, "name": "低速 非同期1800", "hf_mode": "CARRIER", "hf_amount": 9.0, "spread_mode": "RANDOM", "spread_amount": 5.0},
        {"vmax": 28.0, "kind": "ASYNC", "value": 2600.0, "name": "中速 非同期2600", "hf_mode": "TRI", "hf_amount": 6.0, "spread_mode": "SINE", "spread_amount": 4.0},
        {"vmax": 52.0, "kind": "SYNC", "value": 39.0, "name": "同期39", "hf_mode": "SINE", "hf_amount": 4.0, "spread_mode": "TRI", "spread_amount": 3.0},
        {"vmax": 78.0, "kind": "CHM", "value": 27.0, "name": "CHM27", "hf_mode": "CARRIER", "hf_amount": 5.0, "spread_mode": "SINE", "spread_amount": 3.0},
        {"vmax": 105.0, "kind": "SHE", "value": 15.0, "name": "SHE15", "hf_mode": "SQUARE", "hf_amount": 3.0, "spread_mode": "STEP", "spread_amount": 2.0},
        {"vmax": 999.0, "kind": "ONEPULSE", "value": 1.0, "name": "1パルス", "hf_mode": "OFF", "hf_amount": 0.0, "spread_mode": "OFF", "spread_amount": 0.0},
    ],
    "同期重視: 音階がはっきり変わる": [
        {"vmax": 10.0, "kind": "ASYNC", "value": 2200.0, "name": "起動 非同期", "hf_mode": "SINE", "hf_amount": 6.0, "spread_mode": "RANDOM", "spread_amount": 3.0},
        {"vmax": 20.0, "kind": "SYNC", "value": 63.0, "name": "同期63", "hf_mode": "SINE", "hf_amount": 4.0, "spread_mode": "TRI", "spread_amount": 2.0},
        {"vmax": 36.0, "kind": "SYNC", "value": 45.0, "name": "同期45", "hf_mode": "SINE", "hf_amount": 4.0, "spread_mode": "TRI", "spread_amount": 2.0},
        {"vmax": 55.0, "kind": "SYNC", "value": 33.0, "name": "同期33", "hf_mode": "TRI", "hf_amount": 3.0, "spread_mode": "SINE", "spread_amount": 2.0},
        {"vmax": 76.0, "kind": "SYNC", "value": 27.0, "name": "同期27", "hf_mode": "TRI", "hf_amount": 3.0, "spread_mode": "SINE", "spread_amount": 2.0},
        {"vmax": 102.0, "kind": "SHE", "value": 15.0, "name": "SHE15", "hf_mode": "SQUARE", "hf_amount": 3.0, "spread_mode": "STEP", "spread_amount": 2.0},
        {"vmax": 999.0, "kind": "ONEPULSE", "value": 1.0, "name": "1パルス", "hf_mode": "OFF", "hf_amount": 0.0, "spread_mode": "OFF", "spread_amount": 0.0},
    ],
    "SHE/CHM重視: 高速域の粗い音": [
        {"vmax": 8.0, "kind": "ASYNC", "value": 2400.0, "name": "起動 非同期", "hf_mode": "SINE", "hf_amount": 8.0, "spread_mode": "RANDOM", "spread_amount": 4.0},
        {"vmax": 22.0, "kind": "SYNC", "value": 45.0, "name": "同期45", "hf_mode": "SINE", "hf_amount": 4.0, "spread_mode": "TRI", "spread_amount": 3.0},
        {"vmax": 42.0, "kind": "CHM", "value": 33.0, "name": "CHM33", "hf_mode": "CARRIER", "hf_amount": 6.0, "spread_mode": "SINE", "spread_amount": 4.0},
        {"vmax": 62.0, "kind": "CHM", "value": 27.0, "name": "CHM27", "hf_mode": "CARRIER", "hf_amount": 6.0, "spread_mode": "TRI", "spread_amount": 4.0},
        {"vmax": 84.0, "kind": "SHE", "value": 21.0, "name": "SHE21", "hf_mode": "SQUARE", "hf_amount": 4.0, "spread_mode": "STEP", "spread_amount": 3.0},
        {"vmax": 108.0, "kind": "SHE", "value": 15.0, "name": "SHE15", "hf_mode": "SQUARE", "hf_amount": 4.0, "spread_mode": "STEP", "spread_amount": 3.0},
        {"vmax": 128.0, "kind": "WIDE3", "value": 3.0, "name": "広域3パルス", "hf_mode": "OFF", "hf_amount": 0.0, "spread_mode": "OFF", "spread_amount": 0.0},
        {"vmax": 999.0, "kind": "ONEPULSE", "value": 1.0, "name": "1パルス", "hf_mode": "OFF", "hf_amount": 0.0, "spread_mode": "OFF", "spread_amount": 0.0},
    ],
}


# ============================================================
# 音声プロセス側: Tkinterを一切使わない
# ============================================================
def audio_worker(cmd_q, status_q, initial_params: dict):
    """別プロセスで動く音声生成処理。"""
    params = dict(initial_params)
    running = True
    fs = 48000
    # v16: underflow対策。256/lowでは共鳴・反響ON時にPortAudioへ供給が間に合わない場合があるため、
    # 音切れしにくい安定寄りのブロックサイズにする。
    blocksize = 1024
    phase_f = 0.0
    phase_c = 0.0
    phase_hf = 0.0
    phase_spread = 0.0
    phase_wind = 0.0
    # v15: ユーザー提供の通常録音（耳）/モハラジオ録音（磁界）を再解析し、
    # 通常録音側に寄せるための共鳴フィルタ/反響モード状態。
    # 通常録音は、モハラジオより800〜2500Hzの直接的なPWM成分が弱く、
    # 80〜300Hzの車体/床下の太さと、約668Hz/2.1kHz/3.15kHzの空気音ピークが目立つ。
    resonance_states = None
    ear_lp = 0.0
    ear_dark_lp1 = 0.0
    ear_dark_lp2 = 0.0
    ear_body_lp = 0.0
    ear_post_lp1 = 0.0
    ear_post_lp2 = 0.0
    echo_buf = None
    echo_pos = 0
    echo_lp = 0.0
    pink_b0 = 0.0
    pink_b1 = 0.0
    pink_b2 = 0.0
    roll_lp = 0.0
    roll_rumble = 0.0
    roll_body = 0.0
    spread_rand = 0.0
    # v58: ASYNCのキャリア周波数がGUI更新周期で階段状に変化すると、
    # 750→1050Hzのようなランプ時に音が途切れ途切れに感じる。
    # 音声プロセス側でキャリアをサンプル単位に補間するための状態。
    async_fc_smooth = 0.0
    last_pwm_kind_audio = ""
    last_status_time = 0.0

    try:
        import numpy as np
    except Exception as e:
        status_q.put({"type": "error", "message": f"numpyを読み込めません: {e}"})
        return

    rng = np.random.default_rng()

    try:
        import sounddevice as sd
    except Exception as e:
        status_q.put({"type": "error", "message": f"sounddeviceを読み込めません: {e}"})
        return

    # Nuitkaビルド軽量化:
    # 以前は任意で scipy.signal を使っていましたが、Nuitkaがscipy全体を解析・コンパイルし、
    # Visual C++のC1060/C1002（ヒープ不足）を起こしやすいため、exe化版では純Python/Numpy経路に固定します。
    sp_signal = None

    def clamp(x, lo, hi):
        return lo if x < lo else hi if x > hi else x

    def drain_commands():
        nonlocal params, running
        while True:
            try:
                msg = cmd_q.get_nowait()
            except queue.Empty:
                break
            except Exception:
                break
            if not isinstance(msg, dict):
                continue
            if msg.get("cmd") == "stop":
                running = False
                break
            params.update(msg)

    def triangle_wave(phase):
        frac = (phase / np.float32(TAU)) % np.float32(1.0)
        return np.float32(2.0) * np.abs(np.float32(2.0) * frac - np.float32(1.0)) - np.float32(1.0)

    def cat_ear_carrier_wave(phase):
        """同期5/12パルス等で使う猫耳キャリア近似。

        v81では表示・磁束計算の主ルートは下の sync_cat_ear_switch_np() に変更。
        この関数は互換用に残す。
        """
        frac = (phase / np.float32(TAU)) % np.float32(1.0)
        tri = np.float32(2.0) * np.abs(np.float32(2.0) * frac - np.float32(1.0)) - np.float32(1.0)
        d_top = np.minimum(frac, np.float32(1.0) - frac)
        d_bot = np.abs(frac - np.float32(0.5))
        ear_w = np.float32(0.135)
        top = np.clip(np.float32(1.0) - d_top / ear_w, np.float32(0.0), np.float32(1.0))
        bot = np.clip(np.float32(1.0) - d_bot / ear_w, np.float32(0.0), np.float32(1.0))
        top = top * top * (np.float32(3.0) - np.float32(2.0) * top)
        bot = bot * bot * (np.float32(3.0) - np.float32(2.0) * bot)
        cat = tri - np.float32(0.42) * top + np.float32(0.42) * bot
        return np.clip(cat, np.float32(-1.0), np.float32(1.0))

    def sync_cat_ear_switch_np(theta, pulse_value: int, modulation: float):
        """同期5パルス等の猫耳キャリア相当を直接パルス列で生成する。

        参考画像のように、
          正半波: 上側が連続し、途中に下向きノッチが入る
          負半波: 下側が連続し、途中に上向きノッチが入る
        という半波対称波形にする。

        以前のv79/v80はキャリア比較で近似したため、5パルス時に
        αβ磁束が星形・島状になった。ここでは猫耳キャリア比較で得たい
        最終的な2レベル相ゲート波形を直接作る。
        """
        p = max(1, int(round(float(pulse_value))))
        # v82:
        # 参考図の同期5パルスは、相電圧U/V側では正半波に2個の下向きノッチ、
        # 負半波に2個の上向きノッチが入り、相間電圧で5パルス相当になる。
        # v81は p-1 個=4個/半波を相電圧へ入れていたため、細かすぎる波形になっていた。
        notch_count = max(1, p // 2)

        x = theta % np.float32(TAU)
        half = x % np.float32(math.pi)
        sign = np.where(x < np.float32(math.pi), np.float32(1.0), np.float32(-1.0))

        # 変調率が高いほどノッチは細く、低いほど太い。
        # 5パルスでは参考図のように明確な矩形ノッチになるよう、p+1で過度に細くしない。
        m = max(0.0, min(1.0, float(modulation)))
        base_half_width = (0.018 + 0.038 * (1.0 - m)) * math.pi
        # 高パルス指定ではノッチが重ならないように少し狭める。
        scale = min(1.0, 5.0 / max(5.0, float(p)))
        width = np.float32(base_half_width * scale)

        notch = np.zeros_like(half, dtype=bool)
        for k in range(notch_count):
            # 半波内で左右対称に配置。p=5なら約60°/120°。
            center = np.float32(math.pi * (k + 1) / (notch_count + 1))
            notch |= np.abs(half - center) < width

        return np.where(notch, -sign, sign).astype(np.float32)

    def sync_cat_ear_states_np(theta, pulse_value: int, modulation: float):
        """(3+6n)以外の同期PWMを三相状態として生成する。

        v86:
        v85の猫耳ノッチ方式は同期5パルス専用に近い。
        そのまま12パルスへ適用すると、相電圧ノッチがピーク付近へ集中し、
        同期12パルスが不自然な波形になる。

        分岐:
          - 3/5/7パルスなど低パルス・奇数特殊同期: 参考図に近い猫耳ノッチ方式
          - 12パルス等の偶数特殊同期: 各相の基本波位相に同期した三角キャリア比較
            U: sin(θ)       vs tri(pθ)
            V: sin(θ-120°)  vs tri(p(θ-120°))
            W: sin(θ+120°)  vs tri(p(θ+120°))
        """
        p = max(1, int(round(float(pulse_value))))
        m = max(0.0, min(1.0, float(modulation)))

        def tri_np(phase):
            frac = (phase / np.float32(TAU)) % np.float32(1.0)
            return np.float32(2.0) * np.abs(np.float32(2.0) * frac - np.float32(1.0)) - np.float32(1.0)

        # v87:
        # 3/5/7パルスなどの低パルス・奇数特殊同期は、12パルス用の相別三角キャリア比較に入れると
        # 低パルス特有の磁束軌跡が星形に崩れる。奇数は猫耳ノッチ方式にする。
        # p=3 -> 各半波1ノッチ、線間電圧で2ノッチ=3パルス
        # p=5 -> 各半波2ノッチ、線間電圧で4ノッチ=5パルス
        # p=7 -> 各半波3ノッチ、線間電圧で6ノッチ=7パルス
        if p % 2 == 1:
            def phase_gate(phi):
                x = phi % np.float32(TAU)
                sign = np.where(x < np.float32(math.pi), np.float32(1.0), np.float32(-1.0))

                notch_count = max(1, (p - 1) // 2)
                step = math.radians(60.0 / notch_count)
                center0 = -0.5 * step * (notch_count - 1)
                offsets = [center0 + step * k for k in range(notch_count)]

                width = np.float32((0.010 + 0.022 * (1.0 - m)) * math.pi)
                # 7パルス以上はノッチ数が増えるので、少し狭くして重なりを防ぐ。
                if p > 5:
                    width *= np.float32(5.0 / float(p))
                width = np.float32(max(math.radians(1.5), min(math.radians(7.5), float(width))))

                notch = np.zeros_like(x, dtype=bool)
                for off in offsets:
                    c_pos = np.float32(math.pi / 2.0 + off)
                    c_neg = np.float32(3.0 * math.pi / 2.0 + off)
                    notch |= np.abs(x - c_pos) < width
                    notch |= np.abs(x - c_neg) < width

                return np.where(notch, -sign, sign).astype(np.float32)

            u = phase_gate(theta)
            v = phase_gate(theta - np.float32(TAU / 3.0))
            w = phase_gate(theta + np.float32(TAU / 3.0))
            return u, v, w

        # 12パルス等の偶数特殊同期は、猫耳ノッチ形を流用せず、相ごとの位相同期キャリア比較にする。
        th_u = theta
        th_v = theta - np.float32(TAU / 3.0)
        th_w = theta + np.float32(TAU / 3.0)
        ref_u = np.float32(m) * np.sin(th_u)
        ref_v = np.float32(m) * np.sin(th_v)
        ref_w = np.float32(m) * np.sin(th_w)
        tri_u = tri_np(np.float32(p) * th_u)
        tri_v = tri_np(np.float32(p) * th_v)
        tri_w = tri_np(np.float32(p) * th_w)

        u = np.where(ref_u >= tri_u, np.float32(1.0), np.float32(-1.0))
        v = np.where(ref_v >= tri_v, np.float32(1.0), np.float32(-1.0))
        w = np.where(ref_w >= tri_w, np.float32(1.0), np.float32(-1.0))
        return u.astype(np.float32), v.astype(np.float32), w.astype(np.float32)


    def square_wave(phase):
        return np.where(np.sin(phase) >= 0.0, np.float32(1.0), np.float32(-1.0))

    def spread_value(mode: str, phase_arr):
        mode = str(mode).upper()
        if mode == "SINE":
            return np.sin(phase_arr)
        if mode == "TRI":
            return triangle_wave(phase_arr)
        if mode == "STEP":
            frac = (phase_arr / np.float32(TAU)) % np.float32(1.0)
            step = np.floor(frac * np.float32(5.0)) / np.float32(2.0) - np.float32(1.0)
            return step
        if mode == "RANDOM":
            # ブロック内はゆっくり変化する疑似ランダム。完全乱数ではなく音切れしにくい形にする。
            return np.sin(phase_arr * np.float32(1.73) + np.float32(12.9898)) * np.sin(phase_arr * np.float32(0.37) + np.float32(78.233))
        return np.zeros_like(phase_arr, dtype=np.float32)

    def hf_wave(mode: str, phase_arr):
        mode = str(mode).upper()
        if mode == "SINE":
            return np.sin(phase_arr)
        if mode == "TRI":
            return triangle_wave(phase_arr)
        if mode == "SQUARE":
            return square_wave(phase_arr)
        if mode == "CARRIER":
            # v63: PMSM高周波注入の既定は矩形波寄り。
            # 以前の正弦FM側帯だけでは、東芝PMSM風の細かい重畳パルスになりにくかった。
            return square_wave(phase_arr + np.float32(0.12) * np.sin(phase_arr * np.float32(0.125)))
        return np.zeros_like(phase_arr, dtype=np.float32)

    def hfi_abc_np(mode: str, phase_arr, amount: float, modulation: float):
        """PMSM高周波電圧注入風の三相基準波補正を返す。

        v63:
        従来は U/V/W に120°ずらした高周波を単純加算していたため、
        「別の3相音が混ざる」だけで、提示画像のような非同期PWM上の細い
        上下重畳パルスになりにくかった。

        PMSMセンサレスで使われる高周波注入に寄せ、
        αβ固定座標へ高周波電圧を重畳し、それを三相へ逆変換する。
        SQUARE/CARRIERでは矩形高周波注入、SINE/TRIでは回転/三角注入にする。
        """
        mode = str(mode).upper()
        m = np.float32(max(0.0, min(1.0, float(modulation))))
        amt = np.float32(max(0.0, min(0.45, float(amount))))

        # 低電圧・低速域では高周波注入が相対的に目立つ。高電圧側では控えめ。
        inj_amp = amt * (np.float32(0.75) + np.float32(1.20) * (np.float32(1.0) - m))
        inj_amp = np.minimum(inj_amp, np.float32(0.32))

        if mode == "SINE":
            alpha = np.sin(phase_arr)
            beta = np.cos(phase_arr) * np.float32(0.72)
        elif mode == "TRI":
            alpha = triangle_wave(phase_arr)
            beta = triangle_wave(phase_arr - np.float32(math.pi / 2.0)) * np.float32(0.72)
        else:
            # SQUARE/CARRIER: 画像のような上下に細いパルスが乗る矩形注入。
            # β成分も少し入れると、三相相間電圧でPMSMらしい揺れになる。
            alpha = square_wave(phase_arr)
            beta = square_wave(phase_arr - np.float32(math.pi / 2.0)) * np.float32(0.58)

        hu = inj_amp * alpha
        hv = inj_amp * (-np.float32(0.5) * alpha + np.float32(0.8660254) * beta)
        hw = inj_amp * (-np.float32(0.5) * alpha - np.float32(0.8660254) * beta)
        return hu.astype(np.float32), hv.astype(np.float32), hw.astype(np.float32), inj_amp

    def programmed_angles(kind: str, pulse_value: int, modulation: float):
        """SHE/CHM用の四分波対称スイッチング角を返す。

        v36: 従来の等間隔風の簡易角度をやめ、SHEは低次非3倍高調波消去、
        CHMは電流高調波重み付き最小化を狙うプログラムドPWM角度にする。
        """
        return list(ppwm_programmed_angles(kind, pulse_value, modulation))

    def programmed_phase_wave(theta, kind: str, pulse_value: int, modulation: float):
        """SHE/広域3パルス/1パルス系の相スイッチング関数 ±1。

        v27の広域3パルスは、提示図に合わせて相ゲートを
        「立上り直前の補助短パルス + 中央の主パルス + 立下り直後の補助短パルス」
        として生成する。θ幅を変調率で変化させ、100%では1パルスに連続移行する。
        """
        if kind == "ONEPULSE":
            return np.where(np.sin(theta) >= 0.0, np.float32(1.0), np.float32(-1.0))

        if kind == "WIDE3":
            # v34: 広域3パルスは、ユーザー指定によりv27の波形へ完全に戻す。
            # 各相ゲートは「主パルス＋両端の補助短パルス」。
            # θ幅もv27と同じ 38°*(1-m)^0.72 を使う。
            x = theta % np.float32(TAU)
            m = np.float32(clamp(float(modulation), 0.0, 1.0))
            theta_max = np.float32(math.radians(38.0))
            theta_w = theta_max * np.float32((1.0 - float(m)) ** 0.72)
            main = (x >= theta_w) & (x < (np.float32(math.pi) - theta_w))
            aux_before = x >= (np.float32(TAU) - theta_w)
            aux_after = (x >= np.float32(math.pi)) & (x < (np.float32(math.pi) + theta_w))
            gate = main | aux_before | aux_after
            return np.where(gate, np.float32(1.0), np.float32(-1.0)).astype(np.float32)

        # v73: SHE/CHMを同じ2レベル・スイッチング角方式に統一。
        # SHEだけ半波パルス列へ分岐すると、CHMと波形・相間電圧・ベクトル軌跡の
        # 生成ルートがずれてしまうため、両方ともppwm_programmed_angles()を使う。
        angles = programmed_angles(kind, pulse_value, modulation)
        polarity = np.float32(_ppwm_polarity(len(angles)))
        x = theta % np.float32(TAU)
        half = x % np.float32(math.pi)
        q = np.where(half <= np.float32(math.pi / 2), half, np.float32(math.pi) - half)
        sign = np.where(x < np.float32(math.pi), np.float32(1.0), np.float32(-1.0))
        state = np.ones_like(theta, dtype=np.float32)
        for a in angles:
            state = np.where(q >= np.float32(a), -state, state)
        return polarity * sign * state

    def callback(outdata, frames, time_info, status):
        nonlocal phase_f, phase_c, phase_hf, phase_spread, phase_wind, resonance_states, ear_lp, ear_dark_lp1, ear_dark_lp2, ear_body_lp, ear_post_lp1, ear_post_lp2, echo_buf, echo_pos, echo_lp, pink_b0, pink_b1, pink_b2, roll_lp, roll_rumble, roll_body, spread_rand, async_fc_smooth, last_pwm_kind_audio, last_status_time, running
        try:
            drain_commands()

            if status:
                # v16: underflow警告自体の表示頻度も下げる。
                # 警告を隠すのではなく、音声処理は下のblocksize/latency/高速フィルタで安定化する。
                now = time.time()
                if now - last_status_time > 4.0:
                    try:
                        status_q.put_nowait({"type": "warn", "message": f"音声警告: {status}（処理が重い場合は共鳴量/反響量を少し下げてください）"})
                    except Exception:
                        pass
                    last_status_time = now

            f0 = float(params.get("f0", 0.0))
            pwm_kind = str(params.get("pwm_kind", "ASYNC")).upper()
            if pwm_kind not in MODE_LABELS:
                pwm_kind = "ASYNC"
            pattern_value = float(params.get("pattern_value", 0.0))
            carrier = float(params.get("carrier", 1200.0))
            sync_pulses = max(1, int(params.get("sync_pulses", 21)))
            volume = clamp(float(params.get("volume", 0.0)), 0.0, 1.0)
            modulation = clamp(float(params.get("modulation", 0.0)), 0.0, 1.0)
            load = clamp(float(params.get("load", 0.5)), 0.0, 1.2)
            roughness = clamp(float(params.get("roughness", 0.25)), 0.0, 1.0)
            notch = int(params.get("notch", 0))
            drive_active = bool(params.get("drive_active", notch != 0))
            hf_mode = str(params.get("hf_mode", "OFF")).upper()
            hf_amount = clamp(float(params.get("hf_amount", 0.0)), 0.0, 0.45)
            hf_freq = clamp(float(params.get("hf_freq", 750.0)), 20.0, 2000.0)
            spread_mode = str(params.get("spread_mode", "OFF")).upper()
            spread_amount = clamp(float(params.get("spread_amount", 0.0)), 0.0, 0.35)
            spread_rate = clamp(float(params.get("spread_rate", 3.0)), 0.05, 40.0)
            speed_ratio_audio = clamp(float(params.get("speed_ratio", 0.0)), 0.0, 1.2)
            wind_enabled = bool(params.get("wind_enabled", False))
            wind_amount = clamp(float(params.get("wind_amount", 0.0)), 0.0, 1.5)
            rolling_enabled = bool(params.get("rolling_enabled", False))
            rolling_amount = clamp(float(params.get("rolling_amount", 0.0)), 0.0, 1.5)
            # v9: 耳補正。共鳴フィルタはモータ/台車/車体の鳴りを作り、反響は車内/床下反射を作る。
            resonance_enabled = bool(params.get("resonance_enabled", False))
            resonance_amount = clamp(float(params.get("resonance_amount", 0.0)), 0.0, 5.0)
            resonance_shift = clamp(float(params.get("resonance_shift", 1.0)), 0.55, 1.8)
            echo_enabled = bool(params.get("echo_enabled", False))
            echo_amount = clamp(float(params.get("echo_amount", 0.0)), 0.0, 5.0)
            echo_delay_ms = clamp(float(params.get("echo_delay_ms", 70.0)), 20.0, 260.0)
            # v18: モーター電圧0%時/100%時のPWM音量をGUIで指定できるようにする。
            voltage_gain_0 = clamp(float(params.get("voltage_gain_0", 0.15)), 0.0, 5.0)
            voltage_gain_100 = clamp(float(params.get("voltage_gain_100", 1.20)), 0.0, 5.0)
            # v14由来: 起動時に音が消えすぎないよう、現在の疑似モーター電力も補助的に使う。
            motor_kw_ratio = clamp(abs(float(params.get("motor_kw_ratio", 0.0))), 0.0, 2.5)

            # PWM種別ごとのキャリア/パルス設定
            pulse_value = max(1, int(round(pattern_value or sync_pulses)))
            if pwm_kind == "ASYNC":
                fc = clamp(pattern_value if pattern_value > 10 else carrier, 40.0, 12000.0)
            elif pwm_kind == "WIDE3":
                pulse_value = 3
                fc = clamp(f0 * 3.0 if f0 >= 0.4 else 60.0, 30.0, 9000.0)
            elif pwm_kind == "ONEPULSE":
                pulse_value = 1
                fc = clamp(f0 if f0 >= 0.4 else 30.0, 20.0, 9000.0)
            else:
                fc = clamp(f0 * pulse_value if f0 >= 0.4 else 80.0, 40.0, 12000.0)

            # v12: 中立ノッチではインバータ音だけをOFFにする。
            # 速度が残っている場合は、走行ノイズ/転動音だけを鳴らせる。
            inverter_active = bool(drive_active and f0 > 0.02 and modulation > 0.001)
            non_inverter_active = bool(speed_ratio_audio > 0.01 and ((wind_enabled and wind_amount > 0.0001) or (rolling_enabled and rolling_amount > 0.0001)))
            if volume <= 0.0001 or (not inverter_active and not non_inverter_active):
                outdata[:] = 0
                return

            t = np.arange(frames, dtype=np.float32) / np.float32(fs)
            theta = phase_f + np.float32(TAU * f0) * t

            spread_phase_arr = phase_spread + np.float32(TAU * spread_rate) * t
            if spread_mode == "RANDOM" and spread_amount > 0.0001:
                # ランダム拡散はブロックごとの急な乱数ではなく、前値→目標値へ滑らかに補間する。
                # これをスイッチング周波数fcそのものに掛ける。
                spread_target = float(rng.uniform(-1.0, 1.0))
                spread_base = np.linspace(np.float32(spread_rand), np.float32(spread_target), frames, dtype=np.float32)
                spread_rand = spread_target
            else:
                spread_base = spread_value(spread_mode, spread_phase_arr)
            spread = np.clip(spread_base * np.float32(spread_amount), -np.float32(0.85), np.float32(0.85))

            # v7: 拡散方式は「音声を揺らす」のではなく、三角キャリアの瞬時スイッチング周波数を拡散する。
            # 位相は fc_inst * t ではなく、瞬時周波数の積分で作る。
            # v58: ASYNCではGUI側の33ms更新でfcが階段状に変わると途切れ感が出るため、
            #      音声ブロック内で前回fc→今回fcへ滑らかに補間する。
            if pwm_kind == "ASYNC":
                if last_pwm_kind_audio != "ASYNC" or async_fc_smooth <= 1.0:
                    async_fc_smooth = float(fc)

                # v59:
                # v58は「各音声ブロックの先頭→末尾で現在targetへ到達」する線形補間だったため、
                # GUIからtargetが25〜33msごとに更新されると、1050→750Hzの下降時に
                # 小さな階段として聞こえることがあった。
                #
                # ここでは音声サンプルごとの1次追従に変更し、targetが階段状に来ても
                # 実際に使うfcは連続曲線で動くようにする。
                # 下降時は少し遅めの時定数にして、段差感を特に抑える。
                target_fc = float(fc)
                fc_base_arr = np.empty(frames, dtype=np.float32)
                fc_cur = float(async_fc_smooth)
                tau_s = 0.115 if target_fc < fc_cur else 0.075
                alpha = 1.0 - math.exp(-1.0 / max(1.0, fs * tau_s))

                # 大きな表切替時だけ追従が遅すぎないよう、1サンプルごとの最大変化も入れる。
                max_step = 1800.0 / fs
                for ii in range(frames):
                    diff = target_fc - fc_cur
                    step = diff * alpha
                    if step > max_step:
                        step = max_step
                    elif step < -max_step:
                        step = -max_step
                    fc_cur += step
                    fc_base_arr[ii] = np.float32(fc_cur)

                async_fc_smooth = fc_cur
            else:
                async_fc_smooth = float(fc)
                fc_base_arr = np.full(frames, np.float32(fc), dtype=np.float32)
            last_pwm_kind_audio = pwm_kind

            fc_inst = np.clip(fc_base_arr * (np.float32(1.0) + spread), np.float32(20.0), np.float32(18000.0))
            fc_mean = float(np.mean(fc_inst))
            # cumsumをそのまま使うと先頭サンプルが1サンプル分進みすぎるため、直前値を引いて0開始にする。
            fc_phase_inc = np.cumsum(fc_inst, dtype=np.float32) - fc_inst[0]
            ctheta = phase_c + np.float32(TAU / fs) * fc_phase_inc
            hf_phase_arr = phase_hf + np.float32(TAU * hf_freq) * t

            phase_f = float((phase_f + TAU * f0 * frames / fs) % TAU)
            phase_c = float((phase_c + TAU * float(np.sum(fc_inst)) / fs) % TAU)
            phase_hf = float((phase_hf + TAU * hf_freq * frames / fs) % TAU)
            phase_spread = float((phase_spread + TAU * spread_rate * frames / fs) % TAU)
            wind_rate = 1.4 + 5.5 * speed_ratio_audio
            phase_wind = float((phase_wind + TAU * wind_rate * frames / fs) % TAU)

            # 電圧指令でPWM音そのものの強さ・粗さを変える。
            # v18: 指数固定ではなく、
            #      「モーター電圧0%時のPWM音量」と「モーター電圧100%時のPWM音量」を
            #      GUIで指定し、その間を滑らかにつなぐ。
            #      疑似モーター電力は低電圧起動時の補助として使うが、最終ゲインは指定範囲内に収める。
            #      1パルスは常に最大電圧扱い。
            if pwm_kind == "ONEPULSE":
                voltage_ratio_audio = np.float32(1.0)
            else:
                voltage_ratio_audio = np.float32(clamp(modulation / 1.0, 0.0, 1.0))
            vr = float(voltage_ratio_audio)
            # 電力補助は、低電圧でも負荷があると少しだけ100%側へ寄せる。
            # vr=1.0では必ず100%側、vr=0.0かつ電力0では必ず0%側になる。
            gain_pos = clamp(vr + (1.0 - vr) * 2.0 * motor_kw_ratio, 0.0, 1.0)
            gain_pos_rough = clamp(vr + (1.0 - vr) * 1.2 * motor_kw_ratio, 0.0, 1.0)
            voltage_pwm_gain = np.float32(voltage_gain_0 + (voltage_gain_100 - voltage_gain_0) * gain_pos)
            voltage_hum_gain = np.float32(voltage_gain_0 + (voltage_gain_100 - voltage_gain_0) * gain_pos)
            voltage_rough_gain = np.float32(voltage_gain_0 + (voltage_gain_100 - voltage_gain_0) * gain_pos_rough)
            inverter_level = np.float32(1.0 if inverter_active else 0.0)

            if pwm_kind in ("SHE", "CHM", "WIDE3", "ONEPULSE"):
                # v73: SHE/CHMは同じプログラムドPWM経路に統一。
                # どちらもスイッチング角の微小揺れとして拡散を扱う。
                # 1パルス/広域3パルスは基本波同期なので拡散を掛けない。
                if pwm_kind in ("SHE", "CHM") and spread_amount > 0.0001 and spread_mode != "OFF":
                    theta_sw = theta + spread * np.float32(0.22)
                else:
                    theta_sw = theta
                pu = programmed_phase_wave(theta_sw, pwm_kind, pulse_value, modulation)
                pv = programmed_phase_wave(theta_sw - np.float32(TAU / 3.0), pwm_kind, pulse_value, modulation)
                pw = programmed_phase_wave(theta_sw + np.float32(TAU / 3.0), pwm_kind, pulse_value, modulation)
                pwm_gain = np.float32(0.70 if pwm_kind in ("SHE", "CHM") else (0.76 if pwm_kind == "WIDE3" else 0.62))
            else:
                sync_cat = (pwm_kind == "SYNC" and sync_cat_ear_required(pulse_value))
                if sync_cat:
                    # v81: 猫耳キャリア系は、比較キャリアではなく半波対称の
                    # 上下ノッチ型パルス列として直接生成する。
                    tri = None
                else:
                    tri = triangle_wave(ctheta)
                ma = np.float32(modulation)
                # v63: 高周波重畳は三相120°の単純加算ではなく、αβ高周波電圧注入として生成。
                # 非同期PWM 750Hz + 高周波重畳時に、提示画像のような細かい上下パルスになりやすい。
                hf_ref_u, hf_ref_v, hf_ref_w, hf_inj_amp = hfi_abc_np(hf_mode, hf_phase_arr, hf_amount, modulation)

                if pwm_kind == "CHM":
                    # CHM-PWM簡易モデル: 3次・5次・7次の補償注入で音色を変える
                    # 実機のCHM最適化ではなく、音作り用。
                    def chm_ref(x):
                        return (
                            np.sin(x)
                            + np.float32(0.155) * np.sin(np.float32(3.0) * x)
                            - np.float32(0.045) * np.sin(np.float32(5.0) * x)
                            + np.float32(0.025) * np.sin(np.float32(7.0) * x)
                        )
                    u = ma * chm_ref(theta)
                    v = ma * chm_ref(theta - np.float32(TAU / 3.0))
                    w = ma * chm_ref(theta + np.float32(TAU / 3.0))
                    pwm_gain = np.float32(0.56)
                elif pwm_kind == "WIDE3":
                    # 広域3パルス: 低い同期キャリア + やや過変調寄り
                    mm = np.float32(min(1.0, modulation * 1.15 + 0.05))
                    u = mm * np.sin(theta)
                    v = mm * np.sin(theta - np.float32(TAU / 3.0))
                    w = mm * np.sin(theta + np.float32(TAU / 3.0))
                    pwm_gain = np.float32(0.70)
                else:
                    u = ma * np.sin(theta)
                    v = ma * np.sin(theta - np.float32(TAU / 3.0))
                    w = ma * np.sin(theta + np.float32(TAU / 3.0))
                    pwm_gain = np.float32(0.52)

                # 高周波重畳: 基準波に微小な高周波成分を加えてPWM音色を変化させる。
                if hf_mode != "OFF" and hf_amount > 0.0001:
                    u = np.clip(u + hf_ref_u, -np.float32(1.25), np.float32(1.25))
                    v = np.clip(v + hf_ref_v, -np.float32(1.25), np.float32(1.25))
                    w = np.clip(w + hf_ref_w, -np.float32(1.25), np.float32(1.25))

                if sync_cat:
                    pu, pv, pw = sync_cat_ear_states_np(theta, pulse_value, modulation)
                    pwm_gain = np.float32(0.58)
                else:
                    pu = np.where(u >= tri, np.float32(1.0), np.float32(-1.0))
                    pv = np.where(v >= tri, np.float32(1.0), np.float32(-1.0))
                    pw = np.where(w >= tri, np.float32(1.0), np.float32(-1.0))

            line_uv = (pu - pv) * np.float32(0.5)
            line_vw = (pv - pw) * np.float32(0.25)
            # v73: SHE/CHMの相間電圧は同じ脚状態差分で計算する。
            # SHEだけの後段極性補正は廃止し、差分がそのまま波形になるよう統一。
            pwm_tone = (line_uv + line_vw) * pwm_gain * voltage_pwm_gain * inverter_level

            # v63: PMSM高周波注入は、PWM比較波形だけでなく音としても細い「重畳感」を作る。
            # ただし単純なサイン音ではなく、矩形注入由来の奇数高調波を薄く混ぜる。
            if hf_mode != "OFF" and hf_amount > 0.0001 and inverter_active:
                hfi_edge = (
                    np.float32(0.045) * hf_wave(hf_mode, hf_phase_arr)
                    + np.float32(0.018) * hf_wave(hf_mode, np.float32(3.0) * hf_phase_arr)
                    + np.float32(0.010) * np.sin(np.float32(2.0) * hf_phase_arr + np.float32(0.15) * theta)
                )
                # 低速・低電圧側ほど注入音を少し目立たせる。上限は控えめ。
                hfi_gain = np.float32(hf_amount) * (np.float32(0.40) + np.float32(0.80) * (np.float32(1.0) - voltage_ratio_audio))
                pwm_tone = pwm_tone + hfi_edge * hfi_gain * voltage_pwm_gain * inverter_level

            # v58: 低いASYNCキャリアではPWMパルスが粗く、ブツブツ/途切れっぽく聞こえやすい。
            # PWM波形はそのまま残しつつ、キャリアの連続成分を少量だけ足して「細かく鳴る」感じにする。
            if pwm_kind == "ASYNC" and inverter_active:
                async_fill = (
                    np.float32(0.060) * np.sin(ctheta)
                    + np.float32(0.028) * np.sin(np.float32(2.0) * ctheta + np.float32(0.35) * np.sin(theta * np.float32(6.0)))
                    + np.float32(0.018) * np.sin(np.float32(3.0) * ctheta)
                )
                # 低キャリアほど少し多め、高キャリアでは控えめ。
                fill_gain = np.float32(max(0.25, min(1.0, 1400.0 / max(1400.0, fc_mean))))
                pwm_tone = pwm_tone + async_fill * fill_gain * voltage_pwm_gain * inverter_level

            if hf_mode != "OFF" and hf_amount > 0.0001:
                hf_audio = hf_wave(hf_mode, hf_phase_arr + np.float32(0.30) * np.sin(theta * np.float32(6.0)))
                pwm_tone = pwm_tone + np.float32(0.10) * np.float32(hf_amount) * hf_audio * voltage_pwm_gain * inverter_level

            # 電動機のうなり成分
            hum = (
                np.float32(0.30) * np.sin(theta * np.float32(2.0))
                + np.float32(0.18) * np.sin(theta * np.float32(6.0))
                + np.float32(0.08) * np.sin(theta * np.float32(12.0))
            ) * voltage_hum_gain * inverter_level

            # モード別の側帯波。SHE/WIDE3は荒く、CHMは少し滑らか
            mode_rough = {
                "ASYNC": 0.18,
                "SYNC": 0.24,
                "CHM": 0.13,
                "SHE": 0.30,
                "WIDE3": 0.34,
                "ONEPULSE": 0.22,
            }.get(pwm_kind, 0.2)
            sideband = np.sin(ctheta + np.float32(0.75) * np.sin(theta * np.float32(6.0)))
            rough = np.float32(roughness * mode_rough) * sideband * voltage_rough_gain * inverter_level

            brake_factor = np.float32(1.0 + 0.10 * max(0, -notch))
            power_factor = np.float32(1.0 + 0.05 * max(0, notch))

            sig = (
                pwm_tone * (np.float32(0.20) + np.float32(load)) * power_factor
                + np.float32(0.42) * hum * (np.float32(0.25) + np.float32(load)) * brake_factor
                + rough
            )

            # 走行ノイズ/転動音は、共鳴フィルタへ入れずに最後に別系統で混ぜる。
            # これにより、ノイズ成分だけが車体共鳴で不自然に鳴るのを防ぐ。
            acoustic_noise = np.zeros(frames, dtype=np.float32)

            # 走行音: 速度に伴って増える風切りノイズ。
            # v8: 「シュシュシュ」と周期的に揺れる原因になるLFO/三相位相連動を完全に廃止。
            # PWMや基本波とは独立した、常時ランダムな単独の「シャー」という音にする。
            # Nでは完全無音にするため、drive_active判定後にだけ混ぜる。ON/OFF可能。
            if wind_enabled and wind_amount > 0.0001 and speed_ratio_audio > 0.01:
                white = rng.standard_normal(frames).astype(np.float32)
                pink = np.empty(frames, dtype=np.float32)
                for i in range(frames):
                    x = float(white[i])
                    # Paul Kellet型の軽量ピンクノイズ近似。状態を保持するのでブロック境界で途切れにくい。
                    pink_b0 = 0.99765 * pink_b0 + x * 0.0990460
                    pink_b1 = 0.96300 * pink_b1 + x * 0.2965164
                    pink_b2 = 0.57000 * pink_b2 + x * 1.0526913
                    pink[i] = np.float32((pink_b0 + pink_b1 + pink_b2 + x * 0.1848) * 0.075)

                # ピンクだけだと低域寄りで「ゴー」になりやすいので、少量の白色成分を混ぜて
                # 風切りに近い「シャー」を作る。ただし周期変調は一切掛けない。
                wind_hiss = pink * np.float32(0.82) + white * np.float32(0.18)
                wind_gain = np.float32(wind_amount) * np.float32(speed_ratio_audio ** 0.72)
                wind = wind_hiss * wind_gain * np.float32(3.25)
                acoustic_noise = acoustic_noise + wind

            # 転動音: 車輪・軌道・機械摩擦の「ゴー/ザー」という成分。
            # インバータとは独立しているため、ノッチNでも速度が残っていれば鳴る。
            if rolling_enabled and rolling_amount > 0.0001 and speed_ratio_audio > 0.01:
                white2 = rng.standard_normal(frames).astype(np.float32)
                roll = np.empty(frames, dtype=np.float32)
                # 速度が上がるほど少し明るい転動音にする。
                a1 = float(math.exp(-TAU * (90.0 + 360.0 * speed_ratio_audio) / fs))
                a2 = float(math.exp(-TAU * (18.0 + 70.0 * speed_ratio_audio) / fs))
                a3 = float(math.exp(-TAU * (420.0 + 950.0 * speed_ratio_audio) / fs))
                prev_fast = roll_lp
                for i in range(frames):
                    xw = float(white2[i])
                    roll_lp = a1 * roll_lp + (1.0 - a1) * xw
                    roll_rumble = a2 * roll_rumble + (1.0 - a2) * xw
                    roll_body = a3 * roll_body + (1.0 - a3) * xw
                    grit = xw - roll_body
                    roll[i] = np.float32(0.85 * roll_lp + 0.55 * roll_rumble + 0.16 * grit)
                    prev_fast = roll_body
                roll_gain = np.float32(rolling_amount) * np.float32(speed_ratio_audio ** 0.92)
                acoustic_noise = acoustic_noise + roll * roll_gain * np.float32(1.85)

            # v15: 再解析ベースの耳向け共鳴/こもりフィルタ。
            # 通常録音（耳）は、モハラジオ録音よりも以下の傾向が強い。
            #   - 80〜300Hzの車体/床下の太い成分が相対的に大きい
            #   - 500〜800Hzのピークは残るが、800〜2500Hzの直接的なPWM線はかなり丸い
            #   - 4kHz以上は急に弱く、全体としてマイルドでこもった印象
            # そのため、単に1050Hzを持ち上げるのではなく、まずPWMエッジを暗くしてから
            # 低中域の広い車体共鳴を足し、2〜3kHzは薄い空気音としてだけ足す。
            if resonance_enabled and resonance_amount > 0.0001:
                # 通常録音のピーク/帯域感を元にした広めの共鳴。高域は弱め。
                centers = [95.0, 145.0, 220.0, 335.0, 455.0, 668.0, 1050.0, 2100.0, 3150.0]
                bandwidths = [95.0, 115.0, 150.0, 170.0, 190.0, 210.0, 300.0, 650.0, 920.0]
                gains = [0.70, 0.95, 0.90, 0.54, 0.48, 0.82, 0.30, 0.24, 0.18]
                if sp_signal is not None:
                    if (not isinstance(resonance_states, dict)) or resonance_states.get("n") != len(centers):
                        resonance_states = {"n": len(centers), "zi": [np.zeros(2, dtype=np.float64) for _ in centers]}
                else:
                    if resonance_states is None or not isinstance(resonance_states, list) or len(resonance_states) != len(centers) or len(resonance_states[0]) != 4:
                        resonance_states = [[0.0, 0.0, 0.0, 0.0] for _ in centers]

                x_raw = sig.astype(np.float32, copy=False)

                # コイル/磁界ピックアップ的に強くなりやすいPWMエッジを、通常録音のように丸める。
                # 2段ローパス相当のブレンドなので、ON/OFF差が分かりやすく、かつ極端な電話音になりにくい。
                dark_cut = 2500.0 - 650.0 * min(1.0, resonance_amount / 3.0)
                dark_cut = max(1550.0, min(3200.0, dark_cut))
                body_cut = 230.0
                alpha_dark = math.exp(-TAU * dark_cut / fs)
                alpha_body = math.exp(-TAU * body_cut / fs)
                dark_arr = np.empty(frames, dtype=np.float32)
                body_arr = np.empty(frames, dtype=np.float32)
                for i in range(frames):
                    xi = float(x_raw[i])
                    ear_dark_lp1 = alpha_dark * ear_dark_lp1 + (1.0 - alpha_dark) * xi
                    ear_dark_lp2 = alpha_dark * ear_dark_lp2 + (1.0 - alpha_dark) * ear_dark_lp1
                    ear_body_lp = alpha_body * ear_body_lp + (1.0 - alpha_body) * xi
                    dark_arr[i] = np.float32(ear_dark_lp2)
                    body_arr[i] = np.float32(ear_body_lp)

                dark_mix = np.float32(min(0.82, 0.24 + 0.18 * resonance_amount))
                body_mix = np.float32(min(0.85, 0.18 * resonance_amount))
                x = x_raw * (np.float32(1.0) - dark_mix) + dark_arr * dark_mix + body_arr * body_mix

                resonated = np.zeros(frames, dtype=np.float32)
                # RBJ型bandpassで広めに足す。狭いピークを立てすぎるとモハラジオ/電子音に戻るため、Qは低め。
                # v16: SciPyがある場合はlfilterで高速化し、output underflowを大幅に減らす。
                if sp_signal is not None:
                    zi_list = resonance_states["zi"]
                    x64 = x.astype(np.float64, copy=False)
                    for bi, (fc_res, bw_res, gain_res) in enumerate(zip(centers, bandwidths, gains)):
                        fc_r = max(35.0, min(7600.0, fc_res * resonance_shift))
                        q = max(0.22, min(8.0, fc_r / max(30.0, bw_res)))
                        w0 = TAU * fc_r / fs
                        sinw = math.sin(w0)
                        cosw = math.cos(w0)
                        alpha = sinw / (2.0 * q)
                        a0 = 1.0 + alpha
                        b = np.array([alpha / a0, 0.0, -alpha / a0], dtype=np.float64)
                        a = np.array([1.0, (-2.0 * cosw) / a0, (1.0 - alpha) / a0], dtype=np.float64)
                        y_arr, zi = sp_signal.lfilter(b, a, x64, zi=zi_list[bi])
                        zi_list[bi] = zi
                        resonated = resonated + y_arr.astype(np.float32, copy=False) * np.float32(gain_res)
                    resonance_states["zi"] = zi_list
                else:
                    for bi, (fc_res, bw_res, gain_res) in enumerate(zip(centers, bandwidths, gains)):
                        fc_r = max(35.0, min(7600.0, fc_res * resonance_shift))
                        q = max(0.22, min(8.0, fc_r / max(30.0, bw_res)))
                        w0 = TAU * fc_r / fs
                        sinw = math.sin(w0)
                        cosw = math.cos(w0)
                        alpha = sinw / (2.0 * q)
                        a0 = 1.0 + alpha
                        b0 = alpha / a0
                        b1 = 0.0
                        b2 = -alpha / a0
                        a1 = (-2.0 * cosw) / a0
                        a2 = (1.0 - alpha) / a0
                        x1, x2, y1, y2 = resonance_states[bi]
                        y_arr = np.empty(frames, dtype=np.float32)
                        for i in range(frames):
                            xi = float(x[i])
                            yv = b0 * xi + b1 * x1 + b2 * x2 - a1 * y1 - a2 * y2
                            x2 = x1
                            x1 = xi
                            y2 = y1
                            y1 = yv
                            y_arr[i] = np.float32(yv)
                        resonance_states[bi] = [x1, x2, y1, y2]
                        resonated = resonated + y_arr * np.float32(gain_res)

                # 低中域を中心にウェットを増やし、原音の高域PWM線は残しすぎない。
                dry_keep = np.float32(max(0.38, 1.0 - 0.18 * resonance_amount))
                wet_gain = np.float32(min(3.2, 0.82 * resonance_amount))
                body_gain = np.float32(min(1.55, 0.42 * resonance_amount))
                sig = x * dry_keep + resonated * wet_gain + body_arr * body_gain

                # 最終段でもう一度だけ耳録音風に丸める。これで「マイルドなこもり」を作る。
                post_cut = 3400.0 - 850.0 * min(1.0, resonance_amount / 3.0)
                post_cut = max(2100.0, min(3900.0, post_cut))
                alpha_post = math.exp(-TAU * post_cut / fs)
                post_arr = np.empty(frames, dtype=np.float32)
                for i in range(frames):
                    xi = float(sig[i])
                    ear_post_lp1 = alpha_post * ear_post_lp1 + (1.0 - alpha_post) * xi
                    ear_post_lp2 = alpha_post * ear_post_lp2 + (1.0 - alpha_post) * ear_post_lp1
                    post_arr[i] = np.float32(ear_post_lp2)
                post_mix = np.float32(min(0.55, 0.16 + 0.12 * resonance_amount))
                sig = sig * (np.float32(1.0) - post_mix) + post_arr * post_mix

            # v15: 通常録音に寄せた反響モード。
            # 明確な「エコー」ではなく、車内/床下/ホーム反射の短い初期反射を多く重ね、
            # 高域を減衰させながら厚みだけを増やす。反響量を上げるとON/OFF差がはっきり出る。
            if echo_enabled and echo_amount > 0.0001:
                max_echo_len = int(fs * 1.2)
                if echo_buf is None or len(echo_buf) != max_echo_len:
                    echo_buf = np.zeros(max_echo_len, dtype=np.float32)
                    echo_pos = 0
                    echo_lp = 0.0
                base_delay = max(16.0, min(220.0, echo_delay_ms))
                # 密な初期反射。符号を少し混ぜ、単一ディレイのコーン感を避ける。
                tap_ms = [0.11 * base_delay, 0.17 * base_delay, 0.24 * base_delay,
                          0.34 * base_delay, 0.47 * base_delay, 0.63 * base_delay,
                          0.82 * base_delay, 1.00 * base_delay, 1.28 * base_delay, 1.63 * base_delay]
                tap_gain = [0.56, 0.43, -0.34, 0.30, -0.24, 0.21, 0.17, -0.14, 0.10, -0.07]
                delays = [max(1, min(max_echo_len - 1, int(fs * ms / 1000.0))) for ms in tap_ms]
                wet = np.float32(min(1.70, 0.58 * echo_amount))
                fb = np.float32(min(0.38, 0.11 * echo_amount))
                y = np.empty(frames, dtype=np.float32)
                for i in range(frames):
                    d = 0.0
                    for di, gi in zip(delays, tap_gain):
                        d += gi * float(echo_buf[(echo_pos - di) % max_echo_len])
                    # 反射音は高域を丸める。耳録音の「こもった残響」に寄せる。
                    echo_lp = 0.90 * echo_lp + 0.10 * d
                    damped = 0.62 * echo_lp + 0.38 * d
                    inp = float(sig[i])
                    y[i] = np.float32(inp * max(0.58, 1.0 - 0.09 * echo_amount) + wet * damped)
                    echo_buf[echo_pos] = np.float32(inp + fb * echo_lp)
                    echo_pos = (echo_pos + 1) % max_echo_len
                sig = y

            # ノイズ/転動音は共鳴フィルタ・反響処理の後で混ぜる。
            # これによりON/OFF時もインバータ音だけが変わり、走行ノイズは自然な単独音のまま残る。
            sig = sig + acoustic_noise

            sig = np.tanh(sig * np.float32(0.82))
            sig = sig * np.float32(volume * 0.45)
            outdata[:, 0] = sig.astype(np.float32, copy=False)

        except Exception as e:
            try:
                outdata[:] = 0
                status_q.put_nowait({"type": "error", "message": f"音声生成エラー: {e}"})
            except Exception:
                pass

    try:
        device = params.get("device", None)
        if device in ("", "default", "既定"):
            device = None

        status_q.put({"type": "info", "message": "音声プロセスを開始しました"})
        with sd.OutputStream(
            samplerate=fs,
            channels=1,
            dtype="float32",
            blocksize=blocksize,
            latency="high",
            callback=callback,
            device=device,
        ):
            status_q.put({"type": "info", "message": "音声出力を開始しました"})
            while running:
                time.sleep(0.01)
                drain_commands()
    except Exception as e:
        try:
            status_q.put({"type": "error", "message": f"音声ストリーム開始失敗: {e}"})
        except Exception:
            pass
    finally:
        try:
            status_q.put({"type": "info", "message": "音声プロセスを終了しました"})
        except Exception:
            pass


# ============================================================
# GUI側
# ============================================================
class VVVFHexApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("VVVF PWM Pattern Sound GUI")
        self.root.geometry("540x900")
        self.root.minsize(520, 620)

        self.font_ui = ("Yu Gothic UI", 10)
        self.font_small = ("Yu Gothic UI", 9)
        self.font_bold = ("Yu Gothic UI", 11, "bold")
        self.font_big = ("Yu Gothic UI", 18, "bold")
        self.font_meter = ("Yu Gothic UI", 28, "bold")
        # v71: Canvas上の日本語が太く潰れないよう、表示画面では細めのフォントを使う。
        self.font_canvas_title = ("Meiryo UI", 16)
        self.font_canvas_subtitle = ("Meiryo UI", 9)
        self.font_canvas_label = ("Meiryo UI", 10)
        self.font_canvas_small = ("Meiryo UI", 8)
        self.font_canvas_big = ("Meiryo UI", 18)

        # 運転状態
        self.speed_kmh = 0.0
        self.current_accel_kmhps = 0.0
        self.elec_phase = 0.0
        self.notch = 0
        self.prev_notch = 0
        self.transition_async_until = 0.0
        self.transition_async_start = 0.0
        self.transition_async_duration = 0.0
        self.transition_ramp_dir = "none"
        self.transition_async_source = ""
        self.transition_note = ""
        self.last_update = time.perf_counter()
        self.last_param_send = 0.0
        # v49: 重い描画計算を毎フレーム実行しないためのキャッシュ。
        # 音声・走行計算は従来通り更新し、ベクトル軌跡/オシロだけを間引く。
        self._trace_cache_key = None
        self._trace_cache_value = None
        self._trace_cache_time = 0.0
        self._wave_cache_key = None
        self._wave_cache_value = None
        self._wave_cache_time = 0.0
        self.audio_proc = None
        self.cmd_q = None
        self.status_q = None
        # v66: 設定画面とは別に表示専用ウィンドウを持つ。
        self.display_window = None
        self.display_canvas = None
        self.display_fullscreen = False
        # v67: 他アプリが前面でも操作できるグローバルキー用。
        self.global_hotkey_module = None
        self.global_hotkey_enabled = False
        self._last_global_key_time = 0.0
        self._last_global_action = ""
        # v69: TkイベントとWindows APIポーリングが同時に反応しても1ノッチだけにする。
        self._key_debounce_sec = 0.18
        # v71: ローカルキー操作の押下状態。KeyPress自動リピートと二重bindを防ぐ。
        self._notch_key_down = {"up": False, "down": False, "space": False}
        self._notch_last_action_time = 0.0
        self._notch_key_debounce_sec = 0.16
        # v68: WindowsのGetAsyncKeyStateポーリング用。フォーカスが他アプリへ移っても動く。
        self._global_poll_backend = None
        self._global_poll_prev = {"up": False, "down": False, "space": False}
        self._global_poll_running = False
        # v93: Nuitka exe化時のWinError 193対策で、音声はmultiprocessingではなくthreadingを使う。
        self.ctx = None
        self.status_text = tk.StringVar(value="準備完了。音声は内部スレッドで起動します。")
        self.active_pattern_text = tk.StringVar(value="PWMパターン: 未適用")

        # GUI変数
        self.manual_mode_var = tk.StringVar(value="非同期PWM")
        self.pattern_auto_var = tk.BooleanVar(value=True)
        self.volume_var = tk.DoubleVar(value=35.0)
        self.carrier_var = tk.DoubleVar(value=1200.0)
        self.sync_pulses_var = tk.IntVar(value=21)
        self.roughness_var = tk.DoubleVar(value=30.0)
        self.load_var = tk.DoubleVar(value=55.0)
        self.maxspeed_var = tk.DoubleVar(value=130.0)
        self.maxf0_var = tk.DoubleVar(value=120.0)
        # 最高速度と最高基本波は別設定。さらに、最高基本波に到達する速度も独立させる。
        self.freq_fullspeed_var = tk.DoubleVar(value=130.0)
        self.accel_var = tk.DoubleVar(value=3.0)
        self.brake_var = tk.DoubleVar(value=4.2)
        self.modmax_var = tk.DoubleVar(value=100.0)
        self.start_voltage_var = tk.DoubleVar(value=3.0)
        self.voltage100_var = tk.DoubleVar(value=1500.0)
        # v18: 電圧指令によるPWM音量の下限/上限。
        # 例: 15/120なら、電圧0%時は15%、電圧100%時は120%の音量係数になる。
        self.voltage_gain_0_var = tk.DoubleVar(value=15.0)
        self.voltage_gain_100_var = tk.DoubleVar(value=120.0)
        # v19: PWMオシロ波形の横軸は電気角ではなく、固定時間幅で表示する。
        self.scope_window_ms_var = tk.DoubleVar(value=50.0)
        self.power_scale_var = tk.DoubleVar(value=220.0)
        self.hf_mode_var = tk.StringVar(value="正弦重畳")
        self.hf_amount_var = tk.DoubleVar(value=6.0)
        self.hf_freq_var = tk.DoubleVar(value=750.0)
        self.spread_mode_var = tk.StringVar(value="SW周波数ランダム拡散")
        self.spread_amount_var = tk.DoubleVar(value=3.0)
        self.spread_rate_var = tk.DoubleVar(value=3.5)
        self.transition_async_time_var = tk.DoubleVar(value=0.65)
        self.wind_noise_var = tk.BooleanVar(value=True)
        self.wind_amount_var = tk.DoubleVar(value=45.0)
        self.rolling_noise_var = tk.BooleanVar(value=True)
        self.rolling_amount_var = tk.DoubleVar(value=38.0)
        # v10: 通常録音に近い自然な耳補正をデフォルトONにする。
        self.resonance_filter_var = tk.BooleanVar(value=True)
        self.resonance_amount_var = tk.DoubleVar(value=170.0)
        self.resonance_shift_var = tk.DoubleVar(value=1.00)
        self.echo_mode_var = tk.BooleanVar(value=True)
        self.echo_amount_var = tk.DoubleVar(value=125.0)
        self.echo_delay_var = tk.DoubleVar(value=72.0)

        self.pattern_rows = []
        self.pattern_rows_power = []
        self.pattern_rows_brake = []
        self.pattern_table_mode_var = tk.StringVar(value="加速")
        self._last_pattern_table_key = "power"
        # v92: パターンテーブルの保存先はホームフォルダではなく、py/exeファイルと同じディレクトリ。
        self.user_preset_file = os.path.join(self.app_base_dir(), "vvvf_pwm_pattern_presets.json")
        self.user_presets = {}
        self.load_user_presets_from_file()
        self.pattern_preset_var = tk.StringVar(value=next(iter(PATTERN_PRESETS)))
        self.save_preset_name_var = tk.StringVar(value="ユーザー: カスタム")
        self.row_vmax_var = tk.StringVar(value="25")
        self.row_kind_var = tk.StringVar(value="同期PWM")
        self.row_value_var = tk.StringVar(value="45")
        self.row_name_var = tk.StringVar(value="同期45")
        self.row_hf_mode_var = tk.StringVar(value="正弦重畳")
        self.row_hf_amount_var = tk.StringVar(value="5")
        self.row_hf_freq_var = tk.StringVar(value="750")
        self.row_spread_mode_var = tk.StringVar(value="SW周波数三角拡散")
        self.row_spread_amount_var = tk.StringVar(value="3")
        self.row_spread_rate_var = tk.StringVar(value="3.5")
        self.selected_pattern_iid = None

        self._build_ui()
        self.load_pattern_preset(show_message=False)
        # v89: 起動時にpyファイルと同じディレクトリの現在設定・パルステーブルを自動読込。
        self.load_current_settings_from_script_dir(show_message=False, startup=True)
        self._bind_keys()
        self.root.protocol("WM_DELETE_WINDOW", self.on_close)
        self.root.after(30, self.tick)
        # v66: 表示画面は別ウィンドウとして自動で開く。
        self.root.after(180, self.open_display_window)
        # v70: 他アプリ使用中のグローバルキー操作は廃止。
        # キー操作はこのアプリ/表示画面がアクティブな時だけ有効にする。
        # v62: 音声はデフォルトで最初からONにする。
        # GUI初期化完了後に少し遅らせて開始し、起動直後のTk処理と衝突しにくくする。
        self.root.after(450, self.start_audio)

    # -------------------- UI構築 --------------------
    def _build_ui(self):
        style = ttk.Style()
        try:
            style.theme_use("clam")
        except Exception:
            pass

        # v71: 設定画面をコンパクトで暗めのカード風UIにする。
        self.ui_bg = "#0b0f16"
        self.ui_panel = "#131a26"
        self.ui_panel2 = "#1b2433"
        self.ui_panel3 = "#223047"
        self.ui_fg = "#f2f6ff"
        self.ui_muted = "#b7c4d8"
        self.ui_dim = "#8292aa"
        self.ui_accent = "#4da3ff"
        self.ui_accent2 = "#ffb04a"
        self.ui_line = "#3b4b63"

        try:
            self.root.configure(bg=self.ui_bg)
            self.root.geometry("540x900")
            self.root.minsize(520, 620)
            self.root.resizable(False, True)
        except Exception:
            pass

        style.configure(".", background=self.ui_bg, foreground=self.ui_fg, fieldbackground=self.ui_panel2, font=self.font_ui)
        style.configure("TFrame", background=self.ui_bg)
        style.configure("Card.TFrame", background=self.ui_panel)
        style.configure("TLabel", background=self.ui_bg, foreground=self.ui_fg, font=self.font_ui)
        style.configure("Muted.TLabel", background=self.ui_bg, foreground=self.ui_muted, font=self.font_small)

        style.configure("TButton", background=self.ui_panel3, foreground=self.ui_fg, font=self.font_ui, padding=6, borderwidth=1, focusthickness=1, focuscolor=self.ui_accent)
        style.map("TButton",
                  background=[("pressed", "#31537c"), ("active", "#2a3b55"), ("disabled", "#252b35")],
                  foreground=[("disabled", "#778399"), ("active", "#ffffff")])
        style.configure("Accent.TButton", background="#1f5fa8", foreground="#ffffff", font=self.font_ui, padding=7, borderwidth=1)
        style.map("Accent.TButton", background=[("pressed", "#174a82"), ("active", "#2f7ad0")], foreground=[("active", "#ffffff")])

        style.configure("TEntry", fieldbackground="#0f1520", foreground=self.ui_fg, insertcolor="#ffffff", bordercolor=self.ui_line, lightcolor=self.ui_line, darkcolor=self.ui_line)
        style.map("TEntry", fieldbackground=[("focus", "#121c2b")], foreground=[("disabled", "#7c889a")])
        style.configure("TCombobox", fieldbackground="#0f1520", background=self.ui_panel3, foreground=self.ui_fg, arrowcolor=self.ui_fg, bordercolor=self.ui_line, lightcolor=self.ui_line, darkcolor=self.ui_line, font=self.font_ui)
        style.map("TCombobox", fieldbackground=[("readonly", "#0f1520"), ("focus", "#121c2b")], foreground=[("readonly", self.ui_fg)], background=[("active", "#2a3b55")])

        style.configure("TLabelframe", background=self.ui_bg, foreground=self.ui_fg, bordercolor=self.ui_line, lightcolor=self.ui_line, darkcolor=self.ui_line, relief="solid")
        style.configure("TLabelframe.Label", background=self.ui_bg, foreground="#ffffff", font=("Yu Gothic UI", 11, "bold"))
        style.configure("TCheckbutton", background=self.ui_bg, foreground=self.ui_fg, font=self.font_ui, focuscolor=self.ui_accent)
        style.map("TCheckbutton", background=[("active", self.ui_bg)], foreground=[("disabled", "#7c889a"), ("active", "#ffffff")])
        style.configure("Horizontal.TScale", background=self.ui_bg, troughcolor="#263246", bordercolor=self.ui_line, lightcolor=self.ui_line, darkcolor=self.ui_line)

        # v72: 表が白背景になって読めない問題を修正。
        style.configure("Treeview",
                        background="#0f1520",
                        fieldbackground="#0f1520",
                        foreground="#eaf1ff",
                        rowheight=24,
                        bordercolor=self.ui_line,
                        lightcolor=self.ui_line,
                        darkcolor=self.ui_line,
                        font=("Yu Gothic UI", 9))
        style.configure("Treeview.Heading",
                        background="#23314a",
                        foreground="#ffffff",
                        relief="flat",
                        bordercolor=self.ui_line,
                        font=("Yu Gothic UI", 9, "bold"))
        style.map("Treeview",
                  background=[("selected", "#1f5fa8")],
                  foreground=[("selected", "#ffffff")])
        style.map("Treeview.Heading", background=[("active", "#2f4567")])
        style.configure("Vertical.TScrollbar", background=self.ui_panel3, troughcolor=self.ui_bg, arrowcolor=self.ui_fg, bordercolor=self.ui_line)

        main = ttk.Frame(self.root, padding=8)
        main.pack(fill="both", expand=True)

        # 左側は設定項目が多いのでスクロール可能にする
        left_outer = ttk.Frame(main, width=520)
        left_outer.pack(side="left", fill="both", expand=True)
        left_outer.pack_propagate(False)

        left_canvas = tk.Canvas(left_outer, width=505, highlightthickness=0, bg=self.ui_bg, bd=0)
        left_scroll = ttk.Scrollbar(left_outer, orient="vertical", command=left_canvas.yview)
        left_canvas.configure(yscrollcommand=left_scroll.set)
        left_scroll.pack(side="right", fill="y")
        left_canvas.pack(side="left", fill="both", expand=True)

        left = ttk.Frame(left_canvas)
        left_window = left_canvas.create_window((0, 0), window=left, anchor="nw")

        def _sync_scroll_region(_event=None):
            left_canvas.configure(scrollregion=left_canvas.bbox("all"))
            left_canvas.itemconfigure(left_window, width=left_canvas.winfo_width())

        left.bind("<Configure>", _sync_scroll_region)
        left_canvas.bind("<Configure>", lambda e: left_canvas.itemconfigure(left_window, width=e.width))

        def _mousewheel(event):
            try:
                left_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except Exception:
                pass

        left_canvas.bind_all("<MouseWheel>", _mousewheel)

        # v67: 設定画面には表示プレビューを出さず、設定専用にする。
        # 表示は別ウィンドウ(display_window)だけで行う。
        right = None
        try:
            self.root.geometry("540x900")
        except Exception:
            pass

        header = tk.Frame(left, bg="#111b2b", highlightbackground="#3f5f8c", highlightthickness=1)
        header.pack(fill="x", pady=(0, 10), padx=1)
        tk.Frame(header, bg="#4da3ff", height=3).pack(fill="x")
        tk.Label(header, text="VVVF モータ音シミュレータ", bg="#111b2b", fg="#ffffff",
                 font=("Yu Gothic UI", 18, "bold"), anchor="w").pack(fill="x", padx=12, pady=(9, 0))
        # バージョン表記は表示しない。

        # 基本操作
        # v91: 音START/STOP/緊急STOPは非表示。音声は従来通り起動時に自動開始する。
        audio_box = ttk.LabelFrame(left, text="基本操作")
        audio_box.pack(fill="x", pady=4)
        settings_row = ttk.Frame(audio_box)
        settings_row.pack(fill="x", padx=8, pady=(7, 7))
        ttk.Button(settings_row, text="現在設定を保存", command=self.save_current_settings_to_script_dir).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(settings_row, text="現在設定を読込", command=self.load_current_settings_from_script_dir).pack(side="left", fill="x", expand=True, padx=(3, 0))
        display_row = ttk.Frame(audio_box)
        display_row.pack(fill="x", padx=8, pady=(0, 7))
        ttk.Button(display_row, text="表示画面を開く", command=self.open_display_window).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(display_row, text="表示フルスクリーン", command=self.toggle_display_fullscreen, style="Accent.TButton").pack(side="left", fill="x", expand=True, padx=(3, 0))

        # マスコン
        master_box = ttk.LabelFrame(left, text="マスコン")
        master_box.pack(fill="x", pady=4)
        self.notch_label = ttk.Label(master_box, text="N", font=("Yu Gothic UI", 30, "bold"), anchor="center")
        self.notch_label.pack(fill="x", padx=8, pady=(4, 0))
        btns = ttk.Frame(master_box)
        btns.pack(fill="x", padx=8, pady=5)
        ttk.Button(btns, text="B↑", command=self.brake_up).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btns, text="N", command=self.neutral).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Button(btns, text="P↓", command=self.power_down).pack(side="left", fill="x", expand=True, padx=2)
        ttk.Label(master_box, text="キー操作: ↑=ブレーキ側  ↓=力行側  Space=中立（アクティブ時）", font=self.font_small, foreground=self.ui_muted).pack(anchor="w", padx=8, pady=(0, 5))

        # PWMパターン
        pattern_box = ttk.LabelFrame(left, text="PWMパターン選択・編集")
        pattern_box.pack(fill="x", pady=4)
        # v90: 手動PWM設定を廃止し、常に速度域パターンテーブルを使う。
        self.pattern_auto_var.set(True)
        ttk.Label(pattern_box, text="速度域パターンテーブルを常に使用", font=self.font_small, foreground=self.ui_muted).pack(anchor="w", padx=8, pady=(6, 2))

        table_row = ttk.Frame(pattern_box)
        table_row.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Label(table_row, text="編集テーブル", font=self.font_small).pack(side="left")
        self.pattern_table_combo = ttk.Combobox(
            table_row, values=["加速", "減速"], textvariable=self.pattern_table_mode_var, state="readonly", width=8
        )
        self.pattern_table_combo.pack(side="left", padx=(6, 4))
        self.pattern_table_combo.bind("<<ComboboxSelected>>", self.switch_pattern_table)
        ttk.Button(table_row, text="加速→減速へコピー", command=self.copy_power_pattern_to_brake).pack(side="left", fill="x", expand=True)

        preset_row = ttk.Frame(pattern_box)
        preset_row.pack(fill="x", padx=8, pady=(2, 4))
        ttk.Label(preset_row, text="プリセット", font=self.font_small).pack(side="left")
        self.pattern_preset_combo = ttk.Combobox(
            preset_row,
            values=list(PATTERN_PRESETS.keys()),
            textvariable=self.pattern_preset_var,
            state="readonly",
            width=28,
        )
        self.pattern_preset_combo.pack(side="left", fill="x", expand=True, padx=(6, 4))
        self.pattern_preset_combo.bind("<<ComboboxSelected>>", self.on_pattern_preset_selected)
        ttk.Button(preset_row, text="読込", command=self.load_selected_pattern_preset).pack(side="left")

        save_row = ttk.Frame(pattern_box)
        save_row.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Label(save_row, text="保存名", font=self.font_small).pack(side="left")
        ttk.Entry(save_row, textvariable=self.save_preset_name_var, width=20).pack(side="left", fill="x", expand=True, padx=(6, 4))
        ttk.Button(save_row, text="現在を保存", command=self.save_current_pattern_preset).pack(side="left", padx=(0, 4))
        ttk.Button(save_row, text="削除", command=self.delete_user_pattern_preset).pack(side="left")

        io_row = ttk.Frame(pattern_box)
        io_row.pack(fill="x", padx=8, pady=(0, 4))
        ttk.Button(io_row, text="テーブルをインポート", command=self.import_pattern_tables).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(io_row, text="テーブルをエクスポート", command=self.export_pattern_tables).pack(side="left", fill="x", expand=True, padx=(3, 0))

        self.pattern_tree = ttk.Treeview(
            pattern_box,
            columns=("vmax", "kind", "value", "hf", "spread"),
            show="tree headings",
            height=6,
            selectmode="browse",
        )
        self.pattern_tree.heading("#0", text="名前")
        self.pattern_tree.heading("vmax", text="上限")
        self.pattern_tree.heading("kind", text="方式")
        self.pattern_tree.heading("value", text="値")
        self.pattern_tree.heading("hf", text="重畳")
        self.pattern_tree.heading("spread", text="拡散")
        self.pattern_tree.column("#0", width=94, minwidth=80, stretch=True)
        self.pattern_tree.column("vmax", width=45, anchor="e", stretch=False)
        self.pattern_tree.column("kind", width=72, stretch=False)
        self.pattern_tree.column("value", width=62, anchor="e", stretch=False)
        self.pattern_tree.column("hf", width=70, stretch=False)
        self.pattern_tree.column("spread", width=70, stretch=False)
        self.pattern_tree.pack(fill="x", padx=8, pady=(2, 4))
        self.pattern_tree.bind("<<TreeviewSelect>>", self.on_pattern_tree_select)

        edit = ttk.LabelFrame(pattern_box, text="行の編集 / 新規追加")
        edit.pack(fill="x", padx=8, pady=(2, 6))
        grid = ttk.Frame(edit)
        grid.pack(fill="x", padx=6, pady=5)
        ttk.Label(grid, text="上限km/h", font=self.font_small).grid(row=0, column=0, sticky="w")
        ttk.Entry(grid, textvariable=self.row_vmax_var, width=8).grid(row=1, column=0, sticky="ew", padx=(0, 4))
        ttk.Label(grid, text="方式", font=self.font_small).grid(row=0, column=1, sticky="w")
        ttk.Combobox(
            grid,
            values=[MODE_LABELS[k] for k in ("ASYNC", "SYNC", "SHE", "CHM", "WIDE3", "ONEPULSE")],
            textvariable=self.row_kind_var,
            state="readonly",
            width=10,
        ).grid(row=1, column=1, sticky="ew", padx=(0, 4))
        ttk.Label(grid, text="値", font=self.font_small).grid(row=0, column=2, sticky="w")
        ttk.Entry(grid, textvariable=self.row_value_var, width=10).grid(row=1, column=2, sticky="ew", padx=(0, 4))
        ttk.Label(grid, text="名前", font=self.font_small).grid(row=0, column=3, sticky="w")
        ttk.Entry(grid, textvariable=self.row_name_var, width=15).grid(row=1, column=3, sticky="ew")
        grid.columnconfigure(3, weight=1)

        grid2 = ttk.Frame(edit)
        grid2.pack(fill="x", padx=6, pady=(0, 5))
        ttk.Label(grid2, text="高周波", font=self.font_small).grid(row=0, column=0, sticky="w")
        ttk.Combobox(grid2, values=[HF_LABELS[k] for k in ("OFF", "SINE", "TRI", "SQUARE", "CARRIER")], textvariable=self.row_hf_mode_var, state="readonly", width=10).grid(row=1, column=0, sticky="ew", padx=(0, 4))
        ttk.Label(grid2, text="量%", font=self.font_small).grid(row=0, column=1, sticky="w")
        ttk.Entry(grid2, textvariable=self.row_hf_amount_var, width=6).grid(row=1, column=1, sticky="ew", padx=(0, 4))
        ttk.Label(grid2, text="重畳Hz", font=self.font_small).grid(row=0, column=2, sticky="w")
        ttk.Entry(grid2, textvariable=self.row_hf_freq_var, width=7).grid(row=1, column=2, sticky="ew", padx=(0, 4))
        ttk.Label(grid2, text="拡散", font=self.font_small).grid(row=2, column=0, sticky="w", pady=(4, 0))
        ttk.Combobox(grid2, values=[SPREAD_LABELS[k] for k in ("OFF", "SINE", "TRI", "RANDOM", "STEP")], textvariable=self.row_spread_mode_var, state="readonly", width=10).grid(row=3, column=0, sticky="ew", padx=(0, 4))
        ttk.Label(grid2, text="量%", font=self.font_small).grid(row=2, column=1, sticky="w", pady=(4, 0))
        ttk.Entry(grid2, textvariable=self.row_spread_amount_var, width=6).grid(row=3, column=1, sticky="ew", padx=(0, 4))
        ttk.Label(grid2, text="拡散Hz", font=self.font_small).grid(row=2, column=2, sticky="w", pady=(4, 0))
        ttk.Entry(grid2, textvariable=self.row_spread_rate_var, width=7).grid(row=3, column=2, sticky="ew")
        grid2.columnconfigure(0, weight=1)

        rowp = ttk.Frame(pattern_box)
        rowp.pack(fill="x", padx=8, pady=(0, 3))
        ttk.Button(rowp, text="追加", command=self.add_pattern_row).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(rowp, text="選択行を更新", command=self.update_selected_pattern_row).pack(side="left", fill="x", expand=True, padx=3)
        ttk.Button(rowp, text="削除", command=self.delete_selected_pattern_row).pack(side="left", fill="x", expand=True, padx=(3, 0))

        rowp2 = ttk.Frame(pattern_box)
        rowp2.pack(fill="x", padx=8, pady=(0, 6))
        ttk.Button(rowp2, text="上へ", command=lambda: self.move_selected_pattern_row(-1)).pack(side="left", fill="x", expand=True, padx=(0, 3))
        ttk.Button(rowp2, text="下へ", command=lambda: self.move_selected_pattern_row(1)).pack(side="left", fill="x", expand=True, padx=(3, 0))
        ttk.Label(pattern_box, textvariable=self.active_pattern_text, wraplength=370, font=self.font_small).pack(fill="x", padx=8, pady=(0, 6))

        # v90: 手動PWM設定は廃止。パターン動作用の電圧・表示設定だけ残す。
        voltage_box = ttk.LabelFrame(left, text="電圧・表示設定（パターン用）")
        voltage_box.pack(fill="x", pady=4)
        self._slider(voltage_box, "最大変調率 [%]", self.modmax_var, 20, 100, 1)
        self._slider(voltage_box, "起動電圧 [%]", self.start_voltage_var, 0, 5, 0.1)
        self._slider(voltage_box, "変調率100%の相間電圧 [V]", self.voltage100_var, 100, 2500, 10)
        self._slider(voltage_box, "PWMオシロ時間軸 [ms]", self.scope_window_ms_var, 5, 200, 1)

        # 音色
        tone_box = ttk.LabelFrame(left, text="音・負荷")
        tone_box.pack(fill="x", pady=4)
        self._slider(tone_box, "音量 [%]", self.volume_var, 0, 100, 1)
        self._slider(tone_box, "電圧0%時 PWM音量 [%]", self.voltage_gain_0_var, 0, 300, 1)
        self._slider(tone_box, "電圧100%時 PWM音量 [%]", self.voltage_gain_100_var, 0, 300, 1)
        self._slider(tone_box, "音の荒さ [%]", self.roughness_var, 0, 100, 1)
        self._slider(tone_box, "負荷率 [%]", self.load_var, 0, 120, 1)
        ttk.Checkbutton(tone_box, text="走行音ノイズを混ぜる（Nでも速度があれば鳴る）", variable=self.wind_noise_var).pack(anchor="w", padx=8, pady=(4, 0))
        self._slider(tone_box, "走行音ノイズ量 [%]", self.wind_amount_var, 0, 150, 1)
        ttk.Checkbutton(tone_box, text="転動音を混ぜる（車輪・軌道音）", variable=self.rolling_noise_var).pack(anchor="w", padx=8, pady=(4, 0))
        self._slider(tone_box, "転動音量 [%]", self.rolling_amount_var, 0, 150, 1)

        ear_box = ttk.LabelFrame(left, text="耳で聞く励磁音補正")
        ear_box.pack(fill="x", pady=4)
        ttk.Checkbutton(ear_box, text="共鳴フィルタを使う", variable=self.resonance_filter_var).pack(anchor="w", padx=8, pady=(6, 0))
        self._slider(ear_box, "共鳴量 [%]", self.resonance_amount_var, 0, 500, 1)
        self._slider(ear_box, "共鳴周波数倍率", self.resonance_shift_var, 0.6, 1.6, 0.05)
        ttk.Checkbutton(ear_box, text="反響モードを使う", variable=self.echo_mode_var).pack(anchor="w", padx=8, pady=(6, 0))
        self._slider(ear_box, "反響量 [%]", self.echo_amount_var, 0, 500, 1)
        self._slider(ear_box, "反響長さ [ms]", self.echo_delay_var, 10, 220, 1)
        ttk.Label(ear_box, text="v15: 通常録音を基準に再解析。共鳴ONでPWM成分を丸め、低中域の車体鳴りと短い反響を強めます。ノイズ/転動音には掛けません。", font=self.font_small, wraplength=370).pack(anchor="w", padx=8, pady=(2, 6))

        self._slider(tone_box, "疑似パワースケール [kW]", self.power_scale_var, 10, 800, 10)

        # v91: 高周波重畳・キャリア拡散の大項目は削除。
        # パターン表の列が空の場合は内部デフォルト値を使うが、設定画面には表示しない。

        # 走行モデル
        run_box = ttk.LabelFrame(left, text="走行モデル")
        run_box.pack(fill="x", pady=4)
        self._slider(run_box, "最高速度 [km/h]（速度計/走行用）", self.maxspeed_var, 20, 220, 1)
        self._slider(run_box, "基準基本周波数 [Hz]（到達速度時）", self.maxf0_var, 20, 220, 1)
        self._slider(run_box, "基準周波数到達速度 [km/h]", self.freq_fullspeed_var, 20, 220, 1)
        ttk.Label(run_box, text="指定速度で基準基本周波数に達します。その速度を超えても基本波は速度比例で上がり続けます。電圧は基準速度以降で頭打ちです。", font=self.font_small, wraplength=370).pack(anchor="w", padx=8, pady=(0, 4))
        self._slider(run_box, "加速度倍率", self.accel_var, 0.2, 8.0, 0.1)
        self._slider(run_box, "ブレーキ倍率", self.brake_var, 0.2, 10.0, 0.1)

        # ステータス
        status = ttk.LabelFrame(left, text="状態")
        status.pack(fill="x", pady=4)
        self.state_label = ttk.Label(status, textvariable=self.status_text, wraplength=370)
        self.state_label.pack(fill="x", padx=8, pady=8)

        # v67: 設定画面内の描画Canvasは廃止。
        self.canvas = None

    # -------------------- 表示画面ウィンドウ --------------------
    def open_display_window(self):
        """設定画面とは別の表示専用ウィンドウを開く。"""
        try:
            if self.display_window is not None and self.display_window.winfo_exists():
                self.display_window.lift()
                return
        except Exception:
            self.display_window = None
            self.display_canvas = None

        win = tk.Toplevel(self.root)
        win.title("VVVF 表示画面")
        win.geometry("1280x720")
        win.configure(bg="#0f1218")
        try:
            win.minsize(960, 540)
        except Exception:
            pass
        self.display_window = win
        self.display_fullscreen = False

        # F11で全画面、Escで全画面解除。表示画面側でも上下/Spaceを受ける。
        # v90: イベントを必ずbreakし、Canvas側にも同じキーをbindして取りこぼしを減らす。
        win.bind("<F11>", self._display_fullscreen_event)
        win.bind("<Escape>", self._display_fullscreen_off_event)
        win.bind("<KeyPress-Up>", lambda e: self.handle_notch_key_press("up"))
        win.bind("<KeyPress-Down>", lambda e: self.handle_notch_key_press("down"))
        win.bind("<KeyPress-space>", lambda e: self.handle_notch_key_press("space"))
        win.bind("<KeyRelease-Up>", lambda e: self.handle_notch_key_release("up"))
        win.bind("<KeyRelease-Down>", lambda e: self.handle_notch_key_release("down"))
        win.bind("<KeyRelease-space>", lambda e: self.handle_notch_key_release("space"))
        win.protocol("WM_DELETE_WINDOW", self.close_display_window)

        self.display_canvas = tk.Canvas(win, bg="#0f1218", highlightthickness=0)
        self.display_canvas.pack(fill="both", expand=True)
        self.display_canvas.bind("<F11>", self._display_fullscreen_event)
        self.display_canvas.bind("<Escape>", self._display_fullscreen_off_event)
        try:
            self.display_canvas.focus_set()
        except Exception:
            pass

        self.status_text.set("表示画面を開きました。F11でフルスクリーン、Escで解除できます。")

    def close_display_window(self):
        try:
            if self.display_window is not None and self.display_window.winfo_exists():
                self.display_window.destroy()
        except Exception:
            pass
        self.display_window = None
        self.display_canvas = None
        self.display_fullscreen = False

    def _display_fullscreen_event(self, event=None):
        self.toggle_display_fullscreen()
        return "break"

    def _display_fullscreen_off_event(self, event=None):
        self.set_display_fullscreen(False)
        return "break"

    def set_display_fullscreen(self, enable: bool):
        if self.display_window is None or not self.display_window.winfo_exists():
            self.open_display_window()
        try:
            win = self.display_window
            self.display_fullscreen = bool(enable)
            win.deiconify()
            win.lift()
            try:
                win.focus_force()
            except Exception:
                pass

            if self.display_fullscreen:
                # v90:
                # Windows/TkでF11が効かない場合があったため、zoomedとfullscreenを混在させず、
                # fullscreen属性 + 画面サイズgeometry + 遅延再適用で安定させる。
                try:
                    win.state("normal")
                except Exception:
                    pass
                try:
                    sw = win.winfo_screenwidth()
                    sh = win.winfo_screenheight()
                    win.geometry(f"{sw}x{sh}+0+0")
                except Exception:
                    pass
                try:
                    win.attributes("-topmost", True)
                except Exception:
                    pass
                win.attributes("-fullscreen", True)
                try:
                    win.update_idletasks()
                except Exception:
                    pass
                self.root.after(80, lambda: self._apply_fullscreen_again(True))
                self.root.after(240, lambda: self._apply_fullscreen_again(True))
                self.root.after(500, lambda: self._clear_display_topmost())
                self.status_text.set("表示画面をフルスクリーンにしました。Escで解除できます。")
            else:
                win.attributes("-fullscreen", False)
                try:
                    win.attributes("-topmost", False)
                except Exception:
                    pass
                try:
                    win.state("normal")
                    win.geometry("1280x720")
                except Exception:
                    pass
                self.root.after(80, lambda: self._apply_fullscreen_again(False))
                self.status_text.set("表示画面のフルスクリーンを解除しました。")
        except Exception as e:
            self.status_text.set(f"表示画面フルスクリーン切替エラー: {e}")

    def _clear_display_topmost(self):
        try:
            if self.display_window is not None and self.display_window.winfo_exists():
                # fullscreen維持中でも最前面固定は解除する。別アプリを使いたい場合の邪魔を減らす。
                self.display_window.attributes("-topmost", False)
        except Exception:
            pass

    def _apply_fullscreen_again(self, enable: bool):
        try:
            if self.display_window is not None and self.display_window.winfo_exists():
                win = self.display_window
                if enable:
                    try:
                        sw = win.winfo_screenwidth()
                        sh = win.winfo_screenheight()
                        win.geometry(f"{sw}x{sh}+0+0")
                    except Exception:
                        pass
                win.attributes("-fullscreen", bool(enable))
                if enable:
                    win.lift()
                    try:
                        win.focus_force()
                    except Exception:
                        pass
        except Exception:
            pass

    def toggle_display_fullscreen(self):
        if self.display_window is None or not self.display_window.winfo_exists():
            self.open_display_window()
        current = bool(getattr(self, "display_fullscreen", False))
        try:
            current = bool(self.display_window.attributes("-fullscreen"))
        except Exception:
            pass
        self.set_display_fullscreen(not current)


    def _slider(self, parent, text, var, lo, hi, step):
        frame = ttk.Frame(parent)
        frame.pack(fill="x", padx=8, pady=3)
        label = ttk.Label(frame, text=text, font=self.font_small)
        label.pack(anchor="w")
        row = ttk.Frame(frame)
        row.pack(fill="x")
        scale = ttk.Scale(row, from_=lo, to=hi, variable=var, orient="horizontal")
        scale.pack(side="left", fill="x", expand=True)
        value_label = ttk.Label(row, width=7, anchor="e", font=self.font_small)
        value_label.pack(side="right", padx=(6, 0))

        def update_label(*_):
            v = var.get()
            if step >= 1:
                value_label.config(text=f"{v:.0f}")
            else:
                value_label.config(text=f"{v:.1f}")
        var.trace_add("write", update_label)
        update_label()

    def handle_notch_key_press(self, key: str):
        """1回の物理キー押下で1ノッチだけ動かす。

        v71:
        TkのKeyPress自動リピートや、root/displayの二重bindでノッチが飛ぶのを防ぐ。
        """
        key = str(key)
        now = time.perf_counter()
        if self._notch_key_down.get(key, False):
            return "break"
        if now - float(getattr(self, "_notch_last_action_time", 0.0)) < float(getattr(self, "_notch_key_debounce_sec", 0.16)):
            return "break"

        self._notch_key_down[key] = True
        self._notch_last_action_time = now

        if key == "up":
            self.brake_up()
        elif key == "down":
            self.power_down()
        elif key == "space":
            self.neutral()
        return "break"

    def handle_notch_key_release(self, key: str):
        key = str(key)
        # KeyRelease直後に自動リピート由来のKeyPressが残る環境があるため少し遅らせる。
        def clear():
            self._notch_key_down[key] = False
        try:
            self.root.after(40, clear)
        except Exception:
            self._notch_key_down[key] = False
        return "break"

    def _bind_keys(self):
        # v71: グローバルキー廃止。アプリ/表示画面がアクティブな時だけ操作。
        # すべて共通ハンドラに通して、1押下=1ノッチにする。
        try:
            self.root.bind_all("<KeyPress-Up>", lambda e: self.handle_notch_key_press("up"))
            self.root.bind_all("<KeyPress-Down>", lambda e: self.handle_notch_key_press("down"))
            self.root.bind_all("<KeyPress-space>", lambda e: self.handle_notch_key_press("space"))
            self.root.bind_all("<KeyRelease-Up>", lambda e: self.handle_notch_key_release("up"))
            self.root.bind_all("<KeyRelease-Down>", lambda e: self.handle_notch_key_release("down"))
            self.root.bind_all("<KeyRelease-space>", lambda e: self.handle_notch_key_release("space"))
            self.root.bind_all("<F11>", self._display_fullscreen_event)
        except Exception:
            pass

    # -------------------- PWMパターン --------------------
    @staticmethod
    def _norm_key(s: str) -> str:
        return str(s).strip().upper().replace(" ", "").replace("_", "-").replace("－", "-")

    @staticmethod
    def normalize_mode(s: str) -> str:
        key = VVVFHexApp._norm_key(s)
        return MODE_ALIASES.get(key, MODE_ALIASES.get(key.replace("-", ""), ""))

    @staticmethod
    def normalize_hf(s: str) -> str:
        key = VVVFHexApp._norm_key(s)
        return HF_ALIASES.get(key, HF_ALIASES.get(key.replace("-", ""), "OFF"))

    @staticmethod
    def normalize_spread(s: str) -> str:
        key = VVVFHexApp._norm_key(s)
        return SPREAD_ALIASES.get(key, SPREAD_ALIASES.get(key.replace("-", ""), "OFF"))

    @staticmethod
    def parse_pattern_value(raw, value_end=None):
        """PWMパターン行の値を解析する。

        v57:
        ASYNC行では、値欄に「750-1050」「750→1050」「1050~750」などを
        入れると、速度域の下限から上限にかけてキャリア周波数を直線補間する。
        既存の数値だけの行は従来通り単一値として扱う。
        """
        if raw is None:
            raw = 0.0
        # すでにJSONなどで value_end が分離している場合。
        if value_end is not None and str(value_end).strip() != "":
            start = float(raw)
            end = float(value_end)
            text = f"{start:g}-{end:g}" if abs(start - end) > 1e-9 else f"{start:g}"
            return start, (end if abs(start - end) > 1e-9 else None), text

        if isinstance(raw, (int, float)):
            v = float(raw)
            return v, None, f"{v:g}"

        s = str(raw).strip()
        if not s:
            return 0.0, None, "0"
        ss = s.replace("Hz", "").replace("hz", "").replace("Ｈｚ", "").strip()
        ss = ss.replace("〜", "~").replace("～", "~").replace("－", "-").replace("—", "-").replace("–", "-")
        ss = ss.replace("→", ">").replace("⇒", ">")
        ss = re.sub(r"\s+to\s+", ">", ss, flags=re.IGNORECASE)
        ss = re.sub(r"\s+", "", ss)

        # 範囲指定。負数は想定しない周波数用なので、シンプルに正数範囲を読む。
        m = re.fullmatch(r"([+]?(?:\d+(?:\.\d*)?|\.\d+))(?:-|~|>|\.\.)([+]?(?:\d+(?:\.\d*)?|\.\d+))", ss)
        if m:
            start = float(m.group(1))
            end = float(m.group(2))
            return start, (end if abs(start - end) > 1e-9 else None), (f"{start:g}-{end:g}" if abs(start - end) > 1e-9 else f"{start:g}")

        v = float(ss)
        return v, None, f"{v:g}"

    @staticmethod
    def format_pattern_value(row, edit: bool = False) -> str:
        start, end, text = VVVFHexApp.parse_pattern_value(row.get("value", 0.0), row.get("value_end"))
        if end is not None:
            return f"{start:g}-{end:g}" if edit else f"{start:g}→{end:g}"
        return f"{start:g}"

    def async_value_for_speed(self, row) -> float:
        """ASYNC行のキャリアHzを現在速度で補間する。"""
        start, end, _ = self.parse_pattern_value(row.get("value", 0.0), row.get("value_end"))
        if end is None:
            return float(start)
        vmin = float(row.get("_vmin", 0.0) or 0.0)
        vmax = float(row.get("vmax", vmin + 1.0) or (vmin + 1.0))
        if vmax <= vmin + 1e-9:
            t = 1.0
        else:
            t = (self.speed_kmh - vmin) / (vmax - vmin)
        t = max(0.0, min(1.0, t))
        return float(start + (end - start) * t)

    def clone_pattern_rows(self, rows):
        cloned = []
        for r in rows:
            value, value_end, value_text = self.parse_pattern_value(r.get("value", 0.0), r.get("value_end"))
            row = {
                "vmax": float(r.get("vmax", 999.0)),
                "kind": str(r.get("kind", "ASYNC")),
                "value": float(value),
                "name": str(r.get("name", "")),
                "hf_mode": r.get("hf_mode"),
                "hf_amount": None if r.get("hf_amount") is None else float(r.get("hf_amount")),
                "hf_freq": None if r.get("hf_freq") is None else float(r.get("hf_freq")),
                "spread_mode": r.get("spread_mode"),
                "spread_amount": None if r.get("spread_amount") is None else float(r.get("spread_amount")),
                "spread_rate": None if r.get("spread_rate") is None else float(r.get("spread_rate")),
            }
            if value_end is not None:
                row["value_end"] = float(value_end)
                row["value_text"] = value_text
            cloned.append(row)
        return cloned

    def normalize_preset_payload(self, preset):
        """プリセットを加速/減速2テーブル形式に正規化する。

        旧版互換として、従来のlist形式プリセットは加速/減速の両方へ同じ内容を入れる。
        v26以降のユーザープリセットは {"power": [...], "brake": [...]} で保存する。
        """
        if isinstance(preset, dict):
            power = preset.get("power") or preset.get("accel") or preset.get("加速") or []
            brake = preset.get("brake") or preset.get("decel") or preset.get("減速") or power
            if not isinstance(power, list):
                power = []
            if not isinstance(brake, list):
                brake = power
        else:
            power = preset if isinstance(preset, list) else []
            brake = power
        power_rows = self.clone_pattern_rows(power) if power else self.clone_pattern_rows(next(iter(PATTERN_PRESETS.values())))
        brake_rows = self.clone_pattern_rows(brake) if brake else self.clone_pattern_rows(power_rows)
        return power_rows, brake_rows

    def edit_table_key(self):
        return "brake" if str(self.pattern_table_mode_var.get()).startswith("減") else "power"

    def store_current_pattern_rows_to_active_table(self):
        if not hasattr(self, "pattern_rows_power"):
            return
        # Combobox選択イベントではStringVarが先に新値へ変わるため、
        # 直前に表示していたテーブルキーを使って保存する。
        key = getattr(self, "_last_pattern_table_key", self.edit_table_key())
        if key == "brake":
            self.pattern_rows_brake = self.clone_pattern_rows(self.pattern_rows)
        else:
            self.pattern_rows_power = self.clone_pattern_rows(self.pattern_rows)

    def load_active_table_to_editor(self):
        if self.edit_table_key() == "brake":
            src = self.pattern_rows_brake or self.pattern_rows_power or self.pattern_rows
        else:
            src = self.pattern_rows_power or self.pattern_rows_brake or self.pattern_rows
        self.pattern_rows = self.clone_pattern_rows(src)
        self.refresh_pattern_tree(keep_selection=False)

    def switch_pattern_table(self, _event=None):
        # 現在表示中の編集内容を保存してから、選択された加速/減速テーブルへ切り替える。
        try:
            self.apply_pattern_table(show_message=False)
        except Exception:
            self.store_current_pattern_rows_to_active_table()
        self._last_pattern_table_key = self.edit_table_key()
        self.load_active_table_to_editor()
        self.status_text.set(f"PWMパターン編集テーブルを {self.pattern_table_mode_var.get()} に切り替えました。")

    def copy_power_pattern_to_brake(self):
        # 現在の加速テーブルを減速テーブルへ複製。加速側編集中なら先に反映する。
        try:
            self.apply_pattern_table(show_message=False)
        except Exception:
            pass
        if self.edit_table_key() == "power":
            self.pattern_rows_power = self.clone_pattern_rows(self.pattern_rows)
        self.pattern_rows_brake = self.clone_pattern_rows(self.pattern_rows_power or self.pattern_rows)
        if self.edit_table_key() == "brake":
            self.pattern_rows = self.clone_pattern_rows(self.pattern_rows_brake)
            self.refresh_pattern_tree(keep_selection=False)
        self.status_text.set("加速用PWMパターンを減速用テーブルへコピーしました。")

    def get_drive_pattern_rows(self):
        """現在の運転方向に応じたPWMパターンテーブルを返す。

        力行中は加速テーブル、ブレーキ中は減速テーブルを使う。
        Nへの遷移中は直前ノッチで判定し、遷移音も元の力行/減速テーブルに従う。
        """
        sign_src = self.notch if self.notch != 0 else self.prev_notch
        if sign_src < 0 and self.pattern_rows_brake:
            return self.pattern_rows_brake
        if sign_src >= 0 and self.pattern_rows_power:
            return self.pattern_rows_power
        return self.pattern_rows

    def row_display_values(self, row):
        hf_mode = row.get("hf_mode") or "OFF"
        sp_mode = row.get("spread_mode") or "OFF"
        hf_freq = row.get("hf_freq")
        sp_rate = row.get("spread_rate")
        hf_txt = f"{HF_LABELS.get(hf_mode, hf_mode)} {float(row.get('hf_amount') or 0):g}%"
        if hf_freq is not None:
            hf_txt += f" @{float(hf_freq):g}Hz"
        sp_txt = f"{SPREAD_LABELS.get(sp_mode, sp_mode)} {float(row.get('spread_amount') or 0):g}%"
        if sp_rate is not None:
            sp_txt += f" @{float(sp_rate):g}Hz"
        return (
            f"{float(row['vmax']):g}",
            MODE_LABELS.get(row["kind"], row["kind"]),
            self.format_pattern_value(row),
            hf_txt,
            sp_txt,
        )

    def refresh_pattern_tree(self, keep_selection=True):
        if not hasattr(self, "pattern_tree") or self.pattern_tree is None:
            return
        selected_idx = None
        if keep_selection:
            sel = self.pattern_tree.selection()
            if sel:
                try:
                    selected_idx = int(sel[0])
                except Exception:
                    selected_idx = None
        self.pattern_tree.delete(*self.pattern_tree.get_children())
        try:
            self.pattern_tree.tag_configure("odd", background="#121b2a", foreground="#eaf1ff")
            self.pattern_tree.tag_configure("even", background="#0f1520", foreground="#eaf1ff")
        except Exception:
            pass
        for idx, row in enumerate(self.pattern_rows):
            tag = "odd" if idx % 2 else "even"
            self.pattern_tree.insert("", "end", iid=str(idx), text=row.get("name", ""), values=self.row_display_values(row), tags=(tag,))
        if selected_idx is not None and 0 <= selected_idx < len(self.pattern_rows):
            try:
                self.pattern_tree.selection_set(str(selected_idx))
                self.pattern_tree.focus(str(selected_idx))
            except Exception:
                pass

    def load_user_presets_from_file(self):
        """ユーザー保存プリセットをpy/exeファイルと同じディレクトリから読み込む。"""
        self.user_presets = {}
        try:
            path = self.user_preset_file
            # v92: 旧版はホームフォルダの .vvvf_pwm_pattern_presets.json に保存していた。
            # 新しい保存先がまだ無い場合だけ、旧ファイルを読み込んで互換性を保つ。
            if not os.path.exists(path):
                old_path = os.path.join(os.path.expanduser("~"), ".vvvf_pwm_pattern_presets.json")
                if os.path.exists(old_path):
                    path = old_path
                else:
                    return
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            if isinstance(data, dict):
                for name, rows in data.items():
                    valid = (isinstance(rows, list) and rows) or (isinstance(rows, dict) and (rows.get("power") or rows.get("brake") or rows.get("accel") or rows.get("decel")))
                    if valid:
                        pname = str(name).strip() or "ユーザー: 無題"
                        if not pname.startswith("ユーザー:"):
                            pname = "ユーザー: " + pname
                        self.user_presets[pname] = rows
                        PATTERN_PRESETS[pname] = rows
        except Exception:
            # 読み込み失敗時は標準プリセットだけで起動する。
            self.user_presets = {}

    def write_user_presets_to_file(self):
        """ユーザープリセットをpy/exeファイルと同じディレクトリへ保存する。"""
        try:
            os.makedirs(os.path.dirname(self.user_preset_file), exist_ok=True)
        except Exception:
            pass
        with open(self.user_preset_file, "w", encoding="utf-8") as f:
            json.dump(self.user_presets, f, ensure_ascii=False, indent=2)

    def update_preset_combo_values(self):
        if hasattr(self, "pattern_preset_combo"):
            self.pattern_preset_combo.configure(values=list(PATTERN_PRESETS.keys()))

    def on_pattern_preset_selected(self, _event=None):
        # コンボボックスでプリセット名を変えた時点で、保存名も同じ名前へ合わせる。
        # 実データの読込は従来通り「読込」ボタンでもできるが、保存名の取り違えを防ぐ。
        name = self.pattern_preset_var.get().strip()
        if name:
            self.save_preset_name_var.set(name)

    def current_pattern_payload(self) -> dict:
        """現在の加速/減速パターンテーブルをJSON化しやすい形で返す。"""
        try:
            self.apply_pattern_table(show_message=False)
        except Exception:
            pass
        self.store_current_pattern_rows_to_active_table()
        return {
            "format": "VVVF_PWM_PATTERN_TABLES",
            "version": 2,
            "preset_name": self.save_preset_name_var.get().strip() or self.pattern_preset_var.get().strip() or "ユーザー: カスタム",
            "power": self.clone_pattern_rows(self.pattern_rows_power or self.pattern_rows),
            "brake": self.clone_pattern_rows(self.pattern_rows_brake or self.pattern_rows_power or self.pattern_rows),
        }

    def export_pattern_tables(self):
        """加速/減速2テーブルをJSONファイルへ書き出す。"""
        try:
            payload = self.current_pattern_payload()
            safe_name = (payload.get("preset_name") or "vvvf_pattern").replace("/", "_").replace("\\", "_").replace(":", "_")
            path = filedialog.asksaveasfilename(
                title="PWMパターンテーブルをエクスポート",
                defaultextension=".json",
                initialdir=self.app_base_dir(),
                initialfile=f"{safe_name}.json",
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not path:
                return
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self.status_text.set(f"PWMパターンテーブルをエクスポートしました: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("エクスポートエラー", str(e))

    def import_pattern_tables(self):
        """JSONファイルから加速/減速2テーブルを読み込む。"""
        try:
            path = filedialog.askopenfilename(
                title="PWMパターンテーブルをインポート",
                initialdir=self.app_base_dir(),
                filetypes=[("JSON files", "*.json"), ("All files", "*.*")],
            )
            if not path:
                return
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)

            # v28形式 {power, brake}、旧形式 list、または {pattern_tables:{power,brake}} を許容する。
            if isinstance(data, dict) and isinstance(data.get("pattern_tables"), dict):
                data_for_rows = data["pattern_tables"]
            else:
                data_for_rows = data
            power_rows, brake_rows = self.normalize_preset_payload(data_for_rows)
            if not power_rows:
                raise ValueError("読み込めるPWMパターン行がありません。")

            self.pattern_rows_power = power_rows
            self.pattern_rows_brake = brake_rows or self.clone_pattern_rows(power_rows)
            self._last_pattern_table_key = self.edit_table_key()
            self.load_active_table_to_editor()
            self.apply_pattern_table(show_message=False)

            imported_name = ""
            if isinstance(data, dict):
                imported_name = str(data.get("preset_name") or data.get("name") or "").strip()
            if not imported_name:
                imported_name = "ユーザー: " + os.path.splitext(os.path.basename(path))[0]
            if not imported_name.startswith("ユーザー:"):
                imported_name = "ユーザー: " + imported_name
            PATTERN_PRESETS[imported_name] = {
                "power": self.clone_pattern_rows(self.pattern_rows_power),
                "brake": self.clone_pattern_rows(self.pattern_rows_brake),
            }
            self.update_preset_combo_values()
            self.save_preset_name_var.set(imported_name)
            self.pattern_preset_var.set(imported_name)
            self.status_text.set(f"PWMパターンテーブルをインポートしました: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("インポートエラー", str(e))

    def save_current_pattern_preset(self):
        try:
            if not self.apply_pattern_table(show_message=False):
                return
            name = self.save_preset_name_var.get().strip() or "ユーザー: カスタム"
            if not name.startswith("ユーザー:"):
                name = "ユーザー: " + name
            self.store_current_pattern_rows_to_active_table()
            rows = {
                "power": self.clone_pattern_rows(self.pattern_rows_power or self.pattern_rows),
                "brake": self.clone_pattern_rows(self.pattern_rows_brake or self.pattern_rows_power or self.pattern_rows),
            }
            self.user_presets[name] = rows
            PATTERN_PRESETS[name] = rows
            self.write_user_presets_to_file()
            self.update_preset_combo_values()
            self.pattern_preset_var.set(name)
            self.status_text.set(f"PWMパターンプリセット '{name}' を保存しました: {os.path.basename(self.user_preset_file)}")
        except Exception as e:
            messagebox.showerror("プリセット保存エラー", str(e))

    def delete_user_pattern_preset(self):
        name = self.pattern_preset_var.get().strip()
        if name not in self.user_presets:
            self.status_text.set("削除できるのは保存済みのユーザープリセットだけです。")
            return
        if not messagebox.askyesno("プリセット削除", f"'{name}' を削除しますか？"):
            return
        try:
            self.user_presets.pop(name, None)
            PATTERN_PRESETS.pop(name, None)
            self.write_user_presets_to_file()
            self.update_preset_combo_values()
            first = next(iter(PATTERN_PRESETS))
            self.pattern_preset_var.set(first)
            self.save_preset_name_var.set(first)
            self.load_pattern_preset(show_message=False)
            self.status_text.set(f"ユーザープリセット '{name}' を削除しました。")
        except Exception as e:
            messagebox.showerror("プリセット削除エラー", str(e))

    def load_pattern_preset(self, show_message=True):
        name = self.pattern_preset_var.get()
        if name not in PATTERN_PRESETS:
            name = next(iter(PATTERN_PRESETS))
            self.pattern_preset_var.set(name)
        # v28: プリセットを読み込んだ時は保存名も同じ名前へ合わせる。
        self.save_preset_name_var.set(name)
        self.pattern_rows_power, self.pattern_rows_brake = self.normalize_preset_payload(PATTERN_PRESETS[name])
        self._last_pattern_table_key = self.edit_table_key()
        self.load_active_table_to_editor()
        self.apply_pattern_table(show_message=False)
        self.refresh_pattern_tree(keep_selection=False)
        if show_message:
            self.status_text.set(f"プリセット '{name}' を読み込みました。加速/減速の2テーブルを編集できます。")

    def load_selected_pattern_preset(self):
        self.load_pattern_preset(show_message=True)

    def reset_pattern_table(self):
        self.load_pattern_preset(show_message=True)

    def apply_pattern_table(self, show_message=True):
        rows = []
        errors = []
        for idx, raw in enumerate(self.pattern_rows, start=1):
            try:
                vmax = float(raw["vmax"])
                kind = self.normalize_mode(raw["kind"])
                if kind == "":
                    raise ValueError(f"方式が不明: {raw.get('kind')}")
                value, value_end, value_text = self.parse_pattern_value(raw.get("value", 0.0), raw.get("value_end"))
                name = str(raw.get("name") or f"{MODE_LABELS[kind]} {value_text}")
                hf_mode = self.normalize_hf(raw.get("hf_mode") or "OFF")
                hf_amount = float(raw.get("hf_amount") or 0.0)
                hf_freq = raw.get("hf_freq")
                hf_freq = None if hf_freq is None or str(hf_freq).strip() == "" else max(20.0, min(2000.0, float(hf_freq)))
                spread_mode = self.normalize_spread(raw.get("spread_mode") or "OFF")
                spread_amount = float(raw.get("spread_amount") or 0.0)
                spread_rate = raw.get("spread_rate")
                spread_rate = None if spread_rate is None or str(spread_rate).strip() == "" else max(0.05, min(40.0, float(spread_rate)))
                row = {
                    "vmax": vmax, "kind": kind, "value": value, "name": name,
                    "hf_mode": hf_mode, "hf_amount": hf_amount, "hf_freq": hf_freq,
                    "spread_mode": spread_mode, "spread_amount": spread_amount, "spread_rate": spread_rate,
                }
                if value_end is not None:
                    row["value_end"] = value_end
                    row["value_text"] = value_text
                rows.append(row)
            except Exception as e:
                errors.append(f"{idx}行目: {e}")
        if not rows:
            self.status_text.set("PWMパターンが空です。プリセットを読み込むか、GUIで行を追加してください。")
            return False
        rows.sort(key=lambda r: r["vmax"])
        self.pattern_rows = rows
        self.store_current_pattern_rows_to_active_table()
        self.refresh_pattern_tree(keep_selection=True)
        table_name = self.pattern_table_mode_var.get() if hasattr(self, "pattern_table_mode_var") else "加速"
        msg = f"{table_name}PWMパターン {len(rows)}件を適用しました。"
        if errors:
            msg += "  警告: " + " / ".join(errors[:3])
        self.status_text.set(msg)
        if show_message and errors:
            messagebox.showwarning("パターン警告", "\n".join(errors[:8]))
        return not errors

    def on_pattern_tree_select(self, _event=None):
        if self.pattern_tree is None:
            return
        sel = self.pattern_tree.selection()
        if not sel:
            self.selected_pattern_iid = None
            return
        iid = sel[0]
        self.selected_pattern_iid = iid
        try:
            row = self.pattern_rows[int(iid)]
        except Exception:
            return
        self.row_vmax_var.set(f"{float(row['vmax']):g}")
        self.row_kind_var.set(MODE_LABELS.get(row["kind"], row["kind"]))
        self.row_value_var.set(self.format_pattern_value(row, edit=True))
        self.row_name_var.set(row.get("name", ""))
        self.row_hf_mode_var.set(HF_LABELS.get(row.get("hf_mode") or "OFF", "OFF"))
        self.row_hf_amount_var.set(f"{float(row.get('hf_amount') or 0):g}")
        self.row_hf_freq_var.set(f"{float(row.get('hf_freq') if row.get('hf_freq') is not None else self.hf_freq_var.get()):g}")
        self.row_spread_mode_var.set(SPREAD_LABELS.get(row.get("spread_mode") or "OFF", "OFF"))
        self.row_spread_amount_var.set(f"{float(row.get('spread_amount') or 0):g}")
        self.row_spread_rate_var.set(f"{float(row.get('spread_rate') if row.get('spread_rate') is not None else self.spread_rate_var.get()):g}")

    def read_editor_pattern_row(self):
        kind = self.normalize_mode(self.row_kind_var.get())
        if not kind:
            raise ValueError("PWM方式が不明です。")
        value, value_end, value_text = self.parse_pattern_value(self.row_value_var.get())
        name = self.row_name_var.get().strip() or f"{MODE_LABELS[kind]} {value_text}"
        row = {
            "vmax": float(self.row_vmax_var.get()),
            "kind": kind,
            "value": value,
            "name": name,
            "hf_mode": self.normalize_hf(self.row_hf_mode_var.get()),
            "hf_amount": float(self.row_hf_amount_var.get() or 0.0),
            "hf_freq": max(20.0, min(2000.0, float(self.row_hf_freq_var.get() or self.hf_freq_var.get()))),
            "spread_mode": self.normalize_spread(self.row_spread_mode_var.get()),
            "spread_amount": float(self.row_spread_amount_var.get() or 0.0),
            "spread_rate": max(0.05, min(40.0, float(self.row_spread_rate_var.get() or self.spread_rate_var.get()))),
        }
        if value_end is not None:
            row["value_end"] = value_end
            row["value_text"] = value_text
        return row

    def _select_matching_pattern_row(self, row):
        """並べ替え後、同じ内容に近い行を再選択する。"""
        if self.pattern_tree is None:
            return
        for i, r in enumerate(self.pattern_rows):
            try:
                rv, re, _ = self.parse_pattern_value(r.get("value", 0.0), r.get("value_end"))
                qv, qe, _ = self.parse_pattern_value(row.get("value", 0.0), row.get("value_end"))
                if (abs(float(r["vmax"]) - float(row["vmax"])) < 1e-6
                        and r["kind"] == row["kind"]
                        and abs(rv - qv) < 1e-6
                        and ((re is None and qe is None) or (re is not None and qe is not None and abs(re - qe) < 1e-6))
                        and str(r.get("name", "")) == str(row.get("name", ""))):
                    self.pattern_tree.selection_set(str(i))
                    self.pattern_tree.focus(str(i))
                    self.pattern_tree.see(str(i))
                    return
            except Exception:
                continue

    def add_pattern_row(self):
        """入力欄の内容を新規行として追加する。選択中の行は上書きしない。"""
        try:
            row = self.read_editor_pattern_row()
        except Exception as e:
            messagebox.showerror("パターン入力エラー", str(e))
            return
        self.pattern_rows.append(row)
        self.apply_pattern_table(show_message=False)
        self._select_matching_pattern_row(row)
        self.status_text.set("PWMパターン行を新規追加しました。")

    def update_selected_pattern_row(self):
        """選択中のPWMパターン行だけを入力欄の内容で更新する。"""
        if self.pattern_tree is None:
            return
        sel = self.pattern_tree.selection()
        if not sel:
            self.status_text.set("更新するPWMパターン行を選択してください。新規追加は「追加」を押してください。")
            return
        try:
            row = self.read_editor_pattern_row()
        except Exception as e:
            messagebox.showerror("パターン入力エラー", str(e))
            return
        try:
            idx = int(sel[0])
        except Exception:
            self.status_text.set("更新対象の行番号を取得できませんでした。")
            return
        if idx < 0 or idx >= len(self.pattern_rows):
            self.status_text.set("更新対象の行が見つかりません。")
            return
        self.pattern_rows[idx] = row
        self.apply_pattern_table(show_message=False)
        self._select_matching_pattern_row(row)
        self.status_text.set("選択中のPWMパターン行を更新しました。")

    def add_or_update_pattern_row(self):
        """旧版互換用。現在は未使用。選択行があれば更新、なければ追加。"""
        if self.pattern_tree is not None and self.pattern_tree.selection():
            self.update_selected_pattern_row()
        else:
            self.add_pattern_row()

    def delete_selected_pattern_row(self):
        if self.pattern_tree is None:
            return
        sel = self.pattern_tree.selection()
        if not sel:
            self.status_text.set("削除するPWMパターン行を選択してください。")
            return
        try:
            idx = int(sel[0])
            del self.pattern_rows[idx]
        except Exception:
            return
        if not self.pattern_rows:
            self.load_pattern_preset(show_message=False)
            self.status_text.set("最後の行は削除できないため、プリセットを復元しました。")
            return
        self.apply_pattern_table(show_message=False)
        self.status_text.set("選択したPWMパターン行を削除しました。")

    def move_selected_pattern_row(self, direction: int):
        if self.pattern_tree is None:
            return
        sel = self.pattern_tree.selection()
        if not sel:
            self.status_text.set("移動するPWMパターン行を選択してください。")
            return
        try:
            idx = int(sel[0])
        except Exception:
            return
        new_idx = idx + int(direction)
        if not (0 <= idx < len(self.pattern_rows) and 0 <= new_idx < len(self.pattern_rows)):
            return
        self.pattern_rows[idx], self.pattern_rows[new_idx] = self.pattern_rows[new_idx], self.pattern_rows[idx]
        # 速度上限で自動ソートすると上/下移動の意味が薄いので、vmax値を入れ替える。
        self.pattern_rows[idx]["vmax"], self.pattern_rows[new_idx]["vmax"] = self.pattern_rows[new_idx]["vmax"], self.pattern_rows[idx]["vmax"]
        self.apply_pattern_table(show_message=False)
        try:
            self.pattern_tree.selection_set(str(new_idx))
            self.pattern_tree.focus(str(new_idx))
        except Exception:
            pass

    def manual_mode_kind(self):
        s = self.manual_mode_var.get()
        table = {
            "非同期PWM": "ASYNC",
            "同期PWM": "SYNC",
            "SHE-PWM": "SHE",
            "CHM-PWM": "CHM",
            "広域3パルス": "WIDE3",
            "1パルス": "ONEPULSE",
        }
        return table.get(s, "ASYNC")

    def get_active_pattern(self):
        rows_for_drive = self.get_drive_pattern_rows()
        # v90: 手動PWMモードは廃止。常に速度域パターンテーブルを使う。
        if rows_for_drive:
            vmin = 0.0
            last_row = None
            last_vmin = 0.0
            for row in rows_for_drive:
                out = dict(row)
                out["_vmin"] = vmin
                vmax = float(out.get("vmax", 999.0))
                last_row = out
                last_vmin = vmin
                if self.speed_kmh <= vmax:
                    return out
                vmin = vmax
            if last_row is not None:
                last_row["_vmin"] = last_vmin
                return last_row

        kind = self.manual_mode_kind()
        if kind == "ASYNC":
            value = float(self.carrier_var.get())
        elif kind == "WIDE3":
            value = 3.0
        elif kind == "ONEPULSE":
            value = 1.0
        else:
            value = float(self.sync_pulses_var.get())
        return {"vmax": 999.0, "kind": kind, "value": value, "name": f"手動 {MODE_LABELS[kind]}"}

    # -------------------- マスコン --------------------
    def set_notch(self, new_notch: int):
        old = self.notch
        self.prev_notch = old
        self.notch = max(-7, min(5, int(new_notch)))
        now = time.perf_counter()

        # v62:
        # N↔P/B遷移音を復活。ただし速度0では鳴らさない。
        # P/B→Nのときは、transition_async_source="to_neutral" として
        # 中立ノッチ中でも遷移時間だけ低速非同期を鳴らし、終了後は完全に相間電圧0に戻す。
        moving = self.speed_kmh > 0.2
        self.transition_async_until = 0.0
        self.transition_async_start = now
        self.transition_async_duration = 0.0
        self.transition_ramp_dir = "none"
        self.transition_async_source = ""

        if old == 0 and self.notch != 0:
            if moving:
                dur = max(0.0, float(self.transition_async_time_var.get()))
                self.transition_async_duration = dur
                self.transition_async_until = now + dur
                self.transition_ramp_dir = "up"
                self.transition_async_source = "from_neutral"
                self.transition_note = f"N→{'P' if self.notch > 0 else 'B'}: 電圧0→既定値 / {dur:.2f}s 低速非同期" if dur > 0 else "N→P/B: 即時投入"
            else:
                self.transition_note = "速度0: ノッチ投入音なし"

        elif old != 0 and self.notch == 0:
            if moving:
                dur = max(0.0, float(self.transition_async_time_var.get()))
                self.transition_async_duration = dur
                self.transition_async_until = now + dur
                self.transition_ramp_dir = "down"
                self.transition_async_source = "to_neutral"
                self.transition_note = f"P/B→N: 電圧既定値→0% / {dur:.2f}s 低速非同期後に無音" if dur > 0 else "P/B→N: 中立無音"
            else:
                self.transition_note = "速度0: 中立無音"

        self.update_notch_label()

    def brake_up(self):
        # v67: 上方向はブレーキ側へ1ノッチ。
        # 例: P2→P1→N→B1→B2...
        if self.notch > -7:
            self.set_notch(self.notch - 1)
        else:
            self.update_notch_label()

    def power_down(self):
        # v67: 下方向は力行側へ1ノッチ。
        # 例: B3→B2→B1→N→P1→P2...
        if self.notch < 5:
            self.set_notch(self.notch + 1)
        else:
            self.update_notch_label()

    # 旧名も残して、既存のボタン/外部呼び出しがあっても動くようにする。
    def power_up(self):
        self.power_down()

    def brake_down(self):
        self.brake_up()

    def neutral(self):
        self.set_notch(0)

    def update_notch_label(self):
        s = self.notch_text()
        self.notch_label.config(text=s)

    # -------------------- グローバルキー操作 --------------------
    def _global_key_schedule(self, action: str):
        """キー操作を1押下=1ノッチに整える共通入口。

        v69:
        アプリがアクティブな時は Tk の bind_all と Windows API ポーリングの
        両方が同じキーを拾うことがある。そのため全キー入力をここに集約し、
        短時間の重複を無視する。
        """
        now = time.perf_counter()
        debounce = float(getattr(self, "_key_debounce_sec", 0.18))
        if now - self._last_global_key_time < debounce:
            # 同じ押下から来た重複イベントを捨てる。
            return
        self._last_global_key_time = now
        self._last_global_action = str(action)

        def run():
            if action == "brake":
                self.brake_up()
            elif action == "power":
                self.power_down()
            elif action == "neutral":
                self.neutral()

        try:
            self.root.after(0, run)
        except Exception:
            pass

    def start_global_hotkeys(self):
        """v70: 他アプリ使用中のグローバルキー操作は廃止。"""
        self.global_hotkey_enabled = False
        self._global_poll_running = False
        self._global_poll_backend = None
        self.status_text.set("グローバルキーは無効です。キー操作はこのアプリ/表示画面がアクティブな時だけ有効です。")
        return


    def poll_global_keys(self):
        """v70: グローバルキーポーリングは無効。"""
        self._global_poll_running = False
        return


    # -------------------- 音声プロセス制御 --------------------
    def current_hf_mode(self):
        return self.normalize_hf(self.hf_mode_var.get())

    def current_spread_mode(self):
        return self.normalize_spread(self.spread_mode_var.get())

    def is_transition_async_active(self):
        # N→P/B と P/B→N の両方で短時間だけ有効。
        # 音声START直後は transition_async_until=0 なので鳴らない。
        return time.perf_counter() < self.transition_async_until

    def transition_voltage_scale(self) -> float:
        """N↔P/B遷移時の電圧ランプ倍率。

        N→P/B: 0→1、P/B→N: 1→0。
        この値を「既定の電圧指令」に掛ける。
        立ち上がり/立ち下がりは少し滑らかなS字にする。
        """
        if not self.is_transition_async_active():
            return 1.0 if self.notch != 0 else 0.0
        dur = max(1e-6, float(self.transition_async_duration))
        t = max(0.0, min(1.0, (time.perf_counter() - self.transition_async_start) / dur))
        smooth = t * t * (3.0 - 2.0 * t)
        if self.transition_ramp_dir == "down":
            return 1.0 - smooth
        return smooth

    def get_lowest_async_pattern(self):
        """遷移音に使う「もっとも低速域の非同期PWMパターン」を返す。

        パターン表にASYNC行があれば最小vmaxのASYNC行を使う。
        なければ最小速度域の行を元に、方式だけASYNCへ置き換える。
        """
        rows = list(self.get_drive_pattern_rows() or [])
        if not rows:
            return {
                "vmax": 999.0, "kind": "ASYNC", "value": float(self.carrier_var.get()),
                "name": "遷移 非同期", "hf_mode": self.current_hf_mode(),
                "hf_amount": float(self.hf_amount_var.get()),
                "spread_mode": self.current_spread_mode(),
                "spread_amount": float(self.spread_amount_var.get()),
            }
        rows = sorted(rows, key=lambda r: float(r.get("vmax", 999.0)))
        async_rows = [r for r in rows if str(r.get("kind", "")).upper() == "ASYNC"]
        base = dict(async_rows[0] if async_rows else rows[0])
        base["kind"] = "ASYNC"
        # ASYNCの値はキャリア周波数として扱う。範囲指定なら低速側の値を遷移音に使う。
        try:
            val, val_end, val_text = self.parse_pattern_value(base.get("value", 0.0), base.get("value_end"))
        except Exception:
            val, val_end, val_text = 0.0, None, "0"
        if val < 100.0:
            val = float(self.carrier_var.get())
            val_end = None
        base["value"] = val
        base.pop("value_end", None)
        base.pop("value_text", None)
        base["name"] = str(base.get("name") or "低速 非同期") + "（遷移音）"
        return base

    def current_params(self) -> dict:
        max_speed = max(1.0, float(self.maxspeed_var.get()))
        max_f0 = max(1.0, float(self.maxf0_var.get()))
        # v35: 最高基本周波数を「上限」ではなく、
        #      最高周波数到達速度での基準基本周波数として扱う。
        #      その速度を超えても f0 は速度比例で上がり続ける。
        #      ただし電圧指令は基底速度以降で頭打ちにし、簡易弱め界磁領域にする。
        freq_fullspeed = max(1.0, float(self.freq_fullspeed_var.get()))
        speed_ratio = max(0.0, min(1.0, self.speed_kmh / max_speed))
        freq_ratio_raw = max(0.0, self.speed_kmh / freq_fullspeed)
        voltage_freq_ratio = max(0.0, min(1.0, freq_ratio_raw))
        # 安全のため極端なGUI設定でも音声/描画が破綻しにくい上限だけ設ける。
        f0 = min(freq_ratio_raw * max_f0, 2000.0)
        modmax = max(0.05, min(1.00, float(self.modmax_var.get()) / 100.0))
        # 起動電圧は0〜5%を許可する。
        start_voltage = max(0.0, min(0.05, float(self.start_voltage_var.get()) / 100.0))
        voltage100_v = max(1.0, float(self.voltage100_var.get()))

        # 低速でも起動電圧ぶんだけPWM音/電圧を持たせる。
        # ただしNで遷移音が無いときは後段のdrive_active判定で0になる。
        modulation_base = min(modmax, start_voltage + (modmax - start_voltage) * (voltage_freq_ratio ** 0.92))
        if self.speed_kmh < 0.2 and self.notch == 0:
            modulation_base = 0.0

        pat = self.get_active_pattern()
        base_kind = pat["kind"]
        kind = base_kind
        if kind == "ASYNC":
            value = self.async_value_for_speed(pat)
        else:
            value, _value_end, _value_text = self.parse_pattern_value(pat.get("value", 0.0), pat.get("value_end"))

        # ノッチ遷移時だけ、現在の速度域パターンではなく、もっとも低速域の非同期PWMを挿入する。
        # v62: 速度0時は遷移音を禁止。P/B→Nでは中立ノッチ中でも遷移時間だけ鳴らす。
        transition_async = self.is_transition_async_active() and (self.speed_kmh > 0.2)
        voltage_scale = self.transition_voltage_scale() if transition_async else 0.0
        transition_pat = None
        if transition_async:
            transition_pat = self.get_lowest_async_pattern()
            kind = "ASYNC"
            tv, _te, _tt = self.parse_pattern_value(transition_pat.get("value", self.carrier_var.get()), transition_pat.get("value_end"))
            value = max(100.0, float(tv))
            if f0 < 2.0:
                f0 = 2.0

        sync_pulses = int(value if kind != "ASYNC" else self.sync_pulses_var.get())

        # v62: 通常のNではインバータOFF。ただしP/B→N遷移中だけは低速非同期音を許可する。
        # 遷移終了後は drive_active=False になり、相間電圧は0へ戻る。
        drive_active = (self.notch != 0) or transition_async
        # v91: 速度0では表示・音声ともPWM電圧を0にする。
        # 起動電圧によって停止中にPWM波形が出るのを防ぐ。
        if self.speed_kmh < 0.2:
            drive_active = False
        if not drive_active:
            modulation = 0.0
        elif transition_async:
            # N→P/Bは0→既定電圧、P/B→Nは既定電圧→0へ滑らかに変化させる。
            # v14: 停止付近の既定電圧は100%ではなく、起動電圧1〜5%を基準にする。
            transition_target = min(modmax, max(modulation_base, start_voltage))
            modulation = transition_target * max(0.0, min(1.0, voltage_scale))
        elif kind == "ONEPULSE":
            # 1パルスは電圧制御せず、常に100%電圧利用率として扱う。
            modulation = modmax
        else:
            modulation = modulation_base

        # 方式ごとの見た目・音の変化を少し強調。ただし1パルスは100%固定を崩さない。
        if kind in ("SHE", "WIDE3"):
            modulation = min(modmax, modulation * 1.06)
        elif kind == "CHM":
            modulation = min(modmax, modulation * 1.02)

        # v35: 「最高基本周波数」を上限でなく基準周波数として扱う。
        # 指定した「最高周波数到達速度」を超えても基本波は速度比例で上がり続ける。
        # 電圧指令だけは基底速度以降で頭打ちにし、簡易的な定電圧/弱め界磁領域として扱う。

        # v34: 「変調率100%の相間電圧[V]」に対する現在電圧なので、
        # 表示・疑似電力は最大変調率スライダーで割らず、実際の絶対変調率を使う。
        # 例: 最大変調率を80%に制限していても、現在電圧は100%電圧の80%になる。
        voltage_use_ratio = 1.0 if kind == "ONEPULSE" and drive_active else max(0.0, min(1.0, modulation))
        motor_voltage_v = voltage100_v * voltage_use_ratio
        sign_notch_for_power = self.prev_notch if transition_async and self.notch == 0 else self.notch
        sign = 1.0 if sign_notch_for_power >= 0 else -1.0
        load_ratio = float(self.load_var.get()) / 100.0
        # v91:
        # 疑似モーター電力はノッチ段数で変えない。
        # ノッチは力行/ブレーキの向きだけに使い、電力量は電圧指令と負荷率で決める。
        motor_kw = sign * float(self.power_scale_var.get()) * voltage_use_ratio * min(1.2, load_ratio)
        motor_kw_ratio = abs(motor_kw) / max(1.0, float(self.power_scale_var.get()))

        sound_pat = transition_pat if transition_pat is not None else pat
        hf_mode = sound_pat.get("hf_mode") or self.current_hf_mode()
        hf_amount = sound_pat.get("hf_amount")
        if hf_amount is None:
            hf_amount = float(self.hf_amount_var.get())
        hf_freq = sound_pat.get("hf_freq")
        if hf_freq is None:
            hf_freq = float(self.hf_freq_var.get())
        spread_mode = sound_pat.get("spread_mode") or self.current_spread_mode()
        spread_amount = sound_pat.get("spread_amount")
        if spread_amount is None:
            spread_amount = float(self.spread_amount_var.get())
        spread_rate = sound_pat.get("spread_rate")
        if spread_rate is None:
            spread_rate = float(self.spread_rate_var.get())

        transition_text = " / 遷移非同期" if transition_async else (" / 中立無音" if not drive_active else "")
        shown_name = sound_pat.get("name", pat.get("name", ""))
        if base_kind == "ASYNC" and pat.get("value_end") is not None and not transition_async:
            value_show = f"{value:.0f}Hz（{self.format_pattern_value(pat)}）"
        else:
            value_show = f"{value:g}"
        self.active_pattern_text.set(
            f"現在: {shown_name} / {MODE_LABELS[base_kind]}→{MODE_LABELS[kind]} / 値={value_show} / 上限={pat['vmax']:g} km/h{transition_text}"
        )

        return {
            "f0": f0,
            "pwm_kind": kind,
            "base_pwm_kind": base_kind,
            "pattern_value": value,
            "carrier": float(self.carrier_var.get()),
            "sync_pulses": sync_pulses,
            "volume": float(self.volume_var.get()) / 100.0,
            "roughness": float(self.roughness_var.get()) / 100.0,
            "load": float(self.load_var.get()) / 100.0,
            "modulation": modulation,
            "voltage_use_ratio": voltage_use_ratio,
            "voltage100_v": voltage100_v,
            "motor_voltage_v": motor_voltage_v,
            "motor_kw": motor_kw,
            "motor_kw_ratio": motor_kw_ratio,
            "voltage_gain_0": max(0.0, min(300.0, float(self.voltage_gain_0_var.get()))) / 100.0,
            "voltage_gain_100": max(0.0, min(300.0, float(self.voltage_gain_100_var.get()))) / 100.0,
            "startup_voltage_pct": start_voltage * 100.0,
            "freq_ratio": freq_ratio_raw,
            "voltage_freq_ratio": voltage_freq_ratio,
            "freq_fullspeed": freq_fullspeed,
            "base_f0_at_fullspeed": max_f0,
            "speed_ratio": speed_ratio,
            "wind_enabled": bool(self.wind_noise_var.get()),
            "wind_amount": float(self.wind_amount_var.get()) / 100.0,
            "rolling_enabled": bool(self.rolling_noise_var.get()),
            "rolling_amount": float(self.rolling_amount_var.get()) / 100.0,
            "resonance_enabled": bool(self.resonance_filter_var.get()),
            "resonance_amount": float(self.resonance_amount_var.get()) / 100.0,
            "resonance_shift": float(self.resonance_shift_var.get()),
            "echo_enabled": bool(self.echo_mode_var.get()),
            "echo_amount": float(self.echo_amount_var.get()) / 100.0,
            "echo_delay_ms": float(self.echo_delay_var.get()),
            "notch": self.notch,
            "drive_active": drive_active,
            "transition_async": transition_async,
            "voltage_scale": voltage_scale,
            "hf_mode": hf_mode,
            "hf_amount": max(0.0, min(25.0, float(hf_amount))) / 100.0,
            "hf_freq": max(20.0, min(2000.0, float(hf_freq))),
            "spread_mode": spread_mode,
            "spread_amount": max(0.0, min(35.0, float(spread_amount))) / 100.0,
            "spread_rate": max(0.05, min(40.0, float(spread_rate))),
            "scope_window_ms": max(5.0, min(200.0, float(self.scope_window_ms_var.get()))),
            "device": None,
            "pattern_name": pat["name"],
        }

    # -------------------- 現在設定の保存/読込 --------------------
    def app_base_dir(self) -> str:
        """設定・パターンテーブルを置く基準フォルダ。

        通常実行時:
            pyファイルのあるフォルダ
        Nuitka standalone:
            exeのあるフォルダ
        Nuitka onefile:
            sys.argv[0] が元のonefile exeのパス、
            __file__ は展開先の一時フォルダになる。
            そのため、外部設定ファイルは sys.argv[0] 側を優先する。
        """
        candidates = []

        def add_candidate(path_value):
            try:
                if not path_value:
                    return
                p = os.path.abspath(str(path_value))
                if os.path.isdir(p):
                    d = p
                else:
                    d = os.path.dirname(p)
                if d and d not in candidates:
                    candidates.append(d)
            except Exception:
                pass

        # v94:
        # Nuitka onefileでは、sys.argv[0] が元のexe、
        # __file__ が展開先になる。exe横のJSONを探すにはsys.argv[0]を優先する。
        try:
            add_candidate(sys.argv[0] if sys.argv else "")
        except Exception:
            pass

        try:
            add_candidate(sys.executable)
        except Exception:
            pass

        try:
            add_candidate(__file__)
        except Exception:
            pass

        for d in candidates:
            try:
                if os.path.isdir(d):
                    return d
            except Exception:
                pass
        return os.getcwd()


    def current_settings_path(self) -> str:
        """py/exeファイルと同じディレクトリに保存する現在設定ファイルのパス。"""
        return os.path.join(self.app_base_dir(), "vvvf_current_settings.json")

    def current_settings_payload(self) -> dict:
        """現在のGUI設定と加速/減速PWMパルステーブルを保存する。"""
        var_names = [
            "manual_mode_var", "pattern_auto_var",
            "volume_var", "carrier_var", "sync_pulses_var",
            "roughness_var", "load_var",
            "maxspeed_var", "maxf0_var", "freq_fullspeed_var",
            "accel_var", "brake_var",
            "modmax_var", "start_voltage_var", "voltage100_var",
            "voltage_gain_0_var", "voltage_gain_100_var",
            "scope_window_ms_var", "power_scale_var",
            "hf_mode_var", "hf_amount_var", "hf_freq_var",
            "spread_mode_var", "spread_amount_var", "spread_rate_var",
            "transition_async_time_var",
            "wind_noise_var", "wind_amount_var",
            "rolling_noise_var", "rolling_amount_var",
            "resonance_filter_var", "resonance_amount_var", "resonance_shift_var",
            "echo_mode_var", "echo_amount_var", "echo_delay_var",
            "pattern_preset_var", "save_preset_name_var",
            "row_hf_freq_var", "row_spread_rate_var",
        ]
        settings = {}
        for name in var_names:
            var = getattr(self, name, None)
            if var is None:
                continue
            try:
                settings[name] = var.get()
            except Exception:
                pass

        # v89:
        # 「現在設定を保存」でGUI設定だけでなく、現在の加速/減速パルステーブルも同じJSONへ保存する。
        # これにより起動時に設定とパルステーブルをまとめて復元できる。
        try:
            pattern_payload = self.current_pattern_payload()
            pattern_tables = {
                "power": pattern_payload.get("power", []),
                "brake": pattern_payload.get("brake", []),
                "preset_name": pattern_payload.get("preset_name", "ユーザー: カスタム"),
            }
        except Exception:
            pattern_tables = {}

        return {
            "format": "VVVF_CURRENT_SETTINGS",
            "version": 2,
            "settings": settings,
            "pattern_tables": pattern_tables,
            "note": "GUI設定と現在の加速/減速PWMパルステーブルをpyファイルと同じディレクトリに保存します。",
        }

    def save_current_settings_to_script_dir(self):
        """現在の音量・速度・加速度・音響・表示・パルステーブルなどの設定を保存する。"""
        try:
            payload = self.current_settings_payload()
            path = self.current_settings_path()
            with open(path, "w", encoding="utf-8") as f:
                json.dump(payload, f, ensure_ascii=False, indent=2)
            self.status_text.set(f"現在設定とPWMパルステーブルを保存しました: {os.path.basename(path)}")
        except Exception as e:
            messagebox.showerror("現在設定 保存エラー", str(e))

    def load_current_settings_from_script_dir(self, show_message=True, startup=False):
        """pyファイルと同じディレクトリの現在設定ファイルを読み込む。

        v89:
        - 起動時は show_message=False/startup=True で自動読込
        - version 2形式ではGUI設定に加えてパルステーブルも復元
        - 旧version 1形式では、保存されているプリセット名を使ってパターンだけ再読込
        """
        try:
            path = self.current_settings_path()
            if not os.path.exists(path):
                if show_message:
                    self.status_text.set(f"現在設定ファイルがありません: {os.path.basename(path)}")
                return False

            with open(path, "r", encoding="utf-8") as f:
                payload = json.load(f)

            settings = payload.get("settings") if isinstance(payload, dict) else None
            if not isinstance(settings, dict):
                raise ValueError("現在設定ファイルの形式が違います。")

            for name, value in settings.items():
                var = getattr(self, name, None)
                if var is None:
                    continue
                try:
                    var.set(value)
                except Exception:
                    pass
            try:
                # v90: 保存ファイルが旧版で pattern_auto_var=False でも、起動後は必ずパターン専用に戻す。
                self.pattern_auto_var.set(True)
            except Exception:
                pass

            # パルステーブル本体を復元。
            restored_table = False
            pattern_tables = None
            if isinstance(payload, dict):
                pattern_tables = payload.get("pattern_tables")
                # 将来/手編集互換: {power, brake} が直下にある場合も許容。
                if pattern_tables is None and ("power" in payload or "brake" in payload):
                    pattern_tables = payload

            if isinstance(pattern_tables, dict) and (pattern_tables.get("power") or pattern_tables.get("brake")):
                power_rows, brake_rows = self.normalize_preset_payload(pattern_tables)
                if power_rows:
                    self.pattern_rows_power = self.clone_pattern_rows(power_rows)
                    self.pattern_rows_brake = self.clone_pattern_rows(brake_rows or power_rows)
                    preset_name = str(pattern_tables.get("preset_name") or settings.get("save_preset_name_var") or "ユーザー: 自動読込")
                    try:
                        self.pattern_preset_var.set(preset_name)
                        self.save_preset_name_var.set(preset_name)
                    except Exception:
                        pass
                    self._last_pattern_table_key = self.edit_table_key()
                    self.load_active_table_to_editor()
                    self.apply_pattern_table(show_message=False)
                    self.refresh_pattern_tree(keep_selection=False)
                    restored_table = True

            # 旧形式など、テーブル本体が無い場合は保存されたプリセット名から再読込。
            if not restored_table:
                try:
                    name = self.pattern_preset_var.get()
                    if name in PATTERN_PRESETS:
                        self.load_pattern_preset(show_message=False)
                    else:
                        self.apply_pattern_table(show_message=False)
                except Exception:
                    pass

            if show_message:
                suffix = "設定とPWMパルステーブル" if restored_table else "設定"
                self.status_text.set(f"現在{suffix}を読み込みました: {os.path.basename(path)}")
            elif startup:
                try:
                    suffix = "設定とPWMパルステーブル" if restored_table else "設定"
                    self.status_text.set(f"起動時に{suffix}を自動読込しました: {os.path.basename(path)}")
                except Exception:
                    pass
            return True
        except Exception as e:
            if show_message:
                messagebox.showerror("現在設定 読込エラー", str(e))
            else:
                try:
                    self.status_text.set(f"起動時の現在設定読込をスキップしました: {e}")
                except Exception:
                    pass
            return False


    def start_audio(self):
        """音声生成を開始する。

        v93:
        Nuitkaでexe化したとき、Windowsのmultiprocessing spawnが
        [WinError 193] 有効なWin32アプリケーションではありません
        を出すことがあるため、音声生成は別プロセスではなくdaemonスレッドで起動する。
        """
        if self.audio_proc is not None and self.audio_proc.is_alive():
            self.status_text.set("音声はすでに動作中です。")
            return
        try:
            self.apply_pattern_table(show_message=False)
            self.cmd_q = queue.Queue()
            self.status_q = queue.Queue()
            params = self.current_params()
            self.cmd_q.put(params)
            self.audio_proc = threading.Thread(
                target=audio_worker,
                args=(self.cmd_q, self.status_q, params),
                daemon=True,
                name="VVVF-Audio",
            )
            self.audio_proc.start()
            self.status_text.set("音声スレッドを起動しました。")
        except Exception as e:
            self.status_text.set(f"音声起動失敗: {e}")
            messagebox.showerror("音声起動エラー", str(e))

    def stop_audio(self):
        if self.audio_proc is None:
            self.status_text.set("音声は停止しています。")
            return
        try:
            if self.cmd_q is not None:
                self.cmd_q.put({"cmd": "stop"})
            self.audio_proc.join(timeout=1.5)
            if self.audio_proc.is_alive():
                self.status_text.set("音声停止要求を送信しました。終了待ちです。")
            else:
                self.status_text.set("音声を停止しました。")
        except Exception as e:
            self.status_text.set(f"音声停止エラー: {e}")
        finally:
            if self.audio_proc is not None and not self.audio_proc.is_alive():
                self.audio_proc = None
                self.cmd_q = None
                self.status_q = None

    def kill_audio(self):
        # スレッド方式では強制terminateはできないため、停止要求を送る。
        if self.audio_proc is not None and self.audio_proc.is_alive():
            try:
                if self.cmd_q is not None:
                    self.cmd_q.put({"cmd": "stop"})
                self.audio_proc.join(timeout=1.5)
            except Exception:
                pass
        if self.audio_proc is not None and self.audio_proc.is_alive():
            self.status_text.set("音声停止要求を送信しました。")
            return
        self.audio_proc = None
        self.cmd_q = None
        self.status_q = None
        self.status_text.set("音声を停止しました。")


    def send_params_to_audio(self):
        if self.audio_proc is None or not self.audio_proc.is_alive() or self.cmd_q is None:
            return
        now = time.perf_counter()
        # v59: ASYNC 750↔1050Hzのようなランプをより滑らかにするため、
        # 送信間隔を少しだけ短くする。ただしv16以前の10msには戻さず、音声負荷を抑える。
        if now - self.last_param_send < 0.018:
            return
        self.last_param_send = now
        try:
            self.cmd_q.put_nowait(self.current_params())
        except Exception:
            pass

    def poll_audio_status(self):
        if self.status_q is None:
            return
        got = None
        while True:
            try:
                got = self.status_q.get_nowait()
            except queue.Empty:
                break
            except Exception:
                break
        if got:
            msg = str(got.get("message", got))
            self.status_text.set(msg)

    # -------------------- 走行・描画更新 --------------------
    def tick(self):
        """走行計算・音声パラメータ送信・描画の周期処理。

        v20では描画中の例外(IndexErrorなど)が出ると root.after() まで到達せず、
        以後の加速/減速計算も止まって「音は鳴るが速度が変わらない」状態になった。
        v21では必ず次回tickを予約し、描画エラーはステータスに出して継続する。
        """
        now = time.perf_counter()
        dt = max(0.001, min(0.05, now - self.last_update))
        self.last_update = now
        try:
            self.update_dynamics(dt)
            self.send_params_to_audio()
            self.poll_audio_status()
            try:
                self.draw()
            except Exception as e:
                # 描画だけの失敗で制御ループを止めない。
                self.status_text.set(f"描画警告: {type(e).__name__}: {e}")
        finally:
            self.root.after(33, self.tick)

    def update_dynamics(self, dt: float):
        """速度更新。

        v70:
        3km/h以下で加速度/減速度が異様に弱くなる現象を修正。
        低速ではノッチに応じた最低加速度を確保し、停止直前のブレーキも弱くなりすぎないようにする。
        """
        max_speed = max(1.0, float(self.maxspeed_var.get()))
        accel_base = max(0.0, float(self.accel_var.get()))
        brake_base = max(0.0, float(self.brake_var.get()))
        speed_ratio_total = max(0.0, min(1.0, self.speed_kmh / max_speed))

        if self.notch > 0:
            notch_ratio = max(0.0, min(1.0, self.notch / 5.0))

            # 小さいPノッチほど低い速度で頭打ち。
            notch_limit_table = {
                1: 0.28,
                2: 0.45,
                3: 0.63,
                4: 0.82,
                5: 1.00,
            }
            notch_limit_ratio = notch_limit_table.get(self.notch, 1.0)
            notch_limit_speed = max(1.0, max_speed * notch_limit_ratio)
            local_ratio = max(0.0, min(1.25, self.speed_kmh / notch_limit_speed))

            curve = max(0.0, 1.0 - local_ratio) ** 1.75

            start_accel = accel_base * (3.2 + 6.0 * notch_ratio)
            crawl_accel = accel_base * (0.025 + 0.060 * notch_ratio)
            accel = crawl_accel + (start_accel - crawl_accel) * curve

            if local_ratio >= 1.0:
                accel = accel_base * 0.006 * notch_ratio

            # 3km/h以下で遅すぎないよう最低加速度を確保。
            if self.speed_kmh < 3.0:
                low = max(0.0, 1.0 - self.speed_kmh / 3.0)
                min_low_accel = accel_base * (1.15 + 2.40 * notch_ratio)
                accel = max(accel, min_low_accel * (0.55 + 0.45 * low))

            if self.speed_kmh < 4.0:
                creep_boost = (1.0 - self.speed_kmh / 4.0) ** 2
                accel *= (1.0 + 0.16 * creep_boost)

        elif self.notch < 0:
            brake_ratio = max(0.0, min(1.0, (-self.notch) / 7.0))

            # ほぼ一定減速度。高速側ほど少しだけ弱くする。
            base_brake = brake_base * (0.42 + 1.02 * brake_ratio)
            high_speed_weaken = 1.0 - 0.18 * (speed_ratio_total ** 1.15)
            brake = base_brake * high_speed_weaken

            # 3km/h以下で減速度が弱くなりすぎないようにする。
            if self.speed_kmh < 3.0:
                low = max(0.0, 1.0 - self.speed_kmh / 3.0)
                min_low_brake = brake_base * (0.52 + 1.10 * brake_ratio)
                brake = max(brake, min_low_brake * (0.60 + 0.40 * low))

            if self.speed_kmh < 2.0:
                stop_boost = (1.0 - self.speed_kmh / 2.0) ** 2
                brake *= (1.0 + 0.10 * stop_boost)

            accel = -brake

        else:
            # 惰行N: 毎分2km/hで速度低下。
            accel = -(2.0 / 60.0)

        self.current_accel_kmhps = accel
        self.speed_kmh += accel * dt

        if self.speed_kmh < 0.0:
            self.speed_kmh = 0.0
            self.current_accel_kmhps = 0.0
        if self.speed_kmh > max_speed:
            self.speed_kmh = max_speed
            self.current_accel_kmhps = 0.0

        f0 = self.current_params()["f0"]
        self.elec_phase = (self.elec_phase + TAU * f0 * dt) % TAU

    # -------------------- 描画 --------------------
    def draw(self):
        # 設定画面内のプレビューCanvasと、別ウィンドウの表示Canvasの両方を更新する。
        for c in (getattr(self, "canvas", None), getattr(self, "display_canvas", None)):
            try:
                if c is not None and c.winfo_exists():
                    self.draw_dashboard_canvas(c)
            except tk.TclError:
                pass
            except Exception as e:
                self.status_text.set(f"描画警告: {type(e).__name__}: {e}")

    def draw_dashboard_canvas(self, c):
        c.delete("all")
        w = max(1, c.winfo_width())
        h = max(1, c.winfo_height())

        c.create_rectangle(0, 0, w, h, fill="#0f1218", outline="")
        c.create_text(18, 14, anchor="nw", text="PWM積分ベクトル軌跡・パワー表示", fill="#e8edf7", font=self.font_canvas_title)
        c.create_text(18, 42, anchor="nw", text="PWM波形→Clarke αβ電圧→時間積分で磁束相当軌跡を描画。下のPWM波形は固定時間軸です。", fill="#aeb7c8", font=self.font_canvas_subtitle)

        params = self.current_params()
        pat = self.get_active_pattern()
        max_speed = max(1.0, float(self.maxspeed_var.get()))
        speed_ratio = max(0.0, min(1.0, self.speed_kmh / max_speed))
        f0 = params["f0"]
        kind = params["pwm_kind"]
        value = params["pattern_value"]

        if kind == "ASYNC":
            carrier = value if value > 10 else float(self.carrier_var.get())
        elif kind == "WIDE3":
            carrier = max(0.0, f0 * 3.0)
        elif kind == "ONEPULSE":
            carrier = max(0.0, f0)
        else:
            carrier = max(0.0, f0 * max(1.0, value))

        modulation = params["modulation"]
        use_ratio = max(0.0, min(1.08, float(params.get("voltage_use_ratio", 0.0))))
        power_scale = float(self.power_scale_var.get())
        # v14: 疑似パワーは速度比例の機械出力ではなく、現在の電圧・負荷・ノッチから見た
        # 疑似モーター電力を表示する。起動直後でも小さなW/kWが出る。
        pseudo_kw = float(params.get("motor_kw", 0.0))

        self.draw_speed_meter(c, x=155, y=245, r=118, speed=self.speed_kmh, max_speed=max_speed)
        self.draw_power_bar(c, x=38, y=410, w=260, h=42, kw=pseudo_kw, scale=power_scale)
        self.draw_pattern_strip(c, x=34, y=490, w=285, h=96, active=pat)

        panel_x = max(705, w - 285)
        panel_y = 72
        info_h = min(330, max(250, h - 390))

        # v90:
        # 右側パネルと下側波形が重ならないよう、表示幅から右パネル分を先に確保する。
        hex_cx = int(min(w * 0.60, panel_x - 260))
        hex_cx = max(520, hex_cx)
        # v91: 下部説明・ベクトルラベルとの重なりを避けるため、磁束図を少し上げて小さくする。
        hex_cy = int(h * 0.365)
        hex_r = int(min(w, h) * 0.220)
        self.draw_hex_svpwm(
            c, hex_cx, hex_cy, hex_r, self.elec_phase, use_ratio, pseudo_kw, power_scale, kind, params
        )

        wave_x = 330
        wave_y = h - 150
        wave_w = max(430, panel_x - wave_x - 28)
        wave_h = 108
        self.draw_pwm_voltage_waves(c, x=wave_x, y=wave_y, w=wave_w, h=wave_h, params=params)
        self.draw_info_panel(c, panel_x, panel_y, 262, info_h, {
            "ノッチ": self.notch_text(),
            "速度": f"{self.speed_kmh:5.1f} km/h",
            "加速度": f"{self.current_accel_kmhps:5.2f} km/h/s",
            "基本波": f"{f0:5.2f} Hz",
            "PWM周波数": f"{carrier:5.0f} Hz",
            "PWM方式": MODE_LABELS[kind],
            "パターン": pat["name"],
            "値": f"{value:g}",
            "電圧指令": f"{use_ratio * 100:5.1f} %",
            "現在電圧": f"{params.get('motor_voltage_v', 0.0):5.0f} V",
            "疑似電力": f"{pseudo_kw:6.1f} kW",
            "重畳": f"{HF_LABELS.get(params.get('hf_mode', 'OFF'), 'OFF')} {params.get('hf_amount', 0.0) * 100:.1f}%",
            "拡散": f"{SPREAD_LABELS.get(params.get('spread_mode', 'OFF'), 'OFF')} {params.get('spread_amount', 0.0) * 100:.1f}%",
            "走行音": "ON" if self.wind_noise_var.get() else "OFF",
            "転動音": "ON" if self.rolling_noise_var.get() else "OFF",
            "遷移": self.transition_note if self.transition_note else "-",
        })

        # 右側にグラフィカルなマスコンノッチ表示。情報パネルと重ならない位置に配置。
        notch_y = panel_y + info_h + 14
        self.draw_notch_graphic(c, panel_x, notch_y, 262, max(160, min(260, h - notch_y - 50)))

        audio_state = "音声: ON" if self.audio_proc is not None and self.audio_proc.is_alive() else "音声: OFF"
        c.create_text(18, h - 28, anchor="sw", text=f"{audio_state}    {self.status_text.get()}", fill="#d4d9e6", font=self.font_ui)

    def notch_text(self) -> str:
        if self.notch > 0:
            return f"P{self.notch}"
        if self.notch < 0:
            return f"B{-self.notch}"
        return "N"

    def draw_notch_graphic(self, c, x, y, w, h):
        """右側表示用のグラフィカルなマスコンノッチ表示。"""
        if h < 120:
            return

        c.create_rectangle(x, y, x + w, y + h, fill="#121823", outline="#3a4558", width=2)
        c.create_text(x + 12, y + 12, anchor="nw", text="マスコン", fill="#e8edf7", font=("Meiryo UI", 12))

        current = self.notch
        label = self.notch_text()
        if current > 0:
            label_col = "#ffb04a"
            mode_txt = "力行"
        elif current < 0:
            label_col = "#66bbff"
            mode_txt = "ブレーキ"
        else:
            label_col = "#e8edf7"
            mode_txt = "中立"

        c.create_text(x + w - 12, y + 12, anchor="ne", text=f"{label}  {mode_txt}", fill=label_col, font=("Meiryo UI", 17))

        # 左側に縦型ノッチレバー、右側にバーインジケータ。
        rail_x = x + 54
        top = y + 54
        bottom = y + h - 22
        c.create_line(rail_x, top, rail_x, bottom, fill="#667286", width=5, capstyle=tk.ROUND)

        # v67: ノッチ位置は上側がブレーキ、下側が力行。
        # B7..B1,N,P1..P5 の13段。
        slots = [-7, -6, -5, -4, -3, -2, -1, 0, 1, 2, 3, 4, 5]
        n = len(slots)
        step = (bottom - top) / max(1, n - 1)

        for i, val in enumerate(slots):
            yy = top + step * i
            is_cur = (val == current)
            if val > 0:
                col = "#ff9f3d"
                txt = f"P{val}"
            elif val < 0:
                col = "#57b7ff"
                txt = f"B{-val}"
            else:
                col = "#d6dbe6"
                txt = "N"

            tick_len = 16 if is_cur else 10
            c.create_line(rail_x - tick_len, yy, rail_x + tick_len, yy, fill=col if is_cur else "#738098", width=3 if is_cur else 2)
            c.create_text(rail_x - 28, yy, anchor="e", text=txt, fill=col if is_cur else "#9aa6bb", font=("Meiryo UI", 8))

            # 右側バー表示。現在段まで塗るのではなく、各ノッチを離散的に表示。
            bar_x1 = x + 96
            bar_x2 = x + w - 18
            bh = max(6, min(12, step * 0.48))
            fill = col if is_cur else ("#3b2a1a" if val > 0 else ("#1c3147" if val < 0 else "#323743"))
            outline = "#ffffff" if is_cur else "#2a3342"
            c.create_rectangle(bar_x1, yy - bh / 2, bar_x2, yy + bh / 2, fill=fill, outline=outline, width=2 if is_cur else 1)
            if is_cur:
                c.create_text((bar_x1 + bar_x2) / 2, yy, text=txt, fill="#ffffff", font=("Meiryo UI", 9))

        # レバーつまみ
        try:
            cur_i = slots.index(current)
        except ValueError:
            cur_i = slots.index(0)
        cy = top + step * cur_i
        c.create_oval(rail_x - 14, cy - 14, rail_x + 14, cy + 14, fill=label_col, outline="#ffffff", width=2)
        c.create_line(rail_x + 12, cy, x + 90, cy, fill=label_col, width=4, capstyle=tk.ROUND)

    def draw_speed_meter(self, c, x, y, r, speed, max_speed):
        c.create_text(x, y - r - 38, text="スピードメーター", fill="#e8edf7", font=("Meiryo UI", 14))
        c.create_oval(x - r, y - r, x + r, y + r, fill="#171c26", outline="#3a4558", width=3)
        start_deg = 220
        end_deg = -40
        span = start_deg - end_deg
        for i in range(0, 11):
            ratio = i / 10
            deg = math.radians(start_deg - span * ratio)
            rr1 = r * 0.82
            rr2 = r * 0.94
            x1 = x + rr1 * math.cos(deg)
            y1 = y - rr1 * math.sin(deg)
            x2 = x + rr2 * math.cos(deg)
            y2 = y - rr2 * math.sin(deg)
            c.create_line(x1, y1, x2, y2, fill="#9aa6bb", width=2)
            if i % 2 == 0:
                tx = x + r * 0.68 * math.cos(deg)
                ty = y - r * 0.68 * math.sin(deg)
                c.create_text(tx, ty, text=f"{max_speed * ratio:.0f}", fill="#b7c0d2", font=("Yu Gothic UI", 8))

        # v29: 矢印ではなく、単純な針線だけで現在速度を表示する。
        ratio = max(0.0, min(1.0, speed / max(1.0, max_speed)))
        deg = math.radians(start_deg - span * ratio)
        line_r1 = r * 0.10
        line_r2 = r * 0.82
        x1 = x + line_r1 * math.cos(deg)
        y1 = y - line_r1 * math.sin(deg)
        x2 = x + line_r2 * math.cos(deg)
        y2 = y - line_r2 * math.sin(deg)
        c.create_line(x1, y1, x2, y2, fill="#ffd45a", width=5, capstyle=tk.ROUND)
        c.create_oval(x - 8, y - 8, x + 8, y + 8, fill="#ffd45a", outline="")

        c.create_text(x, y + 45, text=f"{speed:5.1f}", fill="#ffffff", font=self.font_meter)
        c.create_text(x, y + 84, text="km/h", fill="#b7c0d2", font=("Meiryo UI", 12))

    def draw_power_bar(self, c, x, y, w, h, kw, scale):
        c.create_text(x, y - 24, anchor="w", text="疑似モーター電力", fill="#e8edf7", font=("Meiryo UI", 14))
        c.create_rectangle(x, y, x + w, y + h, fill="#171c26", outline="#3a4558", width=2)
        mid = x + w / 2
        c.create_line(mid, y, mid, y + h, fill="#778198", width=2)
        ratio = max(-1.0, min(1.0, kw / max(1.0, scale)))
        if ratio >= 0:
            c.create_rectangle(mid, y + 4, mid + (w / 2 - 4) * ratio, y + h - 4, fill="#ff9f3d", outline="")
            label = "力行"
        else:
            c.create_rectangle(mid + (w / 2 - 4) * ratio, y + 4, mid, y + h - 4, fill="#57b7ff", outline="")
            label = "回生/ブレーキ"
        c.create_text(x + w / 2, y + h / 2, text=f"{kw:+.1f} kW  {label}", fill="#ffffff", font=("Meiryo UI", 12))

    def draw_pattern_strip(self, c, x, y, w, h, active):
        c.create_text(x, y - 18, anchor="w", text="速度域PWMパターン", fill="#e8edf7", font=("Meiryo UI", 12))
        c.create_rectangle(x, y, x + w, y + h, fill="#151b25", outline="#3a4558", width=2)
        if not self.pattern_rows:
            c.create_text(x + w / 2, y + h / 2, text="パターン未設定", fill="#ffffff", font=self.font_ui)
            return
        max_v = max(1.0, min(300.0, max(r["vmax"] for r in self.pattern_rows if r["vmax"] < 999) if any(r["vmax"] < 999 for r in self.pattern_rows) else float(self.maxspeed_var.get())))
        prev = 0.0
        colors = {
            "ASYNC": "#5ea2ff",
            "SYNC": "#52d273",
            "CHM": "#c78dff",
            "SHE": "#ffcf5a",
            "WIDE3": "#ff8c42",
            "ONEPULSE": "#ff5c7a",
        }
        for row in self.pattern_rows:
            end = min(max_v, row["vmax"] if row["vmax"] < 999 else max_v)
            if end < prev:
                continue
            x1 = x + 5 + (w - 10) * (prev / max_v)
            x2 = x + 5 + (w - 10) * (end / max_v)
            col = colors.get(row["kind"], "#999999")
            outline = "#ffffff" if row is active else ""
            c.create_rectangle(x1, y + 22, max(x1 + 2, x2), y + 57, fill=col, outline=outline, width=2)
            if x2 - x1 > 30:
                c.create_text((x1 + x2) / 2, y + 40, text=row["kind"], fill="#0f1218", font=("Meiryo UI", 8))
            prev = end
        vpos = x + 5 + (w - 10) * max(0.0, min(1.0, self.speed_kmh / max_v))
        c.create_line(vpos, y + 18, vpos, y + 64, fill="#ffffff", width=3)
        c.create_text(x + 8, y + 74, anchor="w", text=f"現在: {active['name']} / {MODE_LABELS[active['kind']]}", fill="#ffffff", font=self.font_small)
        c.create_text(x + w - 8, y + 74, anchor="e", text=f"{self.speed_kmh:.1f} km/h", fill="#aeb7c8", font=self.font_small)

    def draw_hex_svpwm(self, c, cx, cy, r, phase, use_ratio, pseudo_kw, scale_kw, kind, params: dict):
        """PWMスイッチング波形を積分した磁束相当ベクトル軌跡を描く。

        参考サイトのベクトル波形は、PWM電圧を時間積分して
        電流0時の磁束軌跡のようなものとして評価している。
        v23では同じ考え方に合わせ、U/V/Wの実PWMスイッチ状態をClarke αβ電圧へ変換し、
        1電気周期ぶん積分してから閉曲線補正・正規化して表示する。
        高パルスでは円に近く、低パルス/1パルスでは多角形・六角形に近い軌跡になる。
        """
        outer = self.hex_points(cx, cy, r)
        c.create_polygon(outer, fill="#151b25", outline="#6f7d95", width=3)
        for rr in (0.25, 0.50, 0.75):
            pts = self.hex_points(cx, cy, r * rr)
            c.create_polygon(pts, fill="", outline="#2c3547", width=1)

        # 積分磁束の理想形は円に近いので、比較用の薄い円を描く。
        ref_rr = r * (0.18 + 0.74 * max(0.0, min(1.0, use_ratio)))
        c.create_oval(cx - ref_rr, cy - ref_rr, cx + ref_rr, cy + ref_rr, outline="#283347", width=1)

        mode_outline = {
            "ASYNC": "#6bb6ff",
            "SYNC": "#7dff9e",
            "CHM": "#c78dff",
            "SHE": "#ffd36a",
            "WIDE3": "#ff9f3d",
            "ONEPULSE": "#ff5c7a",
        }.get(kind, "#ffd36a")

        power_abs = max(0.0, min(1.0, abs(pseudo_kw) / max(1.0, scale_kw)))
        power_col = self.mix_color("#223049", "#ff9f3d" if pseudo_kw >= 0 else "#57b7ff", power_abs)

        trace = self.get_cached_space_vector_trace(params)
        if not trace or not bool(params.get("drive_active", True)):
            trace = [(0.0, 0.0)] * 6

        # v28: 現在位相/現在セクタの表示は不要との要望に合わせ、
        # 位相に連動する扇形ハイライトは描かない。軌跡面だけを表示する。

        def map_ab(alpha, beta):
            # αβ座標を画面用にHEX_DISPLAY_ROTだけ回転。βは上向き。
            cr = math.cos(HEX_DISPLAY_ROT)
            sr = math.sin(HEX_DISPLAY_ROT)
            xd = alpha * cr - beta * sr
            yd = alpha * sr + beta * cr
            return (cx + r * xd, cy - r * yd)

        pts = []
        for alpha, beta in trace:
            # 数値誤差や過変調風の簡易モデルで外へ出すぎないよう軽く制限。
            mag = math.hypot(alpha, beta)
            if mag > 1.08:
                alpha *= 1.08 / mag
                beta *= 1.08 / mag
            x, y = map_ab(alpha, beta)
            pts.extend([x, y])

        if len(pts) >= 6:
            fill = self.mix_color("#16233a", mode_outline, 0.34 if params.get("drive_active", True) else 0.08)
            c.create_polygon(pts, fill=fill, outline="")
            c.create_line(pts + pts[:2], fill=mode_outline, width=4 if params.get("drive_active", True) else 2, smooth=False)

        center_msg = "N: インバータOFF" if not params.get("drive_active", True) else MODE_LABELS.get(kind, kind)
        if params.get("transition_async", False):
            center_msg = "非同期導入"
        c.create_text(cx, cy, text=center_msg, fill="#e8edf7", font=("Yu Gothic UI", 14, "bold"))

        avg_note = "低パルス瞬時積分 / 高パルスSWリプル除去"
        c.create_text(
            cx, cy + r + 34,
            text=f"{MODE_LABELS.get(kind, kind)}   {avg_note}   電圧利用率 {use_ratio * 100:5.1f}%   疑似電力 {pseudo_kw:+.1f} kW",
            fill="#e8edf7", font=("Meiryo UI", 9)
        )

        # 二レベルインバータの6つの有効ベクトル。
        # v91: 長い U+ V- W- 表記は重なるため、短い相名表記にする。
        labels = ["U", "-W", "V", "-U", "W", "-V"]
        for (px2, py2), lab in zip(outer, labels):
            dx = px2 - cx
            dy = py2 - cy
            l = math.hypot(dx, dy) or 1
            c.create_text(px2 + 16 * dx / l, py2 + 16 * dy / l, text=lab, fill="#b9c4d8", font=("Meiryo UI", 9))

    def _trace_cache_key_from_params(self, params: dict):
        """ベクトル軌跡キャッシュ用のキー。

        elec_phaseなどの瞬時値は入れず、波形形状が変わる要素だけで判定する。
        """
        return (
            str(params.get("pwm_kind", "")),
            round(float(params.get("modulation", 0.0)), 3),
            round(float(params.get("f0", 0.0)), 2),
            round(float(params.get("pattern_value", 0.0)), 3),
            int(round(float(params.get("sync_pulses", 0.0)))),
            str(params.get("spread_mode", "")),
            round(float(params.get("spread_amount", 0.0)), 3),
            bool(params.get("drive_active", True)),
        )

    def get_cached_space_vector_trace(self, params: dict):
        """重いPWM積分ベクトル軌跡をキャッシュして返す。

        v48では毎描画ごとに約900点のPWM波形→Clarke→積分を計算していたため、
        SHE/CHMや反響ON時にGUIが重くなりやすかった。
        v49では形状が変わる条件だけをキーにし、約0.12秒ごとに再計算する。
        """
        now = time.perf_counter()
        key = self._trace_cache_key_from_params(params)
        if (
            self._trace_cache_key == key
            and self._trace_cache_value is not None
            and (now - self._trace_cache_time) < 0.12
        ):
            return self._trace_cache_value

        # サンプル数を削減。v73ではSHE/CHMを同じルート・同じ点数にする。
        kind = str(params.get("pwm_kind", "ASYNC")).upper()
        if kind in ("ONEPULSE", "WIDE3"):
            samples = 500
        elif kind in ("SHE", "CHM"):
            samples = 340
        else:
            samples = 380
        trace = self.pwm_space_vector_trace(params, samples=samples)
        self._trace_cache_key = key
        self._trace_cache_value = trace
        self._trace_cache_time = now
        return trace

    @staticmethod
    def circular_moving_average(values, win: int):
        n = len(values)
        if n == 0 or win <= 1:
            return list(values)
        win = max(1, min(int(win), max(1, n // 3)))
        if win % 2 == 0:
            win += 1
        half = win // 2
        ext = list(values[-half:]) + list(values) + list(values[:half])
        prefix = [0.0]
        for v in ext:
            prefix.append(prefix[-1] + v)
        out = []
        for i in range(n):
            out.append((prefix[i + win] - prefix[i]) / win)
        return out

    @staticmethod
    def switching_to_alpha_beta(vals):
        """U/V/WのPWM状態を正規化αβ空間ベクトルへ変換。

        通常のASYNC/SYNC/SHE/ONEPULSEは±1の二レベル脚状態として扱う。
        WIDE3 v32では、図の相間電圧を再現しつつ実際の脚状態に近い±1二値ゲートで返す。
        互換性のため0を含む値が来た場合だけ3値のClarke変換にフォールバックする。
        """
        vals_f = [float(vals[0]), float(vals[1]), float(vals[2])]
        if any(abs(v) < 0.25 for v in vals_f):
            u, v, w = vals_f
            alpha = (2.0 / 3.0) * (u - 0.5 * v - 0.5 * w)
            beta = (2.0 / 3.0) * ((math.sqrt(3.0) / 2.0) * (v - w))
            # ±1二レベル脚の有効ベクトル半径4/3を外枠1に合わせる係数。
            return 0.75 * alpha, 0.75 * beta

        su = 1.0 if vals_f[0] > 0.0 else 0.0
        sv = 1.0 if vals_f[1] > 0.0 else 0.0
        sw = 1.0 if vals_f[2] > 0.0 else 0.0
        alpha = (2.0 / 3.0) * (su - 0.5 * sv - 0.5 * sw)
        beta = (2.0 / 3.0) * ((math.sqrt(3.0) / 2.0) * (sv - sw))
        # 有効ベクトルの半径 2/3 を外枠半径1へ正規化。
        return 1.5 * alpha, 1.5 * beta

    @staticmethod
    def averaged_pole_to_alpha_beta(vals):
        """各相のPWM平均ポール電圧(-1..+1)をαβへ変換する。

        以前の表示では、瞬時の000〜111スイッチ状態をサンプルして円形移動平均していたため、
        キャリア周波数と描画サンプルの関係で歯車状・いびつな軌跡が出ることがあった。
        ここではキャリア1周期で平均した各相ポール電圧そのものをClarke変換する。
        ±1のスイッチ状態を入れた場合は外側六角形の有効ベクトル半径が1になる。
        """
        pu = max(-1.0, min(1.0, float(vals[0])))
        pv = max(-1.0, min(1.0, float(vals[1])))
        pw = max(-1.0, min(1.0, float(vals[2])))
        alpha = (2.0 / 3.0) * (pu - 0.5 * pv - 0.5 * pw)
        beta = (2.0 / 3.0) * ((math.sqrt(3.0) / 2.0) * (pv - pw))
        # ±1ポール電圧の有効ベクトル半径4/3を、外枠半径1へ正規化。
        return 0.75 * alpha, 0.75 * beta

    @staticmethod
    def _clip_ref(x: float) -> float:
        return max(-1.0, min(1.0, float(x)))

    def pwm_average_pole_values_at_theta(self, theta: float, kind: str, pulse_value: int, modulation: float):
        """描画用のPWM平均ポール電圧を返す。

        ASYNC/SYNC/CHM/WIDE3は三角キャリアPWMの1キャリア周期平均、
        SHE/ONEPULSEはプログラムドパルスの瞬時スイッチ状態として扱う。
        スイッチング周波数拡散は平均デューティを変えないため、ベクトル軌跡には反映しない。
        """
        kind = str(kind).upper()
        m = max(0.0, min(1.0, float(modulation)))

        if kind in ("SHE", "CHM", "WIDE3", "ONEPULSE"):
            if kind == "ONEPULSE":
                m = 1.0
            return [
                self.programmed_switch_scalar(theta, kind, pulse_value, m),
                self.programmed_switch_scalar(theta - TAU / 3.0, kind, pulse_value, m),
                self.programmed_switch_scalar(theta + TAU / 3.0, kind, pulse_value, m),
            ]

        def ref(th):
            if kind == "CHM":
                # 音声生成側と同じ高調波注入モデル。平均値として扱うので歪まず滑らかになる。
                return m * (
                    math.sin(th)
                    + 0.155 * math.sin(3.0 * th)
                    - 0.045 * math.sin(5.0 * th)
                    + 0.025 * math.sin(7.0 * th)
                )
            if kind == "WIDE3":
                mm = min(1.0, m * 1.15 + 0.05)
                return mm * math.sin(th)
            return m * math.sin(th)

        return [
            self._clip_ref(ref(theta)),
            self._clip_ref(ref(theta - TAU / 3.0)),
            self._clip_ref(ref(theta + TAU / 3.0)),
        ]

    @staticmethod
    def hf_scalar_wave(mode: str, phase: float) -> float:
        """固定オシロ用の高周波波形。"""
        mode = str(mode).upper()
        if mode == "SINE":
            return math.sin(phase)
        if mode == "TRI":
            return VVVFHexApp.triangle_scalar(phase)
        if mode in ("SQUARE", "CARRIER"):
            return 1.0 if math.sin(phase + (0.12 * math.sin(phase * 0.125) if mode == "CARRIER" else 0.0)) >= 0.0 else -1.0
        return 0.0

    @staticmethod
    def hfi_abc_scalar(mode: str, phase: float, amount: float, modulation: float):
        """固定オシロ用のPMSM高周波電圧注入。"""
        mode = str(mode).upper()
        m = max(0.0, min(1.0, float(modulation)))
        amt = max(0.0, min(0.45, float(amount)))
        inj_amp = min(0.32, amt * (0.75 + 1.20 * (1.0 - m)))

        if mode == "SINE":
            alpha = math.sin(phase)
            beta = math.cos(phase) * 0.72
        elif mode == "TRI":
            alpha = VVVFHexApp.triangle_scalar(phase)
            beta = VVVFHexApp.triangle_scalar(phase - math.pi / 2.0) * 0.72
        elif mode in ("SQUARE", "CARRIER"):
            alpha = VVVFHexApp.hf_scalar_wave(mode, phase)
            beta = VVVFHexApp.hf_scalar_wave(mode, phase - math.pi / 2.0) * 0.58
        else:
            return 0.0, 0.0, 0.0

        hu = inj_amp * alpha
        hv = inj_amp * (-0.5 * alpha + 0.8660254037844386 * beta)
        hw = inj_amp * (-0.5 * alpha - 0.8660254037844386 * beta)
        return hu, hv, hw

    def pwm_switch_samples(self, params: dict, samples: int, window_s: float, theta_start: float = 0.0, carrier_phase_start: float = 0.0):
        """指定した実時間窓でPWM脚状態と相間電圧を生成する。"""
        kind = str(params.get("pwm_kind", "ASYNC")).upper()
        modulation = max(0.0, min(1.0, float(params.get("modulation", 0.0))))
        f0 = max(0.0, float(params.get("f0", 1.0)))
        f0_eff = max(0.05, f0)
        value = float(params.get("pattern_value", 0.0))
        carrier = float(params.get("carrier", 1200.0))
        pulse_value = max(1, int(round(value or params.get("sync_pulses", 21))))

        if kind == "ASYNC":
            fc_base = max(20.0, value if value > 10.0 else carrier)
        elif kind == "WIDE3":
            pulse_value = 3
            fc_base = max(20.0, f0_eff * 3.0)
        elif kind == "ONEPULSE":
            pulse_value = 1
            fc_base = max(20.0, f0_eff)
            modulation = max(0.95, modulation)
        else:
            if kind in ("SHE", "CHM"):
                pulse_value = _ppwm_normalize_pulse_count(pulse_value)
            fc_base = max(20.0, f0_eff * pulse_value)

        spread_mode = str(params.get("spread_mode", "OFF")).upper()
        spread_amount = max(0.0, min(0.85, float(params.get("spread_amount", 0.0))))
        spread_rate = max(0.05, min(40.0, float(params.get("spread_rate", 3.0))))
        hf_mode = str(params.get("hf_mode", "OFF")).upper()
        hf_amount = max(0.0, min(0.45, float(params.get("hf_amount", 0.0))))
        hf_freq = max(20.0, min(2000.0, float(params.get("hf_freq", 750.0))))

        # v61: N惰行中などdrive_active=Falseでは、固定オシロの相間電圧も必ず0にする。
        if (not bool(params.get("drive_active", True))) or modulation <= 1e-9:
            samples = max(8, int(samples))
            return [[0.0, 0.0, 0.0] for _ in range(samples)], [[0.0] * samples, [0.0] * samples, [0.0] * samples], fc_base

        states = []
        line_waves = [[], [], []]
        carrier_phase = float(carrier_phase_start)
        last_t = 0.0
        samples = max(8, int(samples))
        window_s = max(0.001, float(window_s))
        for i in range(samples):
            t = window_s * i / max(1, samples - 1)
            dt = t - last_t if i > 0 else 0.0
            last_t = t
            theta = theta_start + TAU * f0 * t
            spread_phase = TAU * spread_rate * t
            sw_spread = self.spread_scalar(spread_phase, spread_mode) * spread_amount
            fc_inst = max(20.0, fc_base * (1.0 + sw_spread))

            if kind in ("SHE", "CHM", "WIDE3", "ONEPULSE"):
                theta_sw = theta
                # v73: SHE/CHMは同じスイッチング角方式なので、拡散も同じ扱いにする。
                if kind in ("SHE", "CHM") and spread_mode != "OFF" and spread_amount > 0.0001:
                    theta_sw = theta + sw_spread * 0.22
                vals = [
                    self.programmed_switch_scalar(theta_sw, kind, pulse_value, modulation),
                    self.programmed_switch_scalar(theta_sw - TAU / 3.0, kind, pulse_value, modulation),
                    self.programmed_switch_scalar(theta_sw + TAU / 3.0, kind, pulse_value, modulation),
                ]
            else:
                carrier_phase += TAU * fc_inst * dt
                sync_cat = (kind == "SYNC" and sync_cat_ear_required(pulse_value))
                if sync_cat:
                    # v83: 三相を同時に決め、ゼロベクトルノッチで相間電圧を0へ落とす。
                    vals = self.sync_cat_ear_states_scalar(theta, pulse_value, modulation)
                else:
                    tri = self.triangle_scalar(carrier_phase)

                    def ref(th):
                        if kind == "CHM":
                            return modulation * (
                                math.sin(th)
                                + 0.155 * math.sin(3.0 * th)
                                - 0.045 * math.sin(5.0 * th)
                                + 0.025 * math.sin(7.0 * th)
                            )
                        if kind == "WIDE3":
                            mm = min(1.0, modulation * 1.15 + 0.05)
                            return mm * math.sin(th)
                        return modulation * math.sin(th)

                    refs = [ref(theta), ref(theta - TAU / 3.0), ref(theta + TAU / 3.0)]

                    # v63: 固定オシロにもPMSM高周波重畳を反映。
                    if hf_mode != "OFF" and hf_amount > 0.0001:
                        hu, hv, hw = self.hfi_abc_scalar(hf_mode, TAU * hf_freq * t, hf_amount, modulation)
                        refs = [
                            max(-1.25, min(1.25, refs[0] + hu)),
                            max(-1.25, min(1.25, refs[1] + hv)),
                            max(-1.25, min(1.25, refs[2] + hw)),
                        ]

                    vals = [1.0 if r >= tri else -1.0 for r in refs]

            states.append(vals)
            line_vals = [
                (vals[0] - vals[1]) * 0.5,
                (vals[1] - vals[2]) * 0.5,
                (vals[2] - vals[0]) * 0.5,
            ]
            # v73: SHE/CHMの相間電圧表示は、どちらも脚状態差分そのものを表示する。
            for ch in range(3):
                line_waves[ch].append(line_vals[ch])
        return states, line_waves, fc_base

    def pwm_space_vector_trace(self, params: dict, samples: int = 900):
        """モータ磁束推定のαβ軌跡を返す。

        v74:
        表示ルートを以下に変更する。

            U/V/W PWM瞬時電圧
            → Clarke αβ
            → 搬送波周期またはスイッチング周期で移動平均
            → モータ時定数フィルタ
            → 積分
            → 磁束軌跡表示

        これにより、SHE-PWM/CHM-PWMのスイッチングリプルを
        モータ巻線のインダクタンスで平滑された磁束として表示できる。
        """
        if not bool(params.get("drive_active", True)):
            return [(0.0, 0.0)] * 12

        kind = str(params.get("pwm_kind", "ASYNC")).upper()
        f0 = max(0.0, float(params.get("f0", 0.0)))
        if f0 < 0.05:
            return [(0.0, 0.0)] * 12

        modulation = max(0.0, min(1.0, float(params.get("modulation", 0.0))))
        value = float(params.get("pattern_value", 0.0))
        carrier = float(params.get("carrier", 1200.0))
        pulse_value = max(1, int(round(value or params.get("sync_pulses", 21))))

        # 電気角1周期あたりのスイッチング比。
        if kind == "ASYNC":
            fc_est = max(20.0, value if value > 10.0 else carrier)
            carrier_ratio = fc_est / max(0.05, f0)
        elif kind == "WIDE3":
            pulse_value = 3
            carrier_ratio = 3.0
            fc_est = max(20.0, f0 * carrier_ratio)
        elif kind == "ONEPULSE":
            pulse_value = 1
            carrier_ratio = 1.0
            fc_est = max(20.0, f0)
            modulation = max(0.95, modulation)
        elif kind in ("SHE", "CHM"):
            pulse_value = _ppwm_normalize_pulse_count(pulse_value)
            carrier_ratio = float(max(1, pulse_value))
            fc_est = max(20.0, f0 * carrier_ratio)
        elif kind == "SYNC":
            carrier_ratio = float(max(1, pulse_value))
            fc_est = max(20.0, f0 * carrier_ratio)
        else:
            carrier_ratio = float(max(1, pulse_value))
            fc_est = max(20.0, f0 * carrier_ratio)

        # 瞬時PWMを一度高めの密度で作る。
        if kind == "ASYNC":
            points_per_carrier = 18 if carrier_ratio > 120.0 else 26
        elif kind == "ONEPULSE":
            points_per_carrier = 360
        elif kind == "WIDE3":
            points_per_carrier = 160
        elif kind in ("SHE", "CHM"):
            points_per_carrier = 96 if carrier_ratio <= 15 else 56
        elif kind == "SYNC":
            points_per_carrier = 126 if carrier_ratio <= 15 else 72
        else:
            points_per_carrier = 80

        n = int(max(1440, min(9000, carrier_ratio * points_per_carrier)))
        n = max(480, n)
        dtheta = TAU / n

        # 非同期PWMは1周期切り出しのキャリア位相で形が変わるため、初期位相平均。
        # v77:
        # 低パルスPWMを初期キャリア位相で平均すると、3パルスでも複数の切り出しを
        # 重ね合わせたようになり、磁束軌跡が不自然に円へ近づく。
        # 広域3パルスと同様、低パルスでは「そのPWM波形そのもの」を積分する。
        low_pulse_flux = (
            kind in ("ONEPULSE", "WIDE3")
            or (kind in ("SYNC", "SHE", "CHM") and carrier_ratio <= 9.5)
        )

        if low_pulse_flux:
            phase_count = 1
        elif kind == "ASYNC":
            # v89:
            # 初期キャリア位相平均を強くかけると、多パルス時の磁束軌跡が
            # 理想円に近づきすぎる。PWMらしい細かなリプルを残すため弱める。
            phase_count = 4 if carrier_ratio > 60.0 else 3
        elif kind == "SYNC":
            # 高パルス同期も実際は完全な円ではなく、パルス列による角ばりが残る。
            # ここで複数位相平均すると円になりすぎるため1にする。
            phase_count = 1
        else:
            phase_count = 1

        spread_mode = str(params.get("spread_mode", "OFF")).upper()
        spread_amount = max(0.0, min(0.85, float(params.get("spread_amount", 0.0))))
        spread_rate = max(0.05, min(40.0, float(params.get("spread_rate", 3.0))))
        spread_ratio = spread_rate / max(0.05, f0)

        def carrier_phase_for(theta: float, carrier_phase0: float, phase_index: int) -> float:
            base = carrier_ratio * theta + carrier_phase0
            if spread_mode == "OFF" or spread_amount <= 1e-6:
                return base

            sp0 = TAU * (phase_index / max(1, phase_count))
            if spread_mode == "SINE":
                k = max(1, int(round(spread_ratio)))
                return base - carrier_ratio * spread_amount * math.cos(k * theta + sp0) / max(1.0, k) * 0.18
            if spread_mode == "TRI":
                k = max(1, int(round(spread_ratio)))
                return base + carrier_ratio * spread_amount * self.triangle_scalar(k * theta + sp0) * 0.10
            if spread_mode == "STEP":
                k = max(1, int(round(spread_ratio)))
                seg = int(((k * theta + sp0) / TAU) % 1.0 * 6.0)
                step_val = (seg - 2.5) / 2.5
                return base + carrier_ratio * spread_amount * step_val * 0.08
            if spread_mode == "RANDOM":
                k = max(3, int(round(max(3.0, spread_ratio * 2.0))))
                segf = ((k * theta + sp0) / TAU) % 1.0 * 8.0
                seg = math.floor(segf)
                frac = segf - seg

                def rnd(j):
                    return 2.0 * ((math.sin((j + phase_index * 17) * 12.9898 + 78.233) * 43758.5453) % 1.0) - 1.0

                a = rnd(seg)
                b = rnd(seg + 1)
                sm = frac * frac * (3.0 - 2.0 * frac)
                return base + carrier_ratio * spread_amount * (a + (b - a) * sm) * 0.08
            return base

        def ref_value(th: float) -> float:
            if kind == "CHM":
                # CHMは波形生成式はSHEと同じだが、角度テーブル側が異なる。
                return modulation * (
                    math.sin(th)
                    + 0.155 * math.sin(3.0 * th)
                    - 0.045 * math.sin(5.0 * th)
                    + 0.025 * math.sin(7.0 * th)
                )
            if kind == "WIDE3":
                mm = min(1.0, modulation * 1.15 + 0.05)
                return mm * math.sin(th)
            return modulation * math.sin(th)

        def states_at_theta(theta: float, carrier_phase0: float, phase_index: int):
            if kind in ("SHE", "CHM", "WIDE3", "ONEPULSE"):
                theta_sw = theta
                if kind in ("SHE", "CHM") and spread_mode != "OFF" and spread_amount > 0.0001:
                    theta_sw = theta + spread_amount * 0.08 * self.spread_scalar(theta * 6.0 + carrier_phase0, spread_mode)
                return [
                    self.programmed_switch_scalar(theta_sw, kind, pulse_value, modulation),
                    self.programmed_switch_scalar(theta_sw - TAU / 3.0, kind, pulse_value, modulation),
                    self.programmed_switch_scalar(theta_sw + TAU / 3.0, kind, pulse_value, modulation),
                ]

            refs = [
                ref_value(theta),
                ref_value(theta - TAU / 3.0),
                ref_value(theta + TAU / 3.0),
            ]

            if kind == "SYNC" and sync_cat_ear_required(pulse_value):
                # v83: 低パルス特殊同期は、主ベクトル＋ゼロベクトルノッチで作る。
                # 相ごと独立ノッチでは相間電圧が逆向きへ飛ぶので使わない。
                return self.sync_cat_ear_states_scalar(theta, pulse_value, modulation)

            cph = carrier_phase_for(theta, carrier_phase0, phase_index)
            tri = self.triangle_scalar(cph)
            return [1.0 if r >= tri else -1.0 for r in refs]

        # 1) U/V/W PWM瞬時電圧 → Clarke αβ
        va = [0.0] * n
        vb = [0.0] * n
        for pidx in range(phase_count):
            cphase0 = 0.0 if phase_count == 1 else TAU * pidx / phase_count
            for i in range(n):
                theta = (i + 0.5) * dtheta
                vals = states_at_theta(theta, cphase0, pidx)
                a, b = self.switching_to_alpha_beta(vals)
                va[i] += a
                vb[i] += b

        inv_pc = 1.0 / max(1, phase_count)
        va = [x * inv_pc for x in va]
        vb = [x * inv_pc for x in vb]

        # 微小DCを除去。
        ma = sum(va) / n
        mb = sum(vb) / n
        va = [x - ma for x in va]
        vb = [x - mb for x in vb]

        # 2) 搬送波周期/スイッチング周期で移動平均。
        # 低パルス/1パルスは丸めすぎると本来の多角形性が消えるため弱くする。
        samples_per_switch = max(1.0, n / max(1.0, carrier_ratio))
        if low_pulse_flux:
            # 低パルスは瞬時電圧積分を優先。
            avg_win = 1
        elif kind in ("SHE", "CHM"):
            # v89:
            # 高パルスSHE/CHMでも完全な円にしない。
            # 1キャリア周期平均ではなく、半周期未満の軽い平均にしてリプルを残す。
            avg_win = max(1, int(samples_per_switch * 0.30))
        elif kind == "SYNC":
            avg_win = max(1, int(samples_per_switch * 0.28))
        elif kind == "ASYNC":
            avg_win = max(3, int(samples_per_switch * 0.55))
        else:
            avg_win = max(1, int(samples_per_switch * 0.35))

        if avg_win > 1:
            if avg_win % 2 == 0:
                avg_win += 1
            va = self.circular_moving_average(va, avg_win)
            vb = self.circular_moving_average(vb, avg_win)

        # 3) モータ時定数フィルタ。
        # 電気角グリッドを実時間に戻し、1次遅れを周期信号として前後方向にかける。
        def motor_lowpass_periodic(values, tau_s: float, passes: int = 2):
            nloc = len(values)
            if nloc == 0 or tau_s <= 1e-6:
                return list(values)

            dt_s = 1.0 / max(1e-6, f0 * nloc)
            alpha = dt_s / (tau_s + dt_s)
            alpha = max(0.0001, min(0.65, alpha))
            out = list(values)

            for _ in range(max(1, passes)):
                # 周期境界の過渡を消すため、数周回して状態をなじませる。
                y = sum(out) / nloc
                for _warm in range(3):
                    for x in out:
                        y += alpha * (x - y)

                fwd = []
                for x in out:
                    y += alpha * (x - y)
                    fwd.append(y)

                # 位相遅れを抑えるため逆方向にも同じフィルタをかける。
                y = sum(fwd) / nloc
                for _warm in range(3):
                    for x in reversed(fwd):
                        y += alpha * (x - y)

                rev = [0.0] * nloc
                for idx_rev in range(nloc - 1, -1, -1):
                    y += alpha * (fwd[idx_rev] - y)
                    rev[idx_rev] = y
                out = rev
            return out

        # v75:
        # v74の時定数は強すぎ、1パルスやSHE/CHMの低次高調波まで消してしまい、
        # 1パルスまで完全な円に近く見える原因になっていた。
        #
        # ここでは「モータ時定数フィルタ」はPWMキャリアリプルを弱く落とす用途に限定する。
        # 1パルスはキャリアが無いためフィルタ無し。
        # SHE/CHM/SYNCでは、低次高調波を残すためカットオフを 4.5*f0 以上に置く。
        if low_pulse_flux:
            # 低パルスでは、広域3パルスと同じく瞬時電圧積分を優先。
            tau_s = 0.0
            passes = 0
        elif kind in ("SHE", "CHM"):
            # v89:
            # カットオフを従来より上げて、キャリア成分を完全には消さない。
            # これで多パルス時もわずかな角ばり・リプルが残る。
            cutoff_hz = max(7.0 * f0, 0.78 * fc_est)
            tau_s = 1.0 / (TAU * max(180.0, cutoff_hz))
            tau_s = max(0.00008, min(0.00075, tau_s))
            passes = 1
        elif kind == "SYNC":
            cutoff_hz = max(6.5 * f0, 0.72 * fc_est)
            tau_s = 1.0 / (TAU * max(180.0, cutoff_hz))
            tau_s = max(0.00008, min(0.00085, tau_s))
            passes = 1
        elif kind == "ASYNC":
            cutoff_hz = max(5.0 * f0, 0.62 * fc_est)
            tau_s = 1.0 / (TAU * max(220.0, cutoff_hz))
            tau_s = max(0.00006, min(0.00090, tau_s))
            passes = 1
        else:
            cutoff_hz = max(5.5 * f0, 0.65 * fc_est)
            tau_s = 1.0 / (TAU * max(180.0, cutoff_hz))
            tau_s = max(0.00008, min(0.00090, tau_s))
            passes = 1

        if passes > 0 and tau_s > 0.0:
            va = motor_lowpass_periodic(va, tau_s, passes=passes)
            vb = motor_lowpass_periodic(vb, tau_s, passes=passes)

        # フィルタ後のDCを再除去。
        ma = sum(va) / n
        mb = sum(vb) / n
        va = [x - ma for x in va]
        vb = [x - mb for x in vb]

        # 4) 積分して磁束軌跡へ。
        flux = []
        ia = 0.0
        ib = 0.0
        for i in range(n):
            flux.append((ia, ib))
            ia += va[i] * dtheta
            ib += vb[i] * dtheta

        # 5) 1周期の端点ドリフトだけ補正。
        end_a = ia
        end_b = ib
        denom = max(1, n - 1)
        closed = []
        for i, (a, b) in enumerate(flux):
            t = i / denom
            closed.append((a - end_a * t, b - end_b * t))

        ca = sum(p[0] for p in closed) / n
        cb = sum(p[1] for p in closed) / n
        centered = [(a - ca, b - cb) for a, b in closed]

        # 表示上の微小な階段だけ軽く消す。
        post_win = 1
        if low_pulse_flux:
            post_win = 1
        elif kind == "ASYNC":
            post_win = max(1, int(n / 900))
        elif kind in ("SYNC", "SHE", "CHM") and carrier_ratio >= 9:
            # v89: 後段平滑でも円に寄りすぎないようかなり弱める。
            post_win = max(1, int(n / 1800))
        if post_win > 1:
            if post_win % 2 == 0:
                post_win += 1
            aa = self.circular_moving_average([p[0] for p in centered], post_win)
            bb = self.circular_moving_average([p[1] for p in centered], post_win)
            centered = list(zip(aa, bb))

        mags = sorted(math.hypot(a, b) for a, b in centered)
        if not mags or mags[-1] < 1e-12:
            return [(0.0, 0.0)] * 12

        idx = min(len(mags) - 1, max(0, int(len(mags) * 0.97)))
        norm_mag = max(mags[idx], mags[-1] * 0.65, 1e-12)

        abs_mod = max(0.0, min(1.0, float(params.get("modulation", 0.0))))
        display_radius = 0.08 + 0.86 * (abs_mod ** 0.92)
        if kind == "ONEPULSE":
            display_radius = 0.94
        elif kind == "WIDE3":
            display_radius = max(display_radius, 0.52 + 0.38 * abs_mod)
        elif kind in ("SYNC", "SHE", "CHM") and carrier_ratio <= 9:
            display_radius = max(display_radius, 0.18 + 0.58 * abs_mod)

        scaled = []
        for a, b in centered:
            aa = a / norm_mag * display_radius
            bb = b / norm_mag * display_radius
            mag = math.hypot(aa, bb)
            if mag > 1.04:
                aa *= 1.04 / mag
                bb *= 1.04 / mag
            scaled.append((aa, bb))

        target = 600 if kind in ("ONEPULSE", "WIDE3") else 560
        step = max(1, len(scaled) // target)
        out = scaled[::step]
        if len(out) < 6:
            out = scaled
        return out

    def pwm_space_vector_trace_she_line(self, params: dict, samples: int = 900):
        """SHE専用のベクトル軌跡計算。

        v54:
        v53のSHEオシロ波形は、相間電圧のパルス数と細い逆向きパルス補正を
        反映している。一方、ベクトル軌跡は従来通り相脚U/V/Wの瞬時状態を
        直接Clarke変換していたため、オシロに表示される相間電圧と
        ベクトル軌跡の元波形がズレ、内側にループ状の歪みが出ていた。

        ここではSHEだけ、
          U/V/W脚状態 → UV/VW/WU相間電圧
          → オシロ表示と同じSHE相間極性補正
          → 相電圧再構成 → αβ電圧
          → 1パルスピッチ程度で平均 → 積分
        の順に計算する。
        これにより、PWM波形基準を維持しながら、表示上の不自然な内側ループを抑える。
        """
        if not bool(params.get("drive_active", True)):
            return [(0.0, 0.0)] * 12

        f0 = max(0.0, float(params.get("f0", 0.0)))
        if f0 < 0.05:
            return [(0.0, 0.0)] * 12

        modulation = max(0.0, min(1.0, float(params.get("modulation", 0.0))))
        value = float(params.get("pattern_value", 0.0))
        pulse_value = max(1, int(round(value or params.get("sync_pulses", 7))))
        line_pulses = max(1, int(round(pulse_value)))

        # 低パルスでは形状保持のため多め、高パルスでは負荷を抑える。
        n = int(max(720, min(4200, max(samples, line_pulses * 120))))
        dtheta = TAU / n

        va = [0.0] * n
        vb = [0.0] * n
        rt3 = math.sqrt(3.0)

        for i in range(n):
            theta = (i + 0.5) * dtheta

            # v53のSHE相脚波形を使う。相脚は2レベルのまま。
            pu = self.programmed_switch_scalar(theta, "SHE", pulse_value, modulation)
            pv = self.programmed_switch_scalar(theta - TAU / 3.0, "SHE", pulse_value, modulation)
            pw = self.programmed_switch_scalar(theta + TAU / 3.0, "SHE", pulse_value, modulation)

            # 相間電圧。オシロ側と同じ正規化。
            uv = (pu - pv) * 0.5
            vw = (pv - pw) * 0.5
            wu = (pw - pu) * 0.5

            # v48/v53と同じ、SHE相間電圧の細い逆向きパルス補正。
            uv = she_line_polarity_scalar(uv, theta + math.pi / 6.0)
            vw = she_line_polarity_scalar(vw, theta - math.pi / 2.0)
            wu = she_line_polarity_scalar(wu, theta + 5.0 * math.pi / 6.0)

            # 補正後の相間電圧から、ゼロ和の相電圧へ戻す。
            # uv = u-v, vw = v-w, wu = w-u を満たす最小二乗再構成。
            # uv+vw+wu が数値的に0から少し外れても破綻しにくい形。
            u = (uv - wu) / 3.0
            v = (vw - uv) / 3.0
            w = (wu - vw) / 3.0

            # Clarke αβ。表示半径は後段で正規化する。
            va[i] = (2.0 / 3.0) * (u - 0.5 * v - 0.5 * w)
            vb[i] = (2.0 / 3.0) * ((rt3 / 2.0) * (v - w))

        # DC偏りを除去。
        ma = sum(va) / n
        mb = sum(vb) / n
        va = [x - ma for x in va]
        vb = [x - mb for x in vb]

        # SHEは瞬時エッジをそのまま積分すると小さな内側ループが出やすい。
        # パルスピッチの約0.55倍で平均し、パルス列由来の外形は残しつつエッジループだけ抑える。
        samples_per_pulse = n / max(1.0, line_pulses * 2.0)
        smooth_win = max(3, int(samples_per_pulse * 0.55))
        if smooth_win % 2 == 0:
            smooth_win += 1
        smooth_win = min(smooth_win, max(3, n // 16))
        if smooth_win > 1:
            va = self.circular_moving_average(va, smooth_win)
            vb = self.circular_moving_average(vb, smooth_win)

        # 電気角で積分。
        flux = []
        ia = 0.0
        ib = 0.0
        for i in range(n):
            flux.append((ia, ib))
            ia += va[i] * dtheta
            ib += vb[i] * dtheta

        # 閉曲線補正。
        end_a = ia
        end_b = ib
        denom = max(1, n - 1)
        closed = []
        for i, (a, b) in enumerate(flux):
            t = i / denom
            closed.append((a - end_a * t, b - end_b * t))

        ca = sum(p[0] for p in closed) / n
        cb = sum(p[1] for p in closed) / n
        centered = [(a - ca, b - cb) for a, b in closed]

        # さらにごく弱く表示用平滑。パルス数が多い時だけ効かせる。
        post_win = max(1, int(n / max(480, line_pulses * 80)))
        if post_win > 1:
            if post_win % 2 == 0:
                post_win += 1
            aa = self.circular_moving_average([p[0] for p in centered], post_win)
            bb = self.circular_moving_average([p[1] for p in centered], post_win)
            centered = list(zip(aa, bb))

        mags = sorted(math.hypot(a, b) for a, b in centered)
        if not mags or mags[-1] < 1e-12:
            return [(0.0, 0.0)] * 12
        idx = min(len(mags) - 1, max(0, int(len(mags) * 0.97)))
        norm_mag = max(mags[idx], mags[-1] * 0.65, 1e-12)

        abs_mod = max(0.0, min(1.0, float(params.get("modulation", 0.0))))
        display_radius = 0.08 + 0.86 * (abs_mod ** 0.92)

        scaled = []
        for a, b in centered:
            aa = a / norm_mag * display_radius
            bb = b / norm_mag * display_radius
            mag = math.hypot(aa, bb)
            if mag > 1.04:
                aa *= 1.04 / mag
                bb *= 1.04 / mag
            scaled.append((aa, bb))

        target = 560
        step = max(1, len(scaled) // target)
        out = scaled[::step]
        if len(out) < 6:
            out = scaled
        return out

    @staticmethod
    def triangle_scalar(phase: float) -> float:
        frac = (phase / TAU) % 1.0
        return 2.0 * abs(2.0 * frac - 1.0) - 1.0

    @staticmethod
    def cat_ear_carrier_scalar(phase: float) -> float:
        """同期5/12パルス等で使う猫耳キャリア近似。互換用。"""
        frac = (phase / TAU) % 1.0
        tri = 2.0 * abs(2.0 * frac - 1.0) - 1.0
        d_top = min(frac, 1.0 - frac)
        d_bot = abs(frac - 0.5)
        ear_w = 0.135
        top = max(0.0, min(1.0, 1.0 - d_top / ear_w))
        bot = max(0.0, min(1.0, 1.0 - d_bot / ear_w))
        top = top * top * (3.0 - 2.0 * top)
        bot = bot * bot * (3.0 - 2.0 * bot)
        cat = tri - 0.42 * top + 0.42 * bot
        return max(-1.0, min(1.0, cat))

    @staticmethod
    def sync_cat_ear_switch_scalar(theta: float, pulse_value: int, modulation: float) -> float:
        """同期5パルス等の猫耳キャリア相当を半波対称ノッチ列で直接生成。"""
        p = max(1, int(round(float(pulse_value))))
        # v82: 同期5パルスの相電圧は2ノッチ/半波。相間電圧で5パルス相当になる。
        notch_count = max(1, p // 2)
        x = theta % TAU
        half = x % math.pi
        sign = 1.0 if x < math.pi else -1.0
        m = max(0.0, min(1.0, float(modulation)))
        base_half_width = (0.018 + 0.038 * (1.0 - m)) * math.pi
        scale = min(1.0, 5.0 / max(5.0, float(p)))
        width = base_half_width * scale

        for k in range(notch_count):
            center = math.pi * (k + 1) / (notch_count + 1)
            if abs(half - center) < width:
                return -sign
        return sign

    @staticmethod
    def sync_cat_ear_states_scalar(theta: float, pulse_value: int, modulation: float):
        """(3+6n)以外の同期PWMを三相状態として生成する。

        3/5/7パルスなど低パルス・奇数特殊同期は猫耳ノッチ、12パルス等の偶数特殊同期は相ごとの位相同期三角キャリア比較。
        """
        p = max(1, int(round(float(pulse_value))))
        m = max(0.0, min(1.0, float(modulation)))

        def tri(phase: float) -> float:
            frac = (phase / TAU) % 1.0
            return 2.0 * abs(2.0 * frac - 1.0) - 1.0

        if p % 2 == 1:
            def phase_gate(phi: float) -> float:
                x = phi % TAU
                sign = 1.0 if x < math.pi else -1.0

                notch_count = max(1, (p - 1) // 2)
                step = math.radians(60.0 / notch_count)
                center0 = -0.5 * step * (notch_count - 1)
                offsets = [center0 + step * k for k in range(notch_count)]

                width = (0.010 + 0.022 * (1.0 - m)) * math.pi
                if p > 5:
                    width *= 5.0 / float(p)
                width = max(math.radians(1.5), min(math.radians(7.5), width))

                for off in offsets:
                    c_pos = math.pi / 2.0 + off
                    c_neg = 3.0 * math.pi / 2.0 + off
                    if abs(x - c_pos) < width or abs(x - c_neg) < width:
                        return -sign
                return sign

            return [
                phase_gate(theta),
                phase_gate(theta - TAU / 3.0),
                phase_gate(theta + TAU / 3.0),
            ]

        # p=12などの偶数特殊同期: 三相合同性を保つため、キャリアも各相の基本波位相へ同期させる。
        th_u = theta
        th_v = theta - TAU / 3.0
        th_w = theta + TAU / 3.0
        return [
            1.0 if (m * math.sin(th_u)) >= tri(p * th_u) else -1.0,
            1.0 if (m * math.sin(th_v)) >= tri(p * th_v) else -1.0,
            1.0 if (m * math.sin(th_w)) >= tri(p * th_w) else -1.0,
        ]


    @staticmethod
    def spread_scalar(phase: float, mode: str) -> float:
        """固定オシロ表示用のスイッチング周波数拡散波形。"""
        mode = str(mode).upper()
        if mode == "SINE":
            return math.sin(phase)
        if mode == "TRI":
            return VVVFHexApp.triangle_scalar(phase)
        if mode == "STEP":
            frac = (phase / TAU) % 1.0
            return math.floor(frac * 5.0) / 2.0 - 1.0
        if mode == "RANDOM":
            # 画面が毎フレームちらつかないよう、決定論的な疑似ランダム値を段階補間する。
            seg = math.floor((phase / TAU) * 7.0)
            frac = (phase / TAU) * 7.0 - seg
            def rnd(k):
                return 2.0 * ((math.sin(k * 12.9898 + 78.233) * 43758.5453) % 1.0) - 1.0
            a = rnd(seg)
            b = rnd(seg + 1)
            smooth = frac * frac * (3.0 - 2.0 * frac)
            return a + (b - a) * smooth
        return 0.0

    @staticmethod
    def programmed_switch_scalar(theta: float, kind: str, pulse_value: int, modulation: float) -> float:
        if kind == "ONEPULSE":
            return 1.0 if math.sin(theta) >= 0.0 else -1.0

        if kind == "WIDE3":
            # v34: 広域3パルスはv27へ完全に戻す。
            # 各相のゲート波形を「主パルス＋両端の補助短パルス」にする。
            # 変調率100%では補助幅θ=0となり、通常の1パルスへ連続移行する。
            x = theta % TAU
            m = max(0.0, min(1.0, float(modulation)))
            theta_w = math.radians(38.0) * ((1.0 - m) ** 0.72)
            main = (theta_w <= x < (math.pi - theta_w))
            aux_before = (x >= TAU - theta_w)
            aux_after = (math.pi <= x < math.pi + theta_w)
            gate = main or aux_before or aux_after
            return 1.0 if gate else -1.0

        m = max(0.0, min(1.0, float(modulation)))
        # v73: SHE/CHMは同じ2レベル・スイッチング角方式に統一。
        # 違いは角度テーブルの目的関数だけにし、波形生成式は完全に同じにする。
        angles = list(ppwm_programmed_angles(kind, pulse_value, m))
        polarity = _ppwm_polarity(len(angles))
        x = theta % TAU
        half = x % math.pi
        q = half if half <= math.pi / 2 else math.pi - half
        sign = 1.0 if x < math.pi else -1.0
        state = 1.0
        for a in angles:
            if q >= a:
                state = -state
        return polarity * sign * state

    def pwm_voltage_samples(self, params: dict, samples: int = 700):
        """固定時間軸の三相PWM相間電圧パルスを生成する。

        v51:
        ユーザー指定により、PWMオシロ波形はv48相当に戻す。
        キャッシュせず、サンプル数も700へ戻す。
        """
        f0 = max(0.0, float(params.get("f0", 1.0)))
        window_ms = max(5.0, min(200.0, float(params.get("scope_window_ms", 50.0))))
        window_s = window_ms / 1000.0
        # 画面の見た目を安定させるため、電気角0°でトリガした固定時間窓として描く。
        states, waves, fc = self.pwm_switch_samples(params, samples=samples, window_s=window_s, theta_start=0.0)
        xs = [i / max(1, samples - 1) for i in range(samples)]
        carrier_ratio = fc / max(0.2, f0) if f0 > 0.0 else 0.0
        return xs, waves, fc, carrier_ratio, window_ms

    def draw_pwm_voltage_waves(self, c, x, y, w, h, params: dict):
        kind = str(params.get("pwm_kind", "ASYNC")).upper()
        c.create_text(x, y - 18, anchor="w", text=f"相間電圧波形（PWMパルス・固定時間軸） / {MODE_LABELS.get(kind, kind)}", fill="#e8edf7", font=("Meiryo UI", 10))
        c.create_rectangle(x, y, x + w, y + h, fill="#151b25", outline="#3a4558", width=2)
        xs, waves, fc, carrier_ratio, window_ms = self.pwm_voltage_samples(params)

        # 固定時間軸のグリッド。
        grid_n = 5
        for gi in range(grid_n + 1):
            gx = x + 52 + (w - 66) * gi / grid_n
            c.create_line(gx, y + 5, gx, y + h - 5, fill="#252e3e")
            c.create_text(gx, y + h - 22, text=f"{window_ms * gi / grid_n:.0f}ms", fill="#667287", font=("Yu Gothic UI", 8))

        # 相間電圧を縦に分けて、オシロのCH1/CH2/CH3のように表示する。
        colors = ["#ff6b6b", "#6bff95", "#6bb6ff"]
        names = ["UV相間", "VW相間", "WU相間"]
        band_h = h / 3.0
        for ch, (col, name) in enumerate(zip(colors, names)):
            cy = y + band_h * (ch + 0.5)
            amp = band_h * 0.33
            c.create_line(x + 45, cy, x + w - 8, cy, fill="#2c3547")
            c.create_text(x + 8, cy, anchor="w", text=name, fill=col, font=("Meiryo UI", 9))
            pts = []
            prev_x = None
            prev_y = None
            for i, val in enumerate(waves[ch]):
                xx = x + 52 + (w - 66) * xs[i]
                yy = cy - val * amp
                if i == 0:
                    pts.extend([xx, yy])
                else:
                    # ステップ波形として縦エッジも見えるようにする。
                    pts.extend([xx, prev_y, xx, yy])
                prev_x, prev_y = xx, yy
            c.create_line(pts, fill=col, width=1.6)

        c.create_text(
            x + w - 10, y + h - 8, anchor="se",
            text=f"時間軸固定 {window_ms:.0f}ms  相間電圧  PWM≈{fc:.0f}Hz  carrier/f0={carrier_ratio:.1f}",
            fill="#aeb7c8", font=self.font_small,
        )

    def draw_info_panel(self, c, x, y, w, h, items: dict):
        c.create_rectangle(x, y, x + w, y + h, fill="#151b25", outline="#3a4558", width=2)
        c.create_text(x + 12, y + 10, anchor="nw", text="運転情報", fill="#e8edf7", font=("Meiryo UI", 12))
        yy = y + 35
        row_step = 15
        max_y = y + h - 10
        for k, v in items.items():
            if yy > max_y:
                break
            vv = str(v)
            if len(vv) > 22:
                vv = vv[:21] + "…"
            c.create_text(x + 14, yy, anchor="w", text=k, fill="#9eabc0", font=self.font_canvas_small)
            # v90: 右側だけConsolasだったため日本語が浮いて見えた。左側と同じ日本語フォントに統一。
            c.create_text(x + w - 12, yy, anchor="e", text=vv, fill="#ffffff", font=self.font_canvas_small)
            yy += row_step

    @staticmethod
    def hex_points(cx, cy, r):
        pts = []
        for i in range(6):
            a = TAU * i / 6.0 + HEX_DISPLAY_ROT
            pts.append((cx + r * math.cos(a), cy - r * math.sin(a)))
        return pts

    @staticmethod
    def hex_sector(phase):
        sector_float = (phase % TAU) / (TAU / 6.0)
        if not math.isfinite(sector_float):
            sector_float = 0.0
        return int(math.floor(sector_float)) % 6 + 1

    @staticmethod
    def mix_color(c1: str, c2: str, t: float) -> str:
        t = max(0.0, min(1.0, t))
        def parse(s):
            s = s.lstrip("#")
            return int(s[0:2], 16), int(s[2:4], 16), int(s[4:6], 16)
        r1, g1, b1 = parse(c1)
        r2, g2, b2 = parse(c2)
        r = int(r1 + (r2 - r1) * t)
        g = int(g1 + (g2 - g1) * t)
        b = int(b1 + (b2 - b1) * t)
        return f"#{r:02x}{g:02x}{b:02x}"

    def on_close(self):
        self.kill_audio()
        self._global_poll_running = False
        self.root.destroy()


def main():
    root = tk.Tk()
    VVVFHexApp(root)
    root.mainloop()


if __name__ == "__main__":
    mp.freeze_support()
    main()
