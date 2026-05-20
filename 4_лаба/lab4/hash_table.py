"""
Лабораторная работа №4
Хеш-таблицы с квадратичным пробированием
Тематика: Биология (Вариант 4)

Модуль реализует структуру данных хеш-таблицы с CRUD операциями
и методом квадратичного пробирования для разрешения коллизий.
"""

from typing import Optional, List, Tuple


# Константы для хеш-таблицы
ALPHABET_RUSSIAN = 'АБВГДЕЁЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ'
ALPHABET_BASE = len(ALPHABET_RUSSIAN)  # 33 буквы
DEFAULT_TABLE_SIZE = 20
DEFAULT_BASE_ADDRESS = 0


class HashTableCell:
    """
    Структура ячейки хеш-таблицы согласно Рисунок 1 из методички.
    
    Атрибуты:
        id: Ключевое слово (идентификатор)
        collision: Флаг коллизии (C)
        used: Флаг занятости (U)
        terminal: Терминальный флаг (T)
        is_pointer: Флаг связи - данные или указатель (L)
        deleted: Флаг удаления (D)
        next_address: Указатель на следующую запись (P0)
        data: Данные (Pi)
        value: Числовое значение ключа V
        hash_address: Хеш-адрес h
    """
    
    def __init__(self) -> None:
        """Инициализация ячейки хеш-таблицы в пустом состоянии."""
        self.id: Optional[str] = None
        self.collision: bool = False
        self.used: bool = False
        self.terminal: bool = True
        self.is_pointer: bool = False
        self.deleted: bool = False
        self.next_address: int = -1
        self.data: Optional[str] = None
        self.value: int = 0
        self.hash_address: int = 0
    
    def is_empty(self) -> bool:
        """
        Проверка ячейки на пустоту.
        
        Returns:
            True если ячейка никогда не использовалась
        """
        return not self.used and not self.deleted
    
    def is_deleted(self) -> bool:
        """
        Проверка ячейки на удаленную.
        
        Returns:
            True если ячейка помечена как удаленная
        """
        return self.deleted
    
    def reset(self) -> None:
        """Сброс ячейки в начальное состояние."""
        self.id = None
        self.collision = False
        self.used = False
        self.terminal = True
        self.is_pointer = False
        self.deleted = False
        self.next_address = -1
        self.data = None
        self.value = 0
        self.hash_address = 0
    
    def __repr__(self) -> str:
        return (f"Cell(ID={self.id}, V={self.value}, h={self.hash_address}, "
                f"C={int(self.collision)}, U={int(self.used)}, T={int(self.terminal)}, "
                f"L={int(self.is_pointer)}, D={int(self.deleted)}, P0={self.next_address})")


