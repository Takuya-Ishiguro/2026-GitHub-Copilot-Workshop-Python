"""
Pythonロジックのテスト
"""

import pytest
import sys
import os
from datetime import datetime

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from logic import (
    format_time,
    calculate_progress_percentage,
    get_today_date,
    create_progress_data,
    add_pomodoro_completion,
    POMODORO_MINUTES,
    POMODORO_SECONDS
)


class TestFormatTime:
    """format_time関数のテスト"""
    
    def test_format_zero_seconds(self):
        """0秒が正しくフォーマットされることをテスト"""
        assert format_time(0) == "00:00"
    
    def test_format_full_pomodoro(self):
        """25分が正しくフォーマットされることをテスト"""
        assert format_time(1500) == "25:00"
    
    def test_format_with_seconds(self):
        """分と秒が正しくフォーマットされることをテスト"""
        assert format_time(90) == "01:30"
        assert format_time(305) == "05:05"
    
    def test_format_single_digit(self):
        """1桁の数字がゼロパディングされることをテスト"""
        assert format_time(65) == "01:05"
        assert format_time(9) == "00:09"
    
    def test_format_negative_raises_error(self):
        """負の値でValueErrorが発生することをテスト"""
        with pytest.raises(ValueError, match="秒数は0以上である必要があります"):
            format_time(-1)


class TestCalculateProgressPercentage:
    """calculate_progress_percentage関数のテスト"""
    
    def test_no_progress(self):
        """開始時の進捗が0%であることをテスト"""
        assert calculate_progress_percentage(1500, 1500) == 0.0
    
    def test_half_progress(self):
        """半分の進捗が50%であることをテスト"""
        assert calculate_progress_percentage(750, 1500) == 50.0
    
    def test_full_progress(self):
        """完了時の進捗が100%であることをテスト"""
        assert calculate_progress_percentage(0, 1500) == 100.0
    
    def test_quarter_progress(self):
        """1/4の進捗が25%であることをテスト"""
        result = calculate_progress_percentage(1125, 1500)
        assert result == 25.0
    
    def test_negative_time_left(self):
        """負の残り時間が0として扱われることをテスト"""
        assert calculate_progress_percentage(-100, 1500) == 100.0
    
    def test_time_left_exceeds_total(self):
        """残り時間が総時間を超える場合に0%になることをテスト"""
        assert calculate_progress_percentage(2000, 1500) == 0.0
    
    def test_zero_total_time_raises_error(self):
        """総時間が0でValueErrorが発生することをテスト"""
        with pytest.raises(ValueError, match="総時間は0より大きい必要があります"):
            calculate_progress_percentage(100, 0)


class TestGetTodayDate:
    """get_today_date関数のテスト"""
    
    def test_date_format(self):
        """日付がYYYY-MM-DD形式であることをテスト"""
        date = get_today_date()
        assert len(date) == 10
        assert date[4] == '-'
        assert date[7] == '-'
    
    def test_date_is_today(self):
        """返される日付が今日の日付であることをテスト"""
        expected = datetime.now().strftime("%Y-%m-%d")
        assert get_today_date() == expected


class TestCreateProgressData:
    """create_progress_data関数のテスト"""
    
    def test_default_values(self):
        """デフォルト値で進捗データが作成されることをテスト"""
        data = create_progress_data()
        assert data["pomodoro_count"] == 0
        assert data["total_minutes"] == 0
        assert "date" in data
    
    def test_custom_values(self):
        """カスタム値で進捗データが作成されることをテスト"""
        data = create_progress_data(5, 125)
        assert data["pomodoro_count"] == 5
        assert data["total_minutes"] == 125
    
    def test_includes_today_date(self):
        """今日の日付が含まれることをテスト"""
        data = create_progress_data()
        expected_date = get_today_date()
        assert data["date"] == expected_date


class TestAddPomodoroCompletion:
    """add_pomodoro_completion関数のテスト"""
    
    def test_increment_count(self):
        """ポモドーロ回数が増加することをテスト"""
        initial_data = create_progress_data(3, 75)
        updated_data = add_pomodoro_completion(initial_data)
        assert updated_data["pomodoro_count"] == 4
    
    def test_add_minutes(self):
        """総時間が25分増加することをテスト"""
        initial_data = create_progress_data(3, 75)
        updated_data = add_pomodoro_completion(initial_data)
        assert updated_data["total_minutes"] == 100
    
    def test_update_date(self):
        """日付が更新されることをテスト"""
        initial_data = {"date": "2020-01-01", "pomodoro_count": 0, "total_minutes": 0}
        updated_data = add_pomodoro_completion(initial_data)
        assert updated_data["date"] == get_today_date()
    
    def test_original_data_unchanged(self):
        """元のデータが変更されないことをテスト（イミュータブル）"""
        initial_data = create_progress_data(3, 75)
        original_count = initial_data["pomodoro_count"]
        add_pomodoro_completion(initial_data)
        assert initial_data["pomodoro_count"] == original_count


class TestConstants:
    """定数のテスト"""
    
    def test_pomodoro_minutes(self):
        """ポモドーロの分数が25分であることをテスト"""
        assert POMODORO_MINUTES == 25
    
    def test_pomodoro_seconds(self):
        """ポモドーロの秒数が1500秒であることをテスト"""
        assert POMODORO_SECONDS == 1500
        assert POMODORO_SECONDS == POMODORO_MINUTES * 60
