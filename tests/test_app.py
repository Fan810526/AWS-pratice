# -*- coding: utf-8 -*-
import unittest
import json
import os
import sys

# 將專案根目錄與 src 加入 Python Path，以便導入 app
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.app import app

class FlaskAppTestCase(unittest.TestCase):
    def setUp(self):
        # 設定測試模式
        app.config['TESTING'] = True
        self.client = app.test_client()

    def test_home_page(self):
        """測試首頁網頁是否載入成功並且包含關鍵字"""
        response = self.client.get('/')
        self.assertEqual(response.status_code, 200)
        html_content = response.get_data(as_text=True)
        self.assertIn('Flask', html_content)
        self.assertIn('19191', html_content)

    def test_api_info(self):
        """測試 API 端點是否回傳正確的 JSON 格式及專案資訊"""
        response = self.client.get('/api/info')
        self.assertEqual(response.status_code, 200)
        
        # 載入並驗證 JSON 資料
        html_content = response.get_data(as_text=True)
        data = json.loads(html_content)
        self.assertEqual(data['status'], 'success')
        self.assertEqual(data['port'], 19191)
        self.assertIn('python_version', data)

    def test_api_stocks(self):
        """測試股票 API 是否正確回傳股票行情陣列及欄位"""
        response = self.client.get('/api/stocks')
        self.assertEqual(response.status_code, 200)
        
        html_content = response.get_data(as_text=True)
        data = json.loads(html_content)
        
        # 應為列表格式，且包含 5 檔預設股票
        self.assertIsInstance(data, list)
        self.assertEqual(len(data), 5)
        
        # 驗證首筆股票資料欄位
        first_stock = data[0]
        self.assertIn('symbol', first_stock)
        self.assertIn('name', first_stock)
        self.assertIn('price', first_stock)
        self.assertIn('change_percent', first_stock)
        self.assertIn('history', first_stock)
        self.assertIsInstance(first_stock['history'], list)

    def test_api_companies(self):
        """測試企業搜尋 API 及其篩選參數功能"""
        # 1. 測試無參數回傳全部 (共 7 筆)
        response = self.client.get('/api/companies')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.get_data(as_text=True))
        self.assertEqual(len(data), 7)
        
        # 2. 測試只篩選「下午班 (afternoon)」(共 5 筆)
        response_afternoon = self.client.get('/api/companies?shift=afternoon')
        data_afternoon = json.loads(response_afternoon.get_data(as_text=True))
        self.assertEqual(len(data_afternoon), 5)
        for c in data_afternoon:
            self.assertEqual(c['shift'], 'afternoon')
            
        # 3. 測試關鍵字搜尋 "MSI" (微星科技)
        response_msi = self.client.get('/api/companies?keyword=MSI')
        data_msi = json.loads(response_msi.get_data(as_text=True))
        self.assertEqual(len(data_msi), 1)
        self.assertEqual(data_msi[0]['id'], 2)
        self.assertIn(u'微星科技', data_msi[0]['name'])

        # 4. 測試無相符結果
        response_empty = self.client.get('/api/companies?keyword=NonExistentCompany')
        data_empty = json.loads(response_empty.get_data(as_text=True))
        self.assertEqual(len(data_empty), 0)

if __name__ == '__main__':
    unittest.main()
