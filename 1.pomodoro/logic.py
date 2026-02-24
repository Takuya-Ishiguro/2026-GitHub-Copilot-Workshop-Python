"""
ポモドーロタイマーのビジネスロジック

タイマーや進捗管理などのロジックをFlaskルートやJSから分離し、
単体テスト可能な関数・クラスとして実装します。
"""

from datetime import datetime
from typing import Dict


# 定数
POMODORO_MINUTES = 25
POMODORO_SECONDS = POMODORO_MINUTES * 60


def format_time(seconds: int) -> str:
    """秒数をMM:SS形式にフォーマット
    
    Args:
        seconds: 秒数
    
    Returns:
        str: フォーマットされた時間文字列（例: "25:00"）
    
    Raises:
        ValueError: 秒数が負の値の場合
    """
    if seconds < 0:
        raise ValueError("秒数は0以上である必要があります")
    
    mins = seconds // 60
    secs = seconds % 60
    return f"{mins:02d}:{secs:02d}"


def calculate_progress_percentage(time_left: int, total_time: int = POMODORO_SECONDS) -> float:
    """進捗率を計算
    
    Args:
        time_left: 残り時間（秒）
        total_time: 総時間（秒）デフォルトは25分
    
    Returns:
        float: 進捗率（0.0〜100.0）
    
    Raises:
        ValueError: total_timeが0以下の場合
    """
    if total_time <= 0:
        raise ValueError("総時間は0より大きい必要があります")
    
    if time_left < 0:
        time_left = 0
    if time_left > total_time:
        time_left = total_time
    
    elapsed = total_time - time_left
    percentage = (elapsed / total_time) * 100
    return round(percentage, 2)


def get_today_date() -> str:
    """今日の日付を取得
    
    Returns:
        str: YYYY-MM-DD形式の日付文字列
    """
    return datetime.now().strftime("%Y-%m-%d")


def create_progress_data(pomodoro_count: int = 0, total_minutes: int = 0) -> Dict[str, any]:
    """進捗データを作成
    
    Args:
        pomodoro_count: 完了したポモドーロ数
        total_minutes: 総集中時間（分）
    
    Returns:
        dict: 進捗データ
    """
    return {
        "date": get_today_date(),
        "pomodoro_count": pomodoro_count,
        "total_minutes": total_minutes
    }


def add_pomodoro_completion(progress_data: Dict[str, any]) -> Dict[str, any]:
    """ポモドーロ完了を記録
    
    Args:
        progress_data: 現在の進捗データ
    
    Returns:
        dict: 更新された進捗データ
    """
    new_data = progress_data.copy()
    new_data["pomodoro_count"] += 1
    new_data["total_minutes"] += POMODORO_MINUTES
    new_data["date"] = get_today_date()
    return new_data
