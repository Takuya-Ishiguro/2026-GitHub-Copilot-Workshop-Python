"""
Flaskアプリのテスト
"""

import pytest
import sys
import os

# 親ディレクトリをパスに追加
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app


@pytest.fixture
def app():
    """テスト用アプリケーションを作成"""
    app = create_app({'TESTING': True})
    return app


@pytest.fixture
def client(app):
    """テスト用クライアントを作成"""
    return app.test_client()


class TestApp:
    """Flaskアプリケーションのテスト"""
    
    def test_app_creation(self, app):
        """アプリケーションが正しく作成されることをテスト"""
        assert app is not None
        assert app.config['TESTING'] is True
    
    def test_index_route(self, client):
        """メインページが正しく表示されることをテスト"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'<!DOCTYPE html>' in response.data
    
    def test_index_contains_title(self, client):
        """メインページにタイトルが含まれることをテスト"""
        response = client.get('/')
        assert b'\xe3\x83\x9d\xe3\x83\xa2\xe3\x83\x89\xe3\x83\xbc\xe3\x83\xad\xe3\x82\xbf\xe3\x82\xa4\xe3\x83\x9e\xe3\x83\xbc' in response.data  # ポモドーロタイマー in UTF-8
    
    def test_index_contains_timer(self, client):
        """メインページにタイマー要素が含まれることをテスト"""
        response = client.get('/')
        assert b'id="timer"' in response.data
    
    def test_index_contains_buttons(self, client):
        """メインページにボタンが含まれることをテスト"""
        response = client.get('/')
        assert b'id="startBtn"' in response.data
        assert b'id="resetBtn"' in response.data
    
    def test_index_contains_progress(self, client):
        """メインページに進捗表示が含まれることをテスト"""
        response = client.get('/')
        assert b'id="pomodoroCount"' in response.data
        assert b'id="totalTime"' in response.data
    
    def test_health_endpoint(self, client):
        """ヘルスチェックエンドポイントが正しく動作することをテスト"""
        response = client.get('/health')
        assert response.status_code == 200
        assert response.json == {'status': 'ok'}
    
    def test_404_error(self, client):
        """存在しないページで404が返されることをテスト"""
        response = client.get('/nonexistent')
        assert response.status_code == 404
