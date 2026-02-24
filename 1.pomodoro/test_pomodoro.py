"""
ポモドーロタイマーの機能テスト
"""
import unittest
import os
import sys
from datetime import datetime, timedelta

# モジュールパスを追加
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from models import PomodoroDatabase


class TestPomodoroDatabase(unittest.TestCase):
    """データベース機能のテスト"""
    
    def setUp(self):
        """テスト前の準備"""
        self.test_db_path = 'test_pomodoro.db'
        # 既存のテストDBを削除
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
        self.db = PomodoroDatabase(self.test_db_path)
    
    def tearDown(self):
        """テスト後のクリーンアップ"""
        if os.path.exists(self.test_db_path):
            os.remove(self.test_db_path)
    
    def test_initial_stats(self):
        """初期統計の確認"""
        stats = self.db.get_user_stats()
        self.assertEqual(stats['total_xp'], 0)
        self.assertEqual(stats['level'], 1)
        self.assertEqual(stats['current_streak'], 0)
        self.assertEqual(stats['max_streak'], 0)
    
    def test_add_pomodoro(self):
        """ポモドーロ追加のテスト"""
        result = self.db.add_pomodoro(25)
        
        # XPが加算されていることを確認
        self.assertEqual(result['xp_gained'], 100)
        self.assertEqual(result['total_xp'], 100)
        
        # 統計を確認
        stats = self.db.get_user_stats()
        self.assertEqual(stats['total_xp'], 100)
        self.assertEqual(stats['level'], 1)
    
    def test_level_up(self):
        """レベルアップのテスト"""
        # レベルアップに必要なXP（500 XP）を獲得するために5回ポモドーロを完了
        for _ in range(5):
            result = self.db.add_pomodoro(25)
        
        # レベル2になっているはず
        stats = self.db.get_user_stats()
        self.assertEqual(stats['level'], 2)
        self.assertEqual(stats['total_xp'], 500)
    
    def test_streak_same_day(self):
        """同じ日のストリークテスト"""
        # 同じ日に2回完了
        self.db.add_pomodoro(25)
        self.db.add_pomodoro(25)
        
        stats = self.db.get_user_stats()
        # 同じ日なのでストリークは1のまま
        self.assertEqual(stats['current_streak'], 1)
    
    def test_badges_first_pomodoro(self):
        """初回バッジのテスト"""
        self.db.add_pomodoro(25)
        badges = self.db.check_and_award_badges()
        
        # 初めてのポモドーロバッジを獲得
        self.assertIn('初めてのポモドーロ', badges)
    
    def test_badges_total_10(self):
        """10回達成バッジのテスト"""
        # 10回ポモドーロを完了
        for _ in range(10):
            self.db.add_pomodoro(25)
        
        badges = self.db.check_and_award_badges()
        
        # バッジリストを取得
        all_badges = self.db.get_badges()
        badge_types = [b['type'] for b in all_badges]
        
        # 合計10回達成バッジを獲得しているはず
        self.assertIn('合計10回達成', badge_types)
    
    def test_weekly_stats(self):
        """週間統計のテスト"""
        # 今日3回完了
        for _ in range(3):
            self.db.add_pomodoro(25)
        
        weekly = self.db.get_weekly_stats()
        
        # 今週の完了数が3であることを確認
        self.assertEqual(weekly['total_count'], 3)
        self.assertGreater(weekly['completion_rate'], 0)
        
        # 日別データが7日分あることを確認
        self.assertEqual(len(weekly['daily_counts']), 7)
    
    def test_monthly_stats(self):
        """月間統計のテスト"""
        # 5回完了
        for _ in range(5):
            self.db.add_pomodoro(25)
        
        monthly = self.db.get_monthly_stats()
        
        # 今月の完了数が5であることを確認
        self.assertEqual(monthly['total_count'], 5)
        self.assertEqual(monthly['avg_duration'], 25.0)
        self.assertGreater(monthly['completion_rate'], 0)


if __name__ == '__main__':
    unittest.main()
