"""Тесты для хеш-таблицы."""

import unittest
from hash_table import HashTable, HashTableCell


class TestHashTableCell(unittest.TestCase):
    """Тесты ячейки хеш-таблицы."""
    
    def test_init(self):
        """Тест инициализации ячейки."""
        cell = HashTableCell()
        self.assertFalse(cell.used)
        self.assertTrue(cell.terminal)
        self.assertEqual(cell.next_address, -1)
    
    def test_is_empty(self):
        """Тест проверки на пустоту."""
        cell = HashTableCell()
        self.assertTrue(cell.is_empty())
        cell.used = True
        self.assertFalse(cell.is_empty())


class TestHashTable(unittest.TestCase):
    """Тесты хеш-таблицы."""
    
    def setUp(self):
        """Настройка тестов."""
        self.ht = HashTable(size=20, base_address=0)
    
    def test_init(self):
        """Тест инициализации."""
        self.assertEqual(self.ht.size, 20)
        self.assertEqual(self.ht.base_address, 0)
        self.assertEqual(len(self.ht.table), 20)
    
    def test_compute_value(self):
        """Тест вычисления значения ключа."""
        self.assertEqual(self.ht._compute_value("Аминокислота"), 13)
        self.assertEqual(self.ht._compute_value("Белок"), 38)
    
    def test_compute_hash(self):
        """Тест вычисления хеш-адреса."""
        self.assertEqual(self.ht._compute_hash(13), 13)
        self.assertEqual(self.ht._compute_hash(38), 18)
    
    def test_insert(self):
        """Тест вставки."""
        hash_addr, value, collision = self.ht.insert("Аминокислота", "Определение")
        self.assertEqual(value, 13)
        self.assertEqual(hash_addr, 13)
        self.assertFalse(collision)
    
    def test_search_found(self):
        """Тест успешного поиска."""
        self.ht.insert("Аминокислота", "Определение")
        found, data, addr = self.ht.search("Аминокислота")
        self.assertTrue(found)
        self.assertEqual(data, "Определение")
        self.assertEqual(addr, 13)
    
    def test_search_not_found(self):
        """Тест поиска несуществующего."""
        found, data, addr = self.ht.search("НеСуществует")
        self.assertFalse(found)
        self.assertIsNone(data)
        self.assertIsNone(addr)
    
    def test_update(self):
        """Тест обновления."""
        self.ht.insert("Аминокислота", "Определение 1")
        result = self.ht.update("Аминокислота", "Определение 2")
        self.assertTrue(result)
        found, data, _ = self.ht.search("Аминокислота")
        self.assertTrue(found)
        self.assertEqual(data, "Определение 2")
    
    def test_delete(self):
        """Тест удаления."""
        self.ht.insert("Аминокислота", "Определение")
        result = self.ht.delete("Аминокислота")
        self.assertTrue(result)
        found, _, _ = self.ht.search("Аминокислота")
        self.assertFalse(found)
    
    def test_duplicate_key(self):
        """Тест дубликата ключа."""
        self.ht.insert("Аминокислота", "Определение 1")
        with self.assertRaises(ValueError):
            self.ht.insert("Аминокислота", "Определение 2")
    
    def test_collision(self):
        """Тест обработки коллизий."""
        self.ht.insert("Ген", "Определение 1")  # h=4
        self.ht.insert("Энзим", "Определение 2")  # h=4, коллизия
        found1, _, _ = self.ht.search("Ген")
        found2, _, _ = self.ht.search("Энзим")
        self.assertTrue(found1)
        self.assertTrue(found2)
    
    def test_load_factor(self):
        """Тест коэффициента заполнения."""
        self.assertEqual(self.ht.get_load_factor(), 0.0)
        for i in range(10):
            self.ht.insert(f"Key{i}", f"Data{i}")
        self.assertEqual(self.ht.get_load_factor(), 0.5)
    
    def test_chain_lengths(self):
        """Тест длин цепочек."""
        self.ht.insert("Ген", "Определение 1")  # h=4
        self.ht.insert("Энзим", "Определение 2")  # h=4, коллизия
        chains = self.ht.get_chain_lengths()
        self.assertIn(2, chains)  # Должна быть цепочка длины 2
    
    def test_collision_count(self):
        """Тест подсчета коллизий."""
        self.ht.insert("Ген", "Определение 1")
        self.ht.insert("Энзим", "Определение 2")  # Коллизия
        self.assertEqual(self.ht.get_collision_count(), 1)


class TestBiologyData(unittest.TestCase):
    """Тесты с биологическими данными."""
    
    def setUp(self):
        """Настройка тестов."""
        self.ht = HashTable(size=20, base_address=0)
        # Вставляем 15 записей
        self.data = [
            ("Аминокислота", "Органические соединения"),
            ("Белок", "Макромолекулы"),
            ("Вирус", "Инфекционный агент"),
            ("Ген", "Единица наследственности"),
            ("ДНК", "Носитель информации"),
            ("Энзим", "Фермент"),
            ("Зоология", "Наука о животных"),
            ("Клетка", "Единица живого"),
            ("Митохондрия", "Производитель энергии"),
            ("Нуклеотид", "Мономер ДНК"),
            ("Органоид", "Структура клетки"),
            ("Популяция", "Группа особей"),
            ("Рибосома", "Синтез белка"),
            ("Спираль", "Структура ДНК"),
            ("Ткань", "Группа клеток"),
        ]
        for key, data in self.data:
            self.ht.insert(key, data)
    
    def test_all_inserted(self):
        """Тест всех записей."""
        count = sum(1 for c in self.ht.table if c.used and not c.deleted)
        self.assertEqual(count, 15)
    
    def test_all_searchable(self):
        """Тест поиска всех записей."""
        for key, _ in self.data:
            found, _, _ = self.ht.search(key)
            self.assertTrue(found, f"{key} не найдена")
    
    def test_requirements(self):
        """Тест требований."""
        # Размер таблицы >= 20
        self.assertGreaterEqual(self.ht.size, 20)
        # Количество записей >= 10
        count = sum(1 for c in self.ht.table if c.used and not c.deleted)
        self.assertGreaterEqual(count, 10)
        # Количество коллизий >= 2
        self.assertGreaterEqual(self.ht.get_collision_count(), 2)
        # Количество цепочек >= 3
        chains = self.ht.get_chain_lengths()
        long_chains = [c for c in chains if c > 1]
        self.assertGreaterEqual(len(long_chains), 3)


if __name__ == "__main__":
    unittest.main()
