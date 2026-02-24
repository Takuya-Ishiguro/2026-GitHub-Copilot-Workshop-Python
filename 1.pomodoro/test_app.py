#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ポモドーロタイマーのテスト
"""

import unittest
import json
import os
from pathlib import Path
import sys

# ヘッドレス環境でのテスト対応
try:
    import tkinter as tk
except ImportError:
    # tkinterが利用できない場合はスキップ
    print("Warning: tkinter not available, skipping GUI tests", file=sys.stderr)
    sys.exit(0)

# DISPLAY環境変数が設定されていない場合のエラーを回避
try:
    test_root = tk.Tk()
    test_root.destroy()
except Exception as e:
    print(f"Warning: Cannot create Tk window ({e}), skipping GUI tests", file=sys.stderr)
    sys.exit(0)

from app import PomodoroTimer

class TestPomodoroTimer(unittest.TestCase):
    """ポモドーロタイマーのテストクラス"""
    
    def setUp(self):
        """各テストの前に実行"""
        self.root = tk.Tk()
        self.app = PomodoroTimer(self.root)
        
    def tearDown(self):
        """各テストの後に実行"""
        # テスト用設定ファイルを削除
        if self.app.config_file.exists():
            os.remove(self.app.config_file)
        self.root.destroy()
    
    def test_default_settings(self):
        """デフォルト設定のテスト"""
        self.assertEqual(self.app.settings['work_duration'], 25)
        self.assertEqual(self.app.settings['break_duration'], 5)
        self.assertEqual(self.app.settings['theme'], 'light')
        self.assertTrue(self.app.settings['sound_start'])
        self.assertTrue(self.app.settings['sound_end'])
        self.assertFalse(self.app.settings['sound_tick'])
    
    def test_work_duration_options(self):
        """作業時間の選択肢テスト"""
        for duration in [15, 25, 35, 45]:
            self.app.work_var.set(duration)
            self.app.on_settings_change()
            self.assertEqual(self.app.settings['work_duration'], duration)
    
    def test_break_duration_options(self):
        """休憩時間の選択肢テスト"""
        for duration in [5, 10, 15]:
            self.app.break_var.set(duration)
            self.app.on_settings_change()
            self.assertEqual(self.app.settings['break_duration'], duration)
    
    def test_theme_options(self):
        """テーマの選択肢テスト"""
        for theme in ['light', 'dark', 'focus']:
            self.app.theme_var.set(theme)
            self.app.on_theme_change()
            self.assertEqual(self.app.settings['theme'], theme)
    
    def test_sound_settings(self):
        """サウンド設定のテスト"""
        # 開始音
        self.app.sound_start_var.set(False)
        self.app.on_settings_change()
        self.assertFalse(self.app.settings['sound_start'])
        
        # 終了音
        self.app.sound_end_var.set(False)
        self.app.on_settings_change()
        self.assertFalse(self.app.settings['sound_end'])
        
        # tick音
        self.app.sound_tick_var.set(True)
        self.app.on_settings_change()
        self.assertTrue(self.app.settings['sound_tick'])
    
    def test_format_time(self):
        """時間フォーマットのテスト"""
        self.assertEqual(self.app.format_time(0), "00:00")
        self.assertEqual(self.app.format_time(59), "00:59")
        self.assertEqual(self.app.format_time(60), "01:00")
        self.assertEqual(self.app.format_time(1500), "25:00")
        self.assertEqual(self.app.format_time(3599), "59:59")
    
    def test_initial_state(self):
        """初期状態のテスト"""
        self.assertFalse(self.app.is_running)
        self.assertTrue(self.app.is_work_time)
        self.assertEqual(self.app.remaining_seconds, 25 * 60)
    
    def test_save_and_load_settings(self):
        """設定の保存と読み込みテスト"""
        # 設定を変更
        self.app.settings['work_duration'] = 35
        self.app.settings['break_duration'] = 10
        self.app.settings['theme'] = 'dark'
        self.app.save_settings()
        
        # 新しいインスタンスを作成して設定を読み込む
        new_root = tk.Tk()
        new_app = PomodoroTimer(new_root)
        
        # 設定が保存されていることを確認
        self.assertEqual(new_app.settings['work_duration'], 35)
        self.assertEqual(new_app.settings['break_duration'], 10)
        self.assertEqual(new_app.settings['theme'], 'dark')
        
        new_root.destroy()
    
    def test_reset_timer(self):
        """タイマーリセットのテスト"""
        # タイマーの状態を変更
        self.app.is_work_time = False
        self.app.remaining_seconds = 100
        
        # リセット
        self.app.reset_timer()
        
        # 初期状態に戻ることを確認
        self.assertFalse(self.app.is_running)
        self.assertTrue(self.app.is_work_time)
        self.assertEqual(self.app.remaining_seconds, self.app.settings['work_duration'] * 60)
    
    def test_theme_colors(self):
        """テーマカラーの定義テスト"""
        # すべてのテーマが必要なキーを持っていることを確認
        required_keys = ['bg', 'fg', 'button_bg', 'button_fg', 'timer_fg', 'settings_bg']
        for theme_name, theme_colors in PomodoroTimer.THEMES.items():
            for key in required_keys:
                self.assertIn(key, theme_colors, f"Theme '{theme_name}' missing key '{key}'")

class TestSettingsPersistence(unittest.TestCase):
    """設定の永続化テスト"""
    
    def setUp(self):
        """各テストの前に実行"""
        self.test_config_file = Path(__file__).parent / 'test_settings.json'
        
    def tearDown(self):
        """各テストの後に実行"""
        if self.test_config_file.exists():
            os.remove(self.test_config_file)
    
    def test_json_format(self):
        """JSON形式の妥当性テスト"""
        root = tk.Tk()
        app = PomodoroTimer(root)
        
        # 設定を変更して保存
        app.settings['work_duration'] = 45
        app.config_file = self.test_config_file
        app.save_settings()
        
        # ファイルが正しいJSON形式かチェック
        with open(self.test_config_file, 'r', encoding='utf-8') as f:
            loaded_data = json.load(f)
            self.assertIsInstance(loaded_data, dict)
            self.assertEqual(loaded_data['work_duration'], 45)
        
        root.destroy()

if __name__ == '__main__':
    unittest.main()
