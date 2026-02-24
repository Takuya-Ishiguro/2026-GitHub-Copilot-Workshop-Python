#!/usr/bin/env python3
"""
ポモドーロタイマーのテスト
"""

import unittest
import sys
import os

# app.pyのパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import Particle, PomodoroTimer

# テスト定数
NUM_UPDATE_ITERATIONS = 100  # パーティクル更新の反復回数


class TestParticle(unittest.TestCase):
    """Particleクラスのテスト"""
    
    def test_particle_creation(self):
        """パーティクルが正しく作成されるか"""
        particle = Particle(100, 100, 400, 400)
        self.assertEqual(particle.canvas_width, 400)
        self.assertEqual(particle.canvas_height, 400)
        self.assertGreaterEqual(particle.size, 2)
        self.assertLessEqual(particle.size, 5)
        
    def test_particle_update(self):
        """パーティクルの位置が更新されるか"""
        particle = Particle(100, 100, 400, 400)
        initial_x, initial_y = particle.x, particle.y
        initial_vx, initial_vy = particle.vx, particle.vy
        
        # 速度が設定されていることを確認
        self.assertIsNotNone(particle.vx)
        self.assertIsNotNone(particle.vy)
        
        # 複数回更新して、位置が変化することを確認
        for _ in range(10):
            particle.update()
        
        # 速度が0でない限り、位置は変化する
        if initial_vx != 0 or initial_vy != 0:
            self.assertTrue(
                particle.x != initial_x or particle.y != initial_y,
                "パーティクルの位置が更新されませんでした"
            )
        
    def test_particle_boundary(self):
        """パーティクルが境界内に収まるか"""
        particle = Particle(100, 100, 400, 400)
        for _ in range(NUM_UPDATE_ITERATIONS):
            particle.update()
            self.assertGreaterEqual(particle.x, 0)
            self.assertLessEqual(particle.x, 400)
            self.assertGreaterEqual(particle.y, 0)
            self.assertLessEqual(particle.y, 400)


class TestPomodoroTimerLogic(unittest.TestCase):
    """PomodoroTimerのロジックテスト（GUI不要）"""
    
    def test_format_time(self):
        """時間フォーマット関数のテスト"""
        # モックルート
        import tkinter as tk
        try:
            root = tk.Tk()
            root.withdraw()  # ウィンドウを表示しない
            timer = PomodoroTimer(root)
            
            self.assertEqual(timer.format_time(0), "00:00")
            self.assertEqual(timer.format_time(60), "01:00")
            self.assertEqual(timer.format_time(125), "02:05")
            self.assertEqual(timer.format_time(1500), "25:00")
            
            root.destroy()
        except tk.TclError:
            # ディスプレイがない環境ではスキップ
            self.skipTest("No display available for Tkinter")
            
    def test_get_progress_color(self):
        """プログレス色の計算テスト"""
        import tkinter as tk
        try:
            root = tk.Tk()
            root.withdraw()
            timer = PomodoroTimer(root)
            
            # 100%時点（青）
            timer.remaining_seconds = timer.total_seconds
            color = timer.get_progress_color()
            self.assertIsInstance(color, str)
            self.assertTrue(color.startswith("#"))
            
            # 50%時点（黄）
            timer.remaining_seconds = timer.total_seconds // 2
            color = timer.get_progress_color()
            self.assertIsInstance(color, str)
            
            # 0%時点（赤）
            timer.remaining_seconds = 0
            color = timer.get_progress_color()
            self.assertIsInstance(color, str)
            
            root.destroy()
        except tk.TclError:
            self.skipTest("No display available for Tkinter")
            
    def test_initial_state(self):
        """初期状態のテスト"""
        import tkinter as tk
        try:
            root = tk.Tk()
            root.withdraw()
            timer = PomodoroTimer(root)
            
            self.assertFalse(timer.is_running)
            self.assertTrue(timer.is_work_session)
            self.assertEqual(timer.total_seconds, timer.WORK_DURATION * 60)
            self.assertEqual(timer.remaining_seconds, timer.total_seconds)
            self.assertEqual(timer.session_count, 0)
            
            root.destroy()
        except tk.TclError:
            self.skipTest("No display available for Tkinter")


if __name__ == "__main__":
    unittest.main()
