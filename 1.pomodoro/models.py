"""
データモデルとデータベース管理
"""
import sqlite3
from datetime import datetime, timedelta
from typing import List, Dict, Optional
import os


class PomodoroDatabase:
    """ポモドーロタイマーのデータベース管理"""
    
    def __init__(self, db_path: str = "pomodoro.db"):
        """データベースの初期化"""
        self.db_path = db_path
        self._initialize_database()
    
    def _initialize_database(self):
        """データベースとテーブルの作成"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # ポモドーロ記録テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pomodoros (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                completed_at TEXT NOT NULL,
                duration INTEGER NOT NULL
            )
        ''')
        
        # ユーザー統計テーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS user_stats (
                id INTEGER PRIMARY KEY CHECK (id = 1),
                total_xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                current_streak INTEGER DEFAULT 0,
                max_streak INTEGER DEFAULT 0,
                last_completion_date TEXT
            )
        ''')
        
        # バッジテーブル
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS badges (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                badge_type TEXT NOT NULL,
                earned_at TEXT NOT NULL,
                UNIQUE(badge_type)
            )
        ''')
        
        # 初期統計データを挿入
        cursor.execute('''
            INSERT OR IGNORE INTO user_stats (id, total_xp, level, current_streak, max_streak)
            VALUES (1, 0, 1, 0, 0)
        ''')
        
        conn.commit()
        conn.close()
    
    def add_pomodoro(self, duration: int = 25) -> Dict:
        """ポモドーロの完了を記録"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        completed_at = datetime.now().isoformat()
        
        # ポモドーロ記録を追加
        cursor.execute('''
            INSERT INTO pomodoros (completed_at, duration)
            VALUES (?, ?)
        ''', (completed_at, duration))
        
        # XPを加算（1ポモドーロ = 100 XP）
        xp_gained = 100
        cursor.execute('''
            UPDATE user_stats
            SET total_xp = total_xp + ?
            WHERE id = 1
        ''', (xp_gained,))
        
        # 現在の統計を取得
        cursor.execute('SELECT total_xp, level FROM user_stats WHERE id = 1')
        total_xp, current_level = cursor.fetchone()
        
        # レベルアップチェック（500 XPごとにレベルアップ）
        new_level = (total_xp // 500) + 1
        leveled_up = new_level > current_level
        
        if leveled_up:
            cursor.execute('''
                UPDATE user_stats
                SET level = ?
                WHERE id = 1
            ''', (new_level,))
        
        # ストリークを更新
        self._update_streak(cursor, completed_at)
        
        conn.commit()
        conn.close()
        
        return {
            'xp_gained': xp_gained,
            'total_xp': total_xp,
            'leveled_up': leveled_up,
            'new_level': new_level if leveled_up else current_level
        }
    
    def _update_streak(self, cursor, completed_at: str):
        """ストリークを更新"""
        cursor.execute('SELECT last_completion_date, current_streak, max_streak FROM user_stats WHERE id = 1')
        row = cursor.fetchone()
        last_date_str, current_streak, max_streak = row
        
        current_date = datetime.fromisoformat(completed_at).date()
        
        if last_date_str:
            last_date = datetime.fromisoformat(last_date_str).date()
            days_diff = (current_date - last_date).days
            
            if days_diff == 0:
                # 同じ日 - ストリークは変わらない
                pass
            elif days_diff == 1:
                # 連続した日 - ストリークを増やす
                current_streak += 1
            else:
                # ストリークが途切れた
                current_streak = 1
        else:
            # 初回
            current_streak = 1
        
        max_streak = max(max_streak, current_streak)
        
        cursor.execute('''
            UPDATE user_stats
            SET current_streak = ?,
                max_streak = ?,
                last_completion_date = ?
            WHERE id = 1
        ''', (current_streak, max_streak, completed_at))
    
    def get_user_stats(self) -> Dict:
        """ユーザー統計を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT total_xp, level, current_streak, max_streak, last_completion_date
            FROM user_stats WHERE id = 1
        ''')
        row = cursor.fetchone()
        
        if row:
            total_xp, level, current_streak, max_streak, last_date = row
            next_level_xp = (level * 500)
            current_level_xp = ((level - 1) * 500)
            xp_progress = total_xp - current_level_xp
            xp_needed = next_level_xp - current_level_xp
            
            stats = {
                'total_xp': total_xp,
                'level': level,
                'xp_progress': xp_progress,
                'xp_needed': xp_needed,
                'current_streak': current_streak,
                'max_streak': max_streak,
                'last_completion_date': last_date
            }
        else:
            stats = {
                'total_xp': 0,
                'level': 1,
                'xp_progress': 0,
                'xp_needed': 500,
                'current_streak': 0,
                'max_streak': 0,
                'last_completion_date': None
            }
        
        conn.close()
        return stats
    
    def check_and_award_badges(self) -> List[str]:
        """バッジをチェックして授与"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        new_badges = []
        
        # ストリークバッジ
        stats = self.get_user_stats()
        if stats['current_streak'] >= 3:
            badge_type = '3日連続達成'
            cursor.execute('INSERT OR IGNORE INTO badges (badge_type, earned_at) VALUES (?, ?)',
                         (badge_type, datetime.now().isoformat()))
            if cursor.rowcount > 0:
                new_badges.append(badge_type)
        
        # 週間10回達成バッジ
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        cursor.execute('SELECT COUNT(*) FROM pomodoros WHERE completed_at >= ?', (week_ago,))
        week_count = cursor.fetchone()[0]
        
        if week_count >= 10:
            badge_type = '今週10回達成'
            cursor.execute('INSERT OR IGNORE INTO badges (badge_type, earned_at) VALUES (?, ?)',
                         (badge_type, datetime.now().isoformat()))
            if cursor.rowcount > 0:
                new_badges.append(badge_type)
        
        # 初回達成バッジ
        cursor.execute('SELECT COUNT(*) FROM pomodoros')
        total_count = cursor.fetchone()[0]
        
        if total_count == 1:
            badge_type = '初めてのポモドーロ'
            cursor.execute('INSERT OR IGNORE INTO badges (badge_type, earned_at) VALUES (?, ?)',
                         (badge_type, datetime.now().isoformat()))
            if cursor.rowcount > 0:
                new_badges.append(badge_type)
        
        # 10回達成バッジ
        if total_count >= 10:
            badge_type = '合計10回達成'
            cursor.execute('INSERT OR IGNORE INTO badges (badge_type, earned_at) VALUES (?, ?)',
                         (badge_type, datetime.now().isoformat()))
            if cursor.rowcount > 0:
                new_badges.append(badge_type)
        
        # 50回達成バッジ
        if total_count >= 50:
            badge_type = '合計50回達成'
            cursor.execute('INSERT OR IGNORE INTO badges (badge_type, earned_at) VALUES (?, ?)',
                         (badge_type, datetime.now().isoformat()))
            if cursor.rowcount > 0:
                new_badges.append(badge_type)
        
        conn.commit()
        conn.close()
        
        return new_badges
    
    def get_badges(self) -> List[Dict]:
        """獲得したバッジを取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute('SELECT badge_type, earned_at FROM badges ORDER BY earned_at DESC')
        rows = cursor.fetchall()
        
        badges = [{'type': row[0], 'earned_at': row[1]} for row in rows]
        
        conn.close()
        return badges
    
    def get_weekly_stats(self) -> Dict:
        """週間統計を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        week_ago = (datetime.now() - timedelta(days=7)).isoformat()
        
        # 今週の完了数
        cursor.execute('SELECT COUNT(*) FROM pomodoros WHERE completed_at >= ?', (week_ago,))
        week_count = cursor.fetchone()[0]
        
        # 今週の日別データ
        cursor.execute('''
            SELECT DATE(completed_at) as date, COUNT(*) as count
            FROM pomodoros
            WHERE completed_at >= ?
            GROUP BY DATE(completed_at)
            ORDER BY date
        ''', (week_ago,))
        
        daily_data = {row[0]: row[1] for row in cursor.fetchall()}
        
        # 7日分のデータを作成
        daily_counts = []
        for i in range(7):
            date = (datetime.now().date() - timedelta(days=6-i)).isoformat()
            count = daily_data.get(date, 0)
            daily_counts.append({'date': date, 'count': count})
        
        # 完了率（目標: 1日1回として7回）
        completion_rate = min(100, (week_count / 7) * 100)
        
        conn.close()
        
        return {
            'total_count': week_count,
            'daily_counts': daily_counts,
            'completion_rate': round(completion_rate, 1)
        }
    
    def get_monthly_stats(self) -> Dict:
        """月間統計を取得"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        month_ago = (datetime.now() - timedelta(days=30)).isoformat()
        
        # 今月の完了数
        cursor.execute('SELECT COUNT(*) FROM pomodoros WHERE completed_at >= ?', (month_ago,))
        month_count = cursor.fetchone()[0]
        
        # 平均集中時間（分）
        cursor.execute('SELECT AVG(duration) FROM pomodoros WHERE completed_at >= ?', (month_ago,))
        avg_duration = cursor.fetchone()[0] or 0
        
        # 完了率（目標: 1日1回として30回）
        completion_rate = min(100, (month_count / 30) * 100)
        
        conn.close()
        
        return {
            'total_count': month_count,
            'avg_duration': round(avg_duration, 1),
            'completion_rate': round(completion_rate, 1)
        }
