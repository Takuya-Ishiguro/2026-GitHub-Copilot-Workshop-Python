#!/usr/bin/env python3
"""
ポモドーロタイマーアプリケーション
視覚的フィードバック強化版

機能:
- 円形プログレスバーのアニメーション
- 時間経過に応じた色の変化（青→黄→赤）
- 背景パーティクルエフェクト
"""

import tkinter as tk
from tkinter import ttk
import math
import random
from datetime import datetime, timedelta


class Particle:
    """背景パーティクルエフェクト用のクラス"""
    
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
        
        # 画面端で反射
        if self.x < 0 or self.x > self.canvas_width:
            self.vx *= -1
        if self.y < 0 or self.y > self.canvas_height:
            self.vy *= -1
            
        # 範囲内に収める
        self.x = max(0, min(self.canvas_width, self.x))
        self.y = max(0, min(self.canvas_height, self.y))


class PomodoroTimer:
    """ポモドーロタイマーメインクラス"""
    
    # ポモドーロの時間設定（分）
    WORK_DURATION = 25
    SHORT_BREAK = 5
    LONG_BREAK = 15
    
    def __init__(self, root):
        self.root = root
        self.root.title("ポモドーロタイマー - 視覚的フィードバック強化版")
        self.root.geometry("600x700")
        self.root.configure(bg="#1e1e1e")
        
        # タイマー状態
        self.is_running = False
        self.is_work_session = True
        self.total_seconds = self.WORK_DURATION * 60
        self.remaining_seconds = self.total_seconds
        self.session_count = 0
        
        # パーティクル管理
        self.particles = []
        self.num_particles = 50
        
        # UI要素の作成
        self.create_widgets()
        self.initialize_particles()
        
        # アニメーションループ開始
        self.animate()
        
    def create_widgets(self):
        """UI要素を作成"""
        # タイトルラベル
        self.title_label = tk.Label(
            self.root,
            text="ポモドーロタイマー",
            font=("Arial", 24, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        )
        self.title_label.pack(pady=20)
        
        # セッション情報ラベル
        self.session_label = tk.Label(
            self.root,
            text="集中時間",
            font=("Arial", 18),
            bg="#1e1e1e",
            fg="#00d4ff"
        )
        self.session_label.pack(pady=10)
        
        # キャンバス（円形プログレスバーと背景エフェクト用）
        self.canvas = tk.Canvas(
            self.root,
            width=400,
            height=400,
            bg="#1e1e1e",
            highlightthickness=0
        )
        self.canvas.pack(pady=20)
        
        # 時間表示ラベル
        self.time_label = tk.Label(
            self.root,
            text=self.format_time(self.remaining_seconds),
            font=("Arial", 48, "bold"),
            bg="#1e1e1e",
            fg="#ffffff"
        )
        self.time_label.pack(pady=10)
        
        # ボタンフレーム
        button_frame = tk.Frame(self.root, bg="#1e1e1e")
        button_frame.pack(pady=20)
        
        # 開始/一時停止ボタン
        self.start_button = tk.Button(
            button_frame,
            text="開始",
            command=self.toggle_timer,
            font=("Arial", 14),
            bg="#00d4ff",
            fg="#1e1e1e",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # リセットボタン
        self.reset_button = tk.Button(
            button_frame,
            text="リセット",
            command=self.reset_timer,
            font=("Arial", 14),
            bg="#ff6b6b",
            fg="#ffffff",
            padx=20,
            pady=10,
            relief=tk.FLAT,
            cursor="hand2"
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
    def initialize_particles(self):
        """パーティクルを初期化"""
        self.particles = []
        canvas_width = 400
        canvas_height = 400
        for _ in range(self.num_particles):
            x = random.uniform(0, canvas_width)
            y = random.uniform(0, canvas_height)
            self.particles.append(Particle(x, y, canvas_width, canvas_height))
            
    def get_progress_color(self):
        """
        残り時間に応じて色を計算
        青 (#00d4ff) → 黄 (#ffd700) → 赤 (#ff4444)
        """
        progress = self.remaining_seconds / self.total_seconds
        
        if progress > 0.5:
            # 青から黄へ (100% -> 50%)
            t = (progress - 0.5) * 2  # 0.5-1.0 を 0-1 にマッピング
            r = int(0 + (255 - 0) * (1 - t))
            g = int(212 + (215 - 212) * (1 - t))
            b = int(255 + (0 - 255) * (1 - t))
        else:
            # 黄から赤へ (50% -> 0%)
            t = progress * 2  # 0-0.5 を 0-1 にマッピング
            r = 255
            g = int(68 + (215 - 68) * t)
            b = int(68 + (0 - 68) * t)
            
        return f"#{r:02x}{g:02x}{b:02x}"
        
    def draw_circular_progress(self):
        """円形プログレスバーを描画"""
        self.canvas.delete("all")
        
        # 背景パーティクルエフェクト（作業中のみ）
        if self.is_running and self.is_work_session:
            for particle in self.particles:
                particle.update()
                color_alpha = int(particle.alpha * 255)
                color = f"#{color_alpha:02x}{color_alpha:02x}{color_alpha:02x}"
                self.canvas.create_oval(
                    particle.x - particle.size,
                    particle.y - particle.size,
                    particle.x + particle.size,
                    particle.y + particle.size,
                    fill=color,
                    outline=""
                )
        
        # 円の中心と半径
        center_x, center_y = 200, 200
        radius = 150
        
        # 背景円（グレー）
        self.canvas.create_oval(
            center_x - radius,
            center_y - radius,
            center_x + radius,
            center_y + radius,
            outline="#404040",
            width=20,
            fill=""
        )
        
        # プログレス円
        progress = self.remaining_seconds / self.total_seconds
        extent = 360 * progress
        color = self.get_progress_color()
        
        # 円弧を描画（上から時計回り）
        if extent > 0:
            self.canvas.create_arc(
                center_x - radius,
                center_y - radius,
                center_x + radius,
                center_y + radius,
                start=90,
                extent=-extent,
                outline=color,
                width=20,
                style=tk.ARC
            )
            
        # 中央に装飾的なグロー効果
        if self.is_running and self.is_work_session:
            glow_radius = radius * 0.7
            glow_color = self.get_progress_color()
            # 半透明のグロー円
            for i in range(3):
                alpha_radius = glow_radius - i * 10
                self.canvas.create_oval(
                    center_x - alpha_radius,
                    center_y - alpha_radius,
                    center_x + alpha_radius,
                    center_y + alpha_radius,
                    outline=glow_color,
                    width=2,
                    fill=""
                )
    
    def format_time(self, seconds):
        """秒を MM:SS 形式にフォーマット"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
        
    def toggle_timer(self):
        """タイマーの開始/一時停止を切り替え"""
        self.is_running = not self.is_running
        if self.is_running:
            self.start_button.config(text="一時停止")
        else:
            self.start_button.config(text="再開")
            
    def reset_timer(self):
        """タイマーをリセット"""
        self.is_running = False
        self.is_work_session = True
        self.total_seconds = self.WORK_DURATION * 60
        self.remaining_seconds = self.total_seconds
        self.start_button.config(text="開始")
        self.session_label.config(text="集中時間", fg="#00d4ff")
        self.time_label.config(text=self.format_time(self.remaining_seconds))
        self.draw_circular_progress()
        
    def update_timer(self):
        """タイマーを1秒更新"""
        if self.is_running and self.remaining_seconds > 0:
            self.remaining_seconds -= 1
            self.time_label.config(text=self.format_time(self.remaining_seconds))
            
            if self.remaining_seconds == 0:
                # セッション完了
                self.complete_session()
                
    def complete_session(self):
        """セッション完了時の処理"""
        self.is_running = False
        self.start_button.config(text="開始")
        
        if self.is_work_session:
            # 作業セッション完了、休憩へ
            self.session_count += 1
            if self.session_count % 4 == 0:
                # 長い休憩
                self.total_seconds = self.LONG_BREAK * 60
                self.session_label.config(text="長い休憩", fg="#9d4edd")
            else:
                # 短い休憩
                self.total_seconds = self.SHORT_BREAK * 60
                self.session_label.config(text="短い休憩", fg="#90ee90")
            self.is_work_session = False
        else:
            # 休憩完了、作業へ
            self.total_seconds = self.WORK_DURATION * 60
            self.session_label.config(text="集中時間", fg="#00d4ff")
            self.is_work_session = True
            
        self.remaining_seconds = self.total_seconds
        self.time_label.config(text=self.format_time(self.remaining_seconds))
        
    def animate(self):
        """アニメーションループ（60fps目標）"""
        self.draw_circular_progress()
        self.root.after(16, self.animate)  # 約60fps
        
    def tick(self):
        """1秒ごとのタイマー更新"""
        self.update_timer()
        self.root.after(1000, self.tick)


def main():
    """メイン関数"""
    root = tk.Tk()
    app = PomodoroTimer(root)
    app.tick()  # タイマー更新開始
    root.mainloop()


if __name__ == "__main__":
    main()