class HashTable:
    """
    Хеш-таблица с квадратичным пробированием для разрешения коллизий.
    
    Реализует CRUD операции:
        - insert: Вставка записи
        - search: Поиск записи
        - update: Обновление записи
        - delete: Удаление записи
    
    При квадратичном пробировании: h(k, i) = (h(k) + c1*i + c2*i^2) mod H
    Здесь используем упрощённую форму: (h(k) + i^2) mod H
    
    Атрибуты:
        size: Количество строк в таблице (H)
        base_address: Начальный адрес таблицы (B)
        table: Список ячеек хеш-таблицы
        insertion_order: Счетчик для генерации ID
    """
    
    def __init__(self, size: int = DEFAULT_TABLE_SIZE, base_address: int = DEFAULT_BASE_ADDRESS) -> None:
        """
        Инициализация хеш-таблицы.
        
        Args:
            size: Количество строк в таблице (H >= 20)
            base_address: Начальный адрес таблицы (B)
        """
        self.size: int = size
        self.base_address: int = base_address
        self.table: List[HashTableCell] = [HashTableCell() for _ in range(size)]
        self.insertion_order: int = 0
    
    def _compute_value(self, key: str) -> int:
        """
        Вычисление числового значения ключа V по первым двум буквам.
        
        Формула: V = first_char * 33^1 + second_char * 33^0
        
        Args:
            key: Ключевое слово (минимум 2 символа)
        
        Returns:
            Числовое значение V
        """
        if len(key) < 2:
            key = key.ljust(2, 'А')
        
        first_char: str = key[0].upper()
        second_char: str = key[1].upper()
        
        first_idx: int = ALPHABET_RUSSIAN.find(first_char)
        second_idx: int = ALPHABET_RUSSIAN.find(second_char)
        
        if first_idx == -1:
            first_idx = ord(first_char) % ALPHABET_BASE
        if second_idx == -1:
            second_idx = ord(second_char) % ALPHABET_BASE
        
        return first_idx * ALPHABET_BASE + second_idx
    
    def _compute_hash(self, value: int) -> int:
        """
        Вычисление хеш-адреса h(V).
        
        Формула: h(V) = V mod H + B
        
        Args:
            value: Числовое значение ключа V
        
        Returns:
            Хеш-адрес
        """
        return (value % self.size) + self.base_address
    
    def _probe_quadratic(self, hash_addr: int, i: int) -> int:
        """
        Квадратичное пробирование для поиска слота.
        
        Формула: h(k, i) = (h(k) + i^2) mod H
        
        Args:
            hash_addr: Базовый хеш-адрес h(k)
            i: Номер итерации пробинга
        
        Returns:
            Вычисленный адрес для проверки
        """
        return (hash_addr + i * i) % self.size
    
    def _find_slot_quadratic(self, key: str, hash_addr: int) -> Tuple[Optional[int], bool]:
        """
        Поиск слота с помощью квадратичного пробирования.
        
        Args:
            key: Ключ для поиска
            hash_addr: Базовый хеш-адрес
        
        Returns:
            Tuple(адрес слота, найден ли элемент)
        """
        for i in range(self.size):
            probe_addr: int = self._probe_quadratic(hash_addr, i)
            cell: HashTableCell = self.table[probe_addr]
            
            # Если встретили свободную (никогда не использованную) ячейку
            if cell.is_empty():
                return probe_addr, False
            
            # Если нашли искомый ключ
            if cell.used and not cell.deleted and cell.id == key:
                return probe_addr, True
        
        return None, False
    
    def _handle_collision_quadratic(self, hash_addr: int, key: str) -> Tuple[int, int]:
        """
        Обработка коллизии с помощью квадратичного пробирования.
        
        Args:
            hash_addr: Базовый хеш-адрес где произошла коллизия
            key: Ключ для которого ищем место
        
        Returns:
            Tuple(найденный адрес, номер итерации i)
        
        Raises:
            Exception: Если таблица переполнена
        """
        for i in range(self.size):
            probe_addr: int = self._probe_quadratic(hash_addr, i)
            cell: HashTableCell = self.table[probe_addr]
            
            # Если нашли свободную или удалённую ячейку
            if cell.is_empty() or cell.deleted:
                return probe_addr, i
        
        raise Exception("Хеш-таблица переполнена!")
    
    def insert(self, key: str, data: str) -> Tuple[int, int, bool, int]:
        """
        Вставка записи в хеш-таблицу (Create).
        
        Args:
            key: Ключевое слово (ID)
            data: Данные (определение)
        
        Returns:
            Tuple(хеш-адрес, значение V, произошла ли коллизия, итерация i)
        
        Raises:
            ValueError: Если ключ уже существует
        """
        if self.search(key)[0]:
            raise ValueError(f"Ключ '{key}' уже существует в таблице!")
        
        value: int = self._compute_value(key)
        hash_addr: int = self._compute_hash(value)
        
        self.insertion_order += 1
        
        # Проверяем, есть ли уже ключ в таблице
        found_addr, found = self._find_slot_quadratic(key, hash_addr)
        
        if found:
            raise ValueError(f"Ключ '{key}' уже существует в таблице!")
        
        # Проверяем, свободна ли основная ячейка
        if self.table[hash_addr].is_empty():
            self._insert_direct(hash_addr, key, data, value)
            return hash_addr, value, False, 0
        else:
            # Обрабатываем коллизию квадратичным пробированием
            new_addr, i = self._handle_collision_quadratic(hash_addr, key)
            self._insert_collision(hash_addr, new_addr, key, data, value, i)
            return hash_addr, value, True, i
    
    def _insert_direct(self, addr: int, key: str, data: str, value: int) -> None:
        """Прямая вставка без коллизии."""
        cell: HashTableCell = self.table[addr]
        cell.id = key
        cell.collision = False
        cell.used = True
        cell.terminal = True
        cell.is_pointer = False
        cell.deleted = False
        cell.next_address = addr
        cell.data = data
        cell.value = value
        cell.hash_address = addr
    
    def _insert_collision(self, hash_addr: int, new_addr: int, key: str, 
                          data: str, value: int, i: int) -> None:
        """Вставка при коллизии с обновлением цепочки (квадратичное пробирование)."""
        self.table[hash_addr].terminal = False
        self.table[hash_addr].collision = True
        self.table[hash_addr].next_address = new_addr
        
        cell: HashTableCell = self.table[new_addr]
        cell.id = key
        cell.collision = False
        cell.used = True
        cell.terminal = True
        cell.is_pointer = False
        cell.deleted = False
        cell.next_address = new_addr
        cell.data = data
        cell.value = value
        cell.hash_address = hash_addr
    
    def search(self, key: str) -> Tuple[bool, Optional[str], Optional[int], int]:
        """
        Поиск записей по ключу (Read).
        
        Args:
            key: Ключевое слово
        
        Returns:
            Tuple(найден ли, данные, адрес, хеш-адрес)
        """
        value: int = self._compute_value(key)
        hash_addr: int = self._compute_hash(value)
        
        for i in range(self.size):
            probe_addr: int = self._probe_quadratic(hash_addr, i)
            cell: HashTableCell = self.table[probe_addr]
            
            # Если встретили свободную ячейку — элемент не найден
            if cell.is_empty():
                return False, None, None, hash_addr
            
            # Если нашли элемент и он не удалён
            if cell.used and not cell.deleted and cell.id == key:
                return True, cell.data, probe_addr, hash_addr
        
        return False, None, None, hash_addr
    
    def delete(self, key: str) -> bool:
        """
        Удаление записей по ключу (Delete).
        Устанавливаем флаг вычеркивания D=1 согласно методичке.
        
        Args:
            key: Ключевое слово
        
        Returns:
            True если успешно удалено, False если не найдено
        """
        found, _, addr, _ = self.search(key)
        
        if not found or addr is None:
            return False
        
        cell: HashTableCell = self.table[addr]
        # Устанавливаем флаг вычеркивания D=1
        cell.deleted = True
        
        return True
    
    def update(self, key: str, new_data: str) -> bool:
        """
        Обновление данных по ключу (Update).
        
        Args:
            key: Ключевое слово
            new_data: Новые данные
        
        Returns:
            True если успешно обновлено, False если не найдено
        """
        found: bool
        _, _, addr = self.search(key)
        
        if not found:
            return False
        
        self.table[addr].data = new_data
        return True
    
    def update(self, key: str, new_data: str) -> bool:
        """
        Обновление данных по ключу (Update).
        
        Args:
            key: ключевое слово
            new_data: новые данные
        
        Returns:
            Успешно ли обновление
        """
        found, _, addr, _ = self.search(key)
        if not found or addr is None:
            return False
        
        self.table[addr].data = new_data
        return True
        """Расчет коэффициента заполнения таблицы."""
        occupied = sum(1 for cell in self.table if cell.used and not cell.deleted)
        return occupied / self.size
    
    def get_collision_count(self) -> int:
        """Подсчет количества коллизий."""
        return sum(1 for cell in self.table if cell.collision)
    
    def get_chain_lengths(self) -> List[int]:
        """Получение длин всех цепочек."""
        chains = []
        visited = set()
        
        for i, cell in enumerate(self.table):
            if cell.used and not cell.deleted and i not in visited:
                # Начинаем новую цепочку
                chain_len = 0
                current = i
                
                while current not in visited and current != -1:
                    visited.add(current)
                    chain_len += 1
                    next_addr = self.table[current].next_address
                    if next_addr == current:
                        break
                    current = next_addr
                
                if chain_len > 0:
                    chains.append(chain_len)
        
        return chains
    
    def display_table(self) -> str:
        """Вывод содержимого хеш-таблицы."""
        lines = []
        lines.append("\n" + "=" * 100)
        lines.append("ХЕШ-ТАБЛИЦА (Биология)")
        lines.append("=" * 100)
        lines.append(f"{'№':>3} | {'ID':>8} | {'Ключ':>12} | {'V':>6} | {'h':>3} | "
                    f"{'C':>2} | {'U':>2} | {'T':>2} | {'L':>2} | {'D':>2} | {'P0':>4} | Данные")
        lines.append("-" * 100)
        
        for i, cell in enumerate(self.table):
            if cell.used:
                key = cell.id if cell.id else ''
                data_preview = (cell.data[:15] + '...') if cell.data and len(cell.data) > 15 else (cell.data or '')
                
                lines.append(f"{i:>3} | {key:>8} | {key:>12} | "
                           f"{cell.value:>6} | {cell.hash_address:>3} | "
                           f"{int(cell.collision):>2} | {int(cell.used):>2} | "
                           f"{int(cell.terminal):>2} | {int(cell.is_pointer):>2} | "
                           f"{int(cell.deleted):>2} | {cell.next_address:>4} | {data_preview}")
            else:
                lines.append(f"{i:>3} | {'--------':>8} | {'':>12} | "
                           f"{'':>6} | {'':>3} | "
                           f"{'':>2} | {'':>2} | {'':>2} | {'':>2} | "
                           f"{'':>2} | {'':>4} | {'':20}")
        
        lines.append("-" * 100)
        lines.append(f"Коэффициент заполнения: {self.get_load_factor():.2%}")
        lines.append(f"Количество коллизий: {self.get_collision_count()}")
        chains = self.get_chain_lengths()
        lines.append(f"Длины цепочек: {chains}")
        lines.append(f"Количество записей: {sum(1 for c in self.table if c.used and not c.deleted)}")
        lines.append("=" * 100 + "\n")
        
        return "\n".join(lines)
    
    def display_detailed(self, key: str) -> str:
        """Вывод подробной информации о записи."""
        found, data, addr = self.search(key)
        
        if not found:
            return f"Запись с ключом '{key}' не найдена."
        
        cell = self.table[addr]
        
        lines = []
        lines.append(f"\n{'=' * 60}")
        lines.append(f"ПОДРОБНАЯ ИНФОРМАЦИЯ О ЗАПИСИ: {key}")
        lines.append(f"{'=' * 60}")
        lines.append(f"ID: {cell.id}")
        lines.append(f"Ключ: {key}")
        lines.append(f"Числовое значение V: {cell.value}")
        lines.append(f"Хеш-адрес h(V): {cell.hash_address}")
        lines.append(f"Физический адрес: {addr}")
        lines.append(f"Данные: {cell.data}")
        lines.append(f"Флажки:")
        lines.append(f"  C (коллизия): {int(cell.collision)}")
        lines.append(f"  U (занято): {int(cell.used)}")
        lines.append(f"  T (терминальный): {int(cell.terminal)}")
        lines.append(f"  L (связь/указатель): {int(cell.is_pointer)}")
        lines.append(f"  D (удалена): {int(cell.deleted)}")
        lines.append(f"P0 (следующий адрес): {cell.next_address}")
        lines.append(f"{'=' * 60}\n")
        
        return "\n".join(lines)


