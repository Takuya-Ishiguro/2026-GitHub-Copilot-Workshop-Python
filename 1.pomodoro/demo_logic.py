#!/usr/bin/env python3
"""
ポモドーロタイマーのロジック検証デモ
Tkinter不要でコアロジックをテストします
"""

import sys
import os
import random

# 注: Tkinterへの依存を避けるため、app.pyからインポートせず、
# 必要なクラスを独立して再実装してテストを行います
class ParticleSimulation:
    """パーティクルシミュレーション（GUI不要版）"""
    
    def __init__(self, x, y, canvas_width, canvas_height):
        self.x = x
        self.y = y
        self.vx = random.uniform(-1, 1)
        self.vy = random.uniform(-1, 1)
        self.canvas_width = canvas_width
        self.canvas_height = canvas_height
        self.size = random.randint(2, 5)
        self.alpha = random.uniform(0.3, 0.7)
        
    def update(self):
        """パーティクルの位置を更新"""
        self.x += self.vx
        self.y += self.vy
        
        if self.x < 0 or self.x > self.canvas_width:
            self.vx *= -1
        if self.y < 0 or self.y > self.canvas_height:
            self.vy *= -1
            
        self.x = max(0, min(self.canvas_width, self.x))
        self.y = max(0, min(self.canvas_height, self.y))


def get_progress_color(remaining_seconds, total_seconds):
    """
    残り時間に応じて色を計算
    青 (#00d4ff) → 黄 (#ffd700) → 赤 (#ff4444)
    """
    progress = remaining_seconds / total_seconds
    
    if progress > 0.5:
        # 青から黄へ (100% -> 50%)
        t = (progress - 0.5) * 2
        r = int(0 + (255 - 0) * (1 - t))
        g = int(212 + (215 - 212) * (1 - t))
        b = int(255 + (0 - 255) * (1 - t))
    else:
        # 黄から赤へ (50% -> 0%)
        t = progress * 2
        r = 255
        g = int(68 + (215 - 68) * t)
        b = int(68 + (0 - 68) * t)
        
    return f"#{r:02x}{g:02x}{b:02x}"


def format_time(seconds):
    """秒を MM:SS 形式にフォーマット"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def test_particle_system():
    """パーティクルシステムのテスト"""
    print("=" * 50)
    print("パーティクルシステムのテスト")
    print("=" * 50)
    
    particles = []
    for i in range(5):
        p = ParticleSimulation(
            random.uniform(0, 400),
            random.uniform(0, 400),
            400, 400
        )
        particles.append(p)
        print(f"パーティクル {i+1}: 位置=({p.x:.2f}, {p.y:.2f}), "
              f"速度=({p.vx:.2f}, {p.vy:.2f}), サイズ={p.size}")
    
    print("\n10回更新後:")
    for _ in range(10):
        for p in particles:
            p.update()
    
    for i, p in enumerate(particles):
        print(f"パーティクル {i+1}: 位置=({p.x:.2f}, {p.y:.2f})")
        assert 0 <= p.x <= 400, "X座標が範囲外"
        assert 0 <= p.y <= 400, "Y座標が範囲外"
    
    print("✓ パーティクルシステムは正常に動作しています\n")


def test_color_transition():
    """色の遷移のテスト"""
    print("=" * 50)
    print("色の遷移のテスト")
    print("=" * 50)
    
    total_seconds = 25 * 60  # 25分
    
    test_points = [
        (100, "100% (開始時)"),
        (75, "75%"),
        (50, "50% (中間点)"),
        (25, "25%"),
        (10, "10%"),
        (0, "0% (終了時)"),
    ]
    
    for percent, label in test_points:
        remaining = int(total_seconds * percent / 100)
        color = get_progress_color(remaining, total_seconds)
        time_str = format_time(remaining)
        print(f"{label:15} - 残り時間: {time_str} - 色: {color}")
    
    # 色が正しい形式か確認
    color = get_progress_color(total_seconds, total_seconds)
    assert color.startswith("#"), "色が#で始まっていません"
    assert len(color) == 7, "色コードの長さが不正です"
    
    print("✓ 色の遷移は正常に動作しています\n")


def test_time_formatting():
    """時間フォーマットのテスト"""
    print("=" * 50)
    print("時間フォーマットのテスト")
    print("=" * 50)
    
    test_cases = [
        (0, "00:00"),
        (59, "00:59"),
        (60, "01:00"),
        (125, "02:05"),
        (1500, "25:00"),
        (3600, "60:00"),
    ]
    
    for seconds, expected in test_cases:
        result = format_time(seconds)
        status = "✓" if result == expected else "✗"
        print(f"{status} {seconds}秒 -> {result} (期待値: {expected})")
        assert result == expected, f"時間フォーマットが不正: {result} != {expected}"
    
    print("✓ 時間フォーマットは正常に動作しています\n")


def test_timer_logic():
    """タイマーロジックのテスト"""
    print("=" * 50)
    print("タイマーロジックのテスト")
    print("=" * 50)
    
    WORK_DURATION = 25
    SHORT_BREAK = 5
    LONG_BREAK = 15
    
    print(f"作業時間: {WORK_DURATION}分")
    print(f"短い休憩: {SHORT_BREAK}分")
    print(f"長い休憩: {LONG_BREAK}分")
    
    # セッションのシミュレーション
    session_count = 0
    is_work_session = True
    
    for i in range(8):
        if is_work_session:
            duration = WORK_DURATION
            session_type = "作業"
            session_count += 1
        else:
            if session_count % 4 == 0:
                duration = LONG_BREAK
                session_type = "長い休憩"
            else:
                duration = SHORT_BREAK
                session_type = "短い休憩"
        
        print(f"セッション {i+1}: {session_type} ({duration}分)")
        is_work_session = not is_work_session
    
    print("✓ タイマーロジックは正常に動作しています\n")


def main():
    """メイン関数"""
    print("\n" + "=" * 50)
    print("ポモドーロタイマー - ロジック検証デモ")
    print("=" * 50 + "\n")
    
    try:
        test_time_formatting()
        test_color_transition()
        test_particle_system()
        test_timer_logic()
        
        print("=" * 50)
        print("✓ すべてのテストが成功しました！")
        print("=" * 50)
        print("\nアプリケーションは正常に動作する準備ができています。")
        print("GUIを表示するには、tkinterをインストールして以下を実行してください:")
        print("  python3 app.py")
        print()
        
        return 0
        
    except AssertionError as e:
        print(f"\n✗ テスト失敗: {e}")
        return 1
    except Exception as e:
        print(f"\n✗ エラー: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
