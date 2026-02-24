#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポモドーロタイマー アプリケーション
カスタマイズ可能な時間設定、テーマ、サウンド設定を備えたポモドーロタイマー
"""

import tkinter as tk
from tkinter import ttk, messagebox
import json
import os
from pathlib import Path
from datetime import datetime, timedelta
import threading
import time

class PomodoroTimer:
    """ポモドーロタイマーのメインクラス"""
    
    # 設定のデフォルト値
    DEFAULT_SETTINGS = {
        'work_duration': 25,  # 作業時間（分）
        'break_duration': 5,  # 休憩時間（分）
        'theme': 'light',  # テーマ (light/dark/focus)
        'sound_start': True,  # 開始音
        'sound_end': True,  # 終了音
        'sound_tick': False  # tick音
    }
    
    # テーマ設定
    THEMES = {
        'light': {
            'bg': '#f0f0f0',
            'fg': '#333333',
            'button_bg': '#4CAF50',
            'button_fg': '#ffffff',
            'timer_fg': '#2196F3',
            'settings_bg': '#ffffff'
        },
        'dark': {
            'bg': '#1e1e1e',
            'fg': '#e0e0e0',
            'button_bg': '#2e7d32',
            'button_fg': '#ffffff',
            'timer_fg': '#64b5f6',
            'settings_bg': '#2d2d2d'
        },
        'focus': {
            'bg': '#fafafa',
            'fg': '#424242',
            'button_bg': '#757575',
            'button_fg': '#ffffff',
            'timer_fg': '#616161',
            'settings_bg': '#ffffff'
        }
    }
    
    def __init__(self, root):
        """初期化"""
        self.root = root
        self.root.title("ポモドーロタイマー")
        self.root.geometry("600x700")
        self.root.resizable(False, False)
        
        # 設定ファイルのパス
        self.config_file = Path(__file__).parent / 'settings.json'
        
        # 設定の読み込み
        self.settings = self.load_settings()
        
        # タイマーの状態
        self.is_running = False
        self.is_work_time = True
        self.remaining_seconds = self.settings['work_duration'] * 60
        self.timer_thread = None
        
        # UIの構築
        self.setup_ui()
        
        # テーマの適用
        self.apply_theme()
        
    def load_settings(self):
        """設定ファイルを読み込む"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # デフォルト設定にマージ
                    settings = self.DEFAULT_SETTINGS.copy()
                    settings.update(loaded_settings)
                    return settings
            except Exception as e:
                print(f"設定ファイルの読み込みエラー: {e}")
        return self.DEFAULT_SETTINGS.copy()
    
    def save_settings(self):
        """設定をファイルに保存"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.settings, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"設定ファイルの保存エラー: {e}")
    
    def setup_ui(self):
        """UIを構築"""
        # メインフレーム
        self.main_frame = tk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # タイトル
        title_label = tk.Label(
            self.main_frame,
            text="🍅 ポモドーロタイマー",
            font=('Arial', 24, 'bold')
        )
        title_label.pack(pady=(0, 20))
        
        # 状態表示
        self.status_label = tk.Label(
            self.main_frame,
            text="作業時間",
            font=('Arial', 16)
        )
        self.status_label.pack(pady=(0, 10))
        
        # タイマー表示
        self.timer_label = tk.Label(
            self.main_frame,
            text=self.format_time(self.remaining_seconds),
            font=('Arial', 72, 'bold')
        )
        self.timer_label.pack(pady=20)
        
        # コントロールボタンフレーム
        button_frame = tk.Frame(self.main_frame)
        button_frame.pack(pady=20)
        
        # 開始/一時停止ボタン
        self.start_button = tk.Button(
            button_frame,
            text="開始",
            font=('Arial', 14, 'bold'),
            width=12,
            height=2,
            command=self.toggle_timer
        )
        self.start_button.pack(side=tk.LEFT, padx=10)
        
        # リセットボタン
        self.reset_button = tk.Button(
            button_frame,
            text="リセット",
            font=('Arial', 14),
            width=12,
            height=2,
            command=self.reset_timer
        )
        self.reset_button.pack(side=tk.LEFT, padx=10)
        
        # 設定パネル
        self.setup_settings_panel()
    
    def setup_settings_panel(self):
        """設定パネルを構築"""
        settings_frame = tk.LabelFrame(
            self.main_frame,
            text="⚙️ 設定",
            font=('Arial', 14, 'bold'),
            padx=20,
            pady=20
        )
        settings_frame.pack(fill=tk.BOTH, expand=True, pady=(20, 0))
        
        # 作業時間設定
        work_frame = tk.Frame(settings_frame)
        work_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(work_frame, text="作業時間:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.work_var = tk.IntVar(value=self.settings['work_duration'])
        for duration in [15, 25, 35, 45]:
            rb = tk.Radiobutton(
                work_frame,
                text=f"{duration}分",
                variable=self.work_var,
                value=duration,
                font=('Arial', 11),
                command=self.on_settings_change
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # 休憩時間設定
        break_frame = tk.Frame(settings_frame)
        break_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(break_frame, text="休憩時間:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.break_var = tk.IntVar(value=self.settings['break_duration'])
        for duration in [5, 10, 15]:
            rb = tk.Radiobutton(
                break_frame,
                text=f"{duration}分",
                variable=self.break_var,
                value=duration,
                font=('Arial', 11),
                command=self.on_settings_change
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # テーマ設定
        theme_frame = tk.Frame(settings_frame)
        theme_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(theme_frame, text="テーマ:", font=('Arial', 12)).pack(side=tk.LEFT)
        self.theme_var = tk.StringVar(value=self.settings['theme'])
        themes = [('ライト', 'light'), ('ダーク', 'dark'), ('フォーカス', 'focus')]
        for label, value in themes:
            rb = tk.Radiobutton(
                theme_frame,
                text=label,
                variable=self.theme_var,
                value=value,
                font=('Arial', 11),
                command=self.on_theme_change
            )
            rb.pack(side=tk.LEFT, padx=10)
        
        # サウンド設定
        sound_frame = tk.Frame(settings_frame)
        sound_frame.pack(fill=tk.X, pady=10)
        
        tk.Label(sound_frame, text="サウンド:", font=('Arial', 12)).pack(side=tk.LEFT, padx=(0, 10))
        
        self.sound_start_var = tk.BooleanVar(value=self.settings['sound_start'])
        tk.Checkbutton(
            sound_frame,
            text="開始音",
            variable=self.sound_start_var,
            font=('Arial', 11),
            command=self.on_settings_change
        ).pack(side=tk.LEFT, padx=5)
        
        self.sound_end_var = tk.BooleanVar(value=self.settings['sound_end'])
        tk.Checkbutton(
            sound_frame,
            text="終了音",
            variable=self.sound_end_var,
            font=('Arial', 11),
            command=self.on_settings_change
        ).pack(side=tk.LEFT, padx=5)
        
        self.sound_tick_var = tk.BooleanVar(value=self.settings['sound_tick'])
        tk.Checkbutton(
            sound_frame,
            text="tick音",
            variable=self.sound_tick_var,
            font=('Arial', 11),
            command=self.on_settings_change
        ).pack(side=tk.LEFT, padx=5)
    
    def format_time(self, seconds):
        """秒を MM:SS 形式にフォーマット"""
        minutes = seconds // 60
        secs = seconds % 60
        return f"{minutes:02d}:{secs:02d}"
    
    def toggle_timer(self):
        """タイマーの開始/一時停止を切り替え"""
        if self.is_running:
            self.pause_timer()
        else:
            self.start_timer()
    
    def start_timer(self):
        """タイマーを開始"""
        self.is_running = True
        self.start_button.config(text="一時停止")
        
        # 開始音を再生（設定されている場合）
        if self.settings['sound_start']:
            self.play_sound('start')
        
        # タイマースレッドを開始
        if self.timer_thread is None or not self.timer_thread.is_alive():
            self.timer_thread = threading.Thread(target=self.run_timer, daemon=True)
            self.timer_thread.start()
    
    def pause_timer(self):
        """タイマーを一時停止"""
        self.is_running = False
        self.start_button.config(text="再開")
    
    def reset_timer(self):
        """タイマーをリセット"""
        self.is_running = False
        self.is_work_time = True
        self.remaining_seconds = self.settings['work_duration'] * 60
        
        self.start_button.config(text="開始")
        self.status_label.config(text="作業時間")
        self.timer_label.config(text=self.format_time(self.remaining_seconds))
    
    def run_timer(self):
        """タイマーのメインループ"""
        while self.remaining_seconds > 0 and self.is_running:
            time.sleep(1)
            if self.is_running:
                self.remaining_seconds -= 1
                
                # tick音を再生（設定されている場合）
                if self.settings['sound_tick']:
                    self.play_sound('tick')
                
                # UIを更新（メインスレッドで実行）
                self.root.after(0, self.update_display)
        
        # タイマー終了
        if self.remaining_seconds == 0 and self.is_running:
            self.on_timer_complete()
    
    def update_display(self):
        """表示を更新"""
        self.timer_label.config(text=self.format_time(self.remaining_seconds))
    
    def on_timer_complete(self):
        """タイマー完了時の処理"""
        # 終了音を再生（設定されている場合）
        if self.settings['sound_end']:
            self.play_sound('end')
        
        # 作業時間と休憩時間を切り替え
        if self.is_work_time:
            message = "お疲れ様です！休憩時間です。"
            self.is_work_time = False
            self.remaining_seconds = self.settings['break_duration'] * 60
            self.status_label.config(text="休憩時間")
        else:
            message = "休憩終了です。作業を再開しましょう！"
            self.is_work_time = True
            self.remaining_seconds = self.settings['work_duration'] * 60
            self.status_label.config(text="作業時間")
        
        # 通知を表示
        self.root.after(0, lambda: messagebox.showinfo("タイマー完了", message))
        
        # 自動的に次のタイマーを開始
        self.update_display()
    
    def play_sound(self, sound_type):
        """サウンドを再生（実際の音声ファイルがある場合のプレースホルダー）"""
        # 実装例：winsound、pygame、または他のライブラリを使用して音を再生
        # ここでは簡易的にビープ音を使用
        if sound_type in ['start', 'end']:
            # システムビープ音（クロスプラットフォーム対応が難しいため、print文で代用）
            print(f"🔊 {sound_type} サウンド")
    
    def on_settings_change(self):
        """設定変更時の処理"""
        self.settings['work_duration'] = self.work_var.get()
        self.settings['break_duration'] = self.break_var.get()
        self.settings['sound_start'] = self.sound_start_var.get()
        self.settings['sound_end'] = self.sound_end_var.get()
        self.settings['sound_tick'] = self.sound_tick_var.get()
        
        # タイマーが停止中の場合、時間をリセット
        if not self.is_running:
            if self.is_work_time:
                self.remaining_seconds = self.settings['work_duration'] * 60
            else:
                self.remaining_seconds = self.settings['break_duration'] * 60
            self.update_display()
        
        # 設定を保存
        self.save_settings()
    
    def on_theme_change(self):
        """テーマ変更時の処理"""
        self.settings['theme'] = self.theme_var.get()
        self.apply_theme()
        self.save_settings()
    
    def apply_theme(self):
        """現在のテーマを適用"""
        theme = self.THEMES[self.settings['theme']]
        
        # ルートウィンドウの背景色
        self.root.config(bg=theme['bg'])
        
        # メインフレームとその子要素に適用
        self.apply_theme_to_widget(self.main_frame, theme)
    
    def apply_theme_to_widget(self, widget, theme):
        """ウィジェットとその子要素にテーマを適用"""
        # ウィジェットの種類に応じて色を設定
        widget_class = widget.winfo_class()
        
        try:
            if widget_class in ['Frame', 'Labelframe']:
                widget.config(bg=theme['bg'])
            elif widget_class == 'Label':
                # タイマー表示は特別な色
                if widget == self.timer_label:
                    widget.config(bg=theme['bg'], fg=theme['timer_fg'])
                else:
                    widget.config(bg=theme['bg'], fg=theme['fg'])
            elif widget_class == 'Button':
                widget.config(bg=theme['button_bg'], fg=theme['button_fg'])
            elif widget_class in ['Radiobutton', 'Checkbutton']:
                widget.config(bg=theme['bg'], fg=theme['fg'], selectcolor=theme['bg'])
        except tk.TclError:
            # 一部のウィジェットは色設定をサポートしていない場合がある
            pass
        
        # 子要素に再帰的に適用
        for child in widget.winfo_children():
            self.apply_theme_to_widget(child, theme)

def main():
    """メイン関数"""
    root = tk.Tk()
    app = PomodoroTimer(root)
    root.mainloop()

if __name__ == '__main__':
    main()