def get_biology_data() -> List[Tuple[str, str]]:
    """Получение тематических данных по Биологии (Вариант 4)."""
    return [
        ("Аминокислота", "Органические соединения, строительные блоки белков"),
        ("Белок", "Сложные макромолекулы, состоящие из аминокислот"),
        ("Вирус", "Микроскопический инфекционный агент"),
        ("Ген", "Единица наследственной информации"),
        ("ДНК", "Дезоксирибонуклеиновая кислота, носитель генетической информации"),
        ("Энзим", "Биологический катализатор, фермент"),
        ("Зоология", "Раздел биологии, изучающий животных"),
        ("Клетка", "Основная структурная и функциональная единица живых организмов"),
        ("Митохондрия", "Органоид клетки, производящий энергию"),
        ("Нуклеотид", "Мономер нуклеиновых кислот (ДНК и РНК)"),
        ("Органоид", "Структурный компонент клетки"),
        ("Популяция", "Группа особей одного вида, обитающих на определенной территории"),
        ("Рибосома", "Органоид клетки, синтезирующий белки"),
        ("Спираль", "Пространственная структура ДНК"),
        ("Ткань", "Группа клеток, выполняющих общую функцию"),
        ("Углевод", "Органические соединения, источник энергии"),
        ("Фаг", "Вирус, поражающий бактерии"),
        ("Хромосома", "Структура в ядре клетки, несущая генетическую информацию"),
        ("Эукариот", "Организм с оформленным ядром"),
        ("Ядро", "Органоид клетки, содержащий генетическую информацию"),
    ]


