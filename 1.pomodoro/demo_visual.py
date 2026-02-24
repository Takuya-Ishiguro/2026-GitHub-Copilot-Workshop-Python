#!/usr/bin/env python3
"""
ポモドーロタイマーのビジュアルデモンストレーション
ASCII アートで円形プログレスバーと色の変化を表現
"""

import math


def get_progress_color_name(remaining_seconds, total_seconds):
    """色名を取得"""
    progress = remaining_seconds / total_seconds
    
    if progress > 0.66:
        return "青"
    elif progress > 0.33:
        return "黄"
    else:
        return "赤"


def format_time(seconds):
    """秒を MM:SS 形式にフォーマット"""
    minutes = seconds // 60
    secs = seconds % 60
    return f"{minutes:02d}:{secs:02d}"


def draw_circular_progress_ascii(progress, width=40):
    """ASCII アートで円形プログレスバーを描画"""
    center_x, center_y = width // 2, width // 2
    radius = width // 2 - 2
    
    lines = []
    for y in range(width):
        line = []
        for x in range(width):
            dx = x - center_x
            dy = y - center_y
            distance = math.sqrt(dx * dx + dy * dy)
            
            # 円の描画
            if abs(distance - radius) < 1.5:
                # 角度を計算（上から時計回り）
                angle = math.atan2(dy, dx)
                # -90度から開始（上を0度にする）
                angle_deg = (math.degrees(angle) + 90) % 360
                
                # プログレスバーの表示
                if angle_deg <= 360 * progress:
                    line.append("●")
                else:
                    line.append("○")
            elif distance < radius - 3:
                # 中央部分
                line.append(" ")
            else:
                line.append(" ")
        lines.append("".join(line))
    
    return "\n".join(lines)


def main():
    """メイン関数"""
    total_seconds = 25 * 60  # 25分
    
    print("\n" + "=" * 60)
    print("ポモドーロタイマー - ビジュアルデモンストレーション")
    print("=" * 60)
    print("\n円形プログレスバーと色の変化のシミュレーション\n")
    
    # 異なる進捗状態を表示
    progress_points = [
        (1.0, "開始時 (100%)"),
        (0.75, "75%経過"),
        (0.5, "50%経過（中間点）"),
        (0.25, "25%経過"),
        (0.1, "10%経過"),
    ]
    
    for progress, label in progress_points:
        remaining = int(total_seconds * progress)
        color_name = get_progress_color_name(remaining, total_seconds)
        time_str = format_time(remaining)
        
        print(f"\n{label}")
        print(f"残り時間: {time_str}")
        print(f"色: {color_name}")
        print("-" * 40)
        
        # 簡易版のプログレスバー
        filled = int(40 * progress)
        bar = "█" * filled + "░" * (40 - filled)
        print(f"[{bar}] {int(progress * 100)}%")
        print()
    
    print("\n" + "=" * 60)
    print("視覚的フィードバックの要素:")
    print("=" * 60)
    print("""
1. 円形プログレスバーのアニメーション
   - 残り時間に応じて滑らかに減少
   - 60FPSで更新される流れるようなアニメーション
   
2. 色の変化
   - 青 (#00d4ff): 100% → 50% - まだ十分に時間があります
   - 黄 (#ffd700): 50% → 25% - 半分が経過しました
   - 赤 (#ff4444): 25% → 0% - もうすぐ終了です
   
3. 背景エフェクト
   - パーティクルエフェクト: 50個のパーティクルが動き回る
   - グローエフェクト: 円の中心に輝くエフェクト
   - 作業時間中のみ表示され、集中をサポート
   
4. セッション管理
   - 作業: 25分（青い表示）
   - 短い休憩: 5分（緑の表示）
   - 長い休憩: 15分（紫の表示、4セッションごと）
""")
    
    print("=" * 60)
    print("実際のGUIアプリケーションを起動するには:")
    print("  python3 app.py")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
