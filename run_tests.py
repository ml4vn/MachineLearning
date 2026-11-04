"""Chạy kiểm thử toán, dữ liệu mô phỏng và trường hợp biên của cả 10 bài."""
import unittest

if __name__ == "__main__":
    suite = unittest.defaultTestLoader.loadTestsFromNames([f"examples.bai{i:02d}.tests" for i in range(1, 11)])
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    raise SystemExit(0 if result.wasSuccessful() else 1)