def main():
    """Главная функция для демонстрации хеш-таблицы."""
    print("=" * 60)
    print("ЛАБОРАТОРНАЯ РАБОТА №4")
    print("Хеш-таблицы с квадратичным пробированием")
    print("Тематика: Биология (Вариант 4)")
    print("=" * 60)
    
    # Создаем хеш-таблицу
    ht = HashTable(size=20, base_address=0)
    
    # Вставляем начальные данные (не менее 10 записей)
    biology_data = get_biology_data()
    
    print("\n1. Вставка начальных данных...")
    collisions = 0
    for key, data in biology_data[:15]:  # Вставляем 15 записей
        try:
            hash_addr, value, collision, i = ht.insert(key, data)
            if collision:
                collisions += 1
                print(f"  {key}: V={value}, h={hash_addr}, позиция={(hash_addr + i*i) % 20}, коллизия=True, i={i}")
            else:
                print(f"  {key}: V={value}, h={hash_addr}, коллизия=False")
        except ValueError as e:
            print(f"  {key}: {e}")
    
    print(ht.display_table())
    
    # Поиск
    print("2. Поиск записей...")
    search_keys = ["Аминокислота", "Вирус", "НеСуществует"]
    for key in search_keys:
        found, data, addr, hash_addr = ht.search(key)
        if found:
            print(f"  {key}: НАЙДЕНА, данные: {data}, адрес: {addr}, h={hash_addr}")
        else:
            print(f"  {key}: НЕ НАЙДЕНА, h={hash_addr}")
    
    # Обновление
    print("\n3. Обновление записи...")
    if ht.update("Вирус", "Микроскопический инфекционный агент (ОБНОВЛЕНО)"):
        print("  Вирус: успешно обновлен")
    
    # Удаление
    print("\n4. Удаление записи...")
    if ht.delete("Зоология"):
        print("  Зоология: успешно удалена (флаг D=1)")
    
    # Вставка после удаления
    print("\n5. Вставка новой записи...")
    try:
        hash_addr, value, collision, i = ht.insert("Бактерия", "Одноклеточные микроорганизмы")
        if collision:
            print(f"  Бактерия: V={value}, h={hash_addr}, позиция={(hash_addr + i*i) % 20}, коллизия=True, i={i}")
        else:
            print(f"  Бактерия: V={value}, h={hash_addr}, коллизия=False")
    except ValueError as e:
        print(f"  Бактерия: {e}")
    
    print(ht.display_table())
    
    # Проверка требований
    print("6. Проверка требований:")
    print(f"  Размер таблицы: {ht.size} (требуется >= 20)")
    print(f"  Количество записей: {sum(1 for c in ht.table if c.used and not c.deleted)} (требуется >= 10)")
    print(f"  Количество коллизий: {ht.get_collision_count()} (требуется >= 2)")
    chains = ht.get_chain_lengths()
    long_chains = [c for c in chains if c > 1]
    print(f"  Количество цепочек: {len(long_chains)} (требуется >= 3 с длиной > 1)")
    print(f"  Метод разрешения коллизий: Квадратичное пробирование h(k,i) = (h(k) + i²) mod H")
    
    # Интерактивный режим
    print("\n7. Интерактивный режим:")
    print("  Команды:")
    print("    insert <ключ> <данные> - вставка записи")
    print("    search <ключ> - поиск записи")
    print("    update <ключ> <новые данные> - обновление записи")
    print("    delete <ключ> - удаление записи")
    print("    show - показать таблицу")
    print("    exit - выход")
    
    while True:
        try:
            cmd = input("\n> ").strip().split(maxsplit=3)
            if not cmd:
                continue
            
            command = cmd[0].lower()
            
            if command == 'exit':
                print("Выход из программы.")
                break
            elif command == 'show':
                print(ht.display_table())
            elif command == 'insert' and len(cmd) >= 3:
                key = cmd[1]
                data = cmd[2]
                try:
                    hash_addr, value, collision, i = ht.insert(key, data)
                    if collision:
                        print(f"  Успешно: V={value}, h={hash_addr}, позиция={(hash_addr + i*i) % ht.size}, i={i}")
                    else:
                        print(f"  Успешно: V={value}, h={hash_addr}")
                except ValueError as e:
                    print(f"  Ошибка: {e}")
            elif command == 'search' and len(cmd) >= 2:
                key = cmd[1]
                found, data, addr, hash_addr = ht.search(key)
                if found:
                    print(f"  Найдена: данные = {data}, адрес = {addr}, h = {hash_addr}")
                else:
                    print(f"  Не найдена, h = {hash_addr}")
            elif command == 'update' and len(cmd) >= 3:
                key = cmd[1]
                new_data = cmd[2]
                if ht.update(key, new_data):
                    print(f"  Успешно обновлено")
                else:
                    print(f"  Запись не найдена")
            elif command == 'delete' and len(cmd) >= 2:
                key = cmd[1]
                if ht.delete(key):
                    print(f"  Успешно удалено (флаг D=1)")
                else:
                    print(f"  Запись не найдена")
            else:
                print("  Неверная команда. Используйте: insert, search, update, delete, show, exit")
        
        except KeyboardInterrupt:
            print("\nВыход из программы.")
            break
        except Exception as e:
            print(f"  Ошибка: {e}")


if __name__ == "__main__":
    main()
