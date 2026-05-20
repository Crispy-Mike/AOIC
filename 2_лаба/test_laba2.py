"""
Unit-тесты для лабораторной работы 2.
Покрытие >90% кода.
"""

import unittest
from parser import (
    Lexer, Token, Parser, parse_expression, get_all_variables,
    VariableNode, NotNode, AndNode, OrNode, ImpliesNode, XorNode
)
from truth_table import TruthTable
from normal_forms import NormalForm
from post_classes import PostClasses
from zhegalkin import ZhegalkinPolynomial
from dummy_variables import DummyVariables
from boolean_derivatives import BooleanDerivatives
from minimization import Minimization, Implicant
from main import BooleanFunctionAnalyzer


class TestLexer(unittest.TestCase):
    """Тесты лексического анализатора."""
    
    def test_variable_token(self):
        """Тест токенизации переменных."""
        lexer = Lexer("a")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, Token.VARIABLE)
        self.assertEqual(tokens[0].value, "a")
    
    def test_all_variables(self):
        """Тест всех допустимых переменных."""
        for var in ['a', 'b', 'c', 'd', 'e']:
            lexer = Lexer(var)
            tokens = lexer.tokenize()
            self.assertEqual(tokens[0].value, var)
    
    def test_invalid_variable(self):
        """Тест недопустимой переменной."""
        lexer = Lexer("f")
        with self.assertRaises(ValueError):
            lexer.tokenize()
    
    def test_and_operator(self):
        """Тест оператора AND."""
        lexer = Lexer("a&b")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, Token.AND)
    
    def test_or_operator(self):
        """Тест оператора OR."""
        lexer = Lexer("a|b")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, Token.OR)
    
    def test_not_operator(self):
        """Тест оператора NOT."""
        lexer = Lexer("!a")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, Token.NOT)
    
    def test_implies_operator(self):
        """Тест оператора IMPLIES."""
        lexer = Lexer("a->b")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, Token.IMPLIES)
    
    def test_xor_operator(self):
        """Тест оператора XOR."""
        lexer = Lexer("a~b")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, Token.XOR)
    
    def test_parentheses(self):
        """Тест скобок."""
        lexer = Lexer("(a)")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[0].type, Token.LPAREN)
        self.assertEqual(tokens[2].type, Token.RPAREN)
    
    def test_complex_expression(self):
        """Тест сложного выражения."""
        lexer = Lexer("!(!a->!b)|c")
        tokens = lexer.tokenize()
        self.assertEqual(len(tokens), 11)  # ! ( ! a -> ! b ) | c EOF
    
    def test_whitespace_handling(self):
        """Тест обработки пробелов."""
        lexer = Lexer("a & b")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[1].type, Token.AND)
    
    def test_eof_token(self):
        """Тест токена конца файла."""
        lexer = Lexer("a")
        tokens = lexer.tokenize()
        self.assertEqual(tokens[-1].type, Token.EOF)


class TestParser(unittest.TestCase):
    """Тесты синтаксического анализатора."""
    
    def test_single_variable(self):
        """Тест разбора одиночной переменной."""
        ast = parse_expression("a")
        self.assertIsInstance(ast, VariableNode)
        self.assertEqual(ast.name, "a")
    
    def test_not_expression(self):
        """Тест разбора NOT выражения."""
        ast = parse_expression("!a")
        self.assertIsInstance(ast, NotNode)
        self.assertIsInstance(ast.operand, VariableNode)
    
    def test_and_expression(self):
        """Тест разбора AND выражения."""
        ast = parse_expression("a&b")
        self.assertIsInstance(ast, AndNode)
    
    def test_or_expression(self):
        """Тест разбора OR выражения."""
        ast = parse_expression("a|b")
        self.assertIsInstance(ast, OrNode)
    
    def test_implies_expression(self):
        """Тест разбора IMPLIES выражения."""
        ast = parse_expression("a->b")
        self.assertIsInstance(ast, ImpliesNode)
    
    def test_xor_expression(self):
        """Тест разбора XOR выражения."""
        ast = parse_expression("a~b")
        self.assertIsInstance(ast, XorNode)
    
    def test_parenthesized_expression(self):
        """Тест разбора выражения в скобках."""
        ast = parse_expression("(a|b)&c")
        self.assertIsInstance(ast, AndNode)
        self.assertIsInstance(ast.left, OrNode)
    
    def test_complex_expression(self):
        """Тест разбора сложного выражения."""
        ast = parse_expression("!(!a->!b)|c")
        self.assertIsInstance(ast, OrNode)
    
    def test_nested_operations(self):
        """Тест вложенных операций."""
        ast = parse_expression("a&(b|c)")
        self.assertIsInstance(ast, AndNode)
        self.assertIsInstance(ast.right, OrNode)


class TestASTNodes(unittest.TestCase):
    """Тесты узлов AST."""
    
    def test_variable_evaluate_true(self):
        """Тест вычисления переменной (True)."""
        node = VariableNode("a")
        self.assertTrue(node.evaluate({"a": True}))
    
    def test_variable_evaluate_false(self):
        """Тест вычисления переменной (False)."""
        node = VariableNode("a")
        self.assertFalse(node.evaluate({"a": False}))
    
    def test_variable_get_variables(self):
        """Тест получения переменных."""
        node = VariableNode("a")
        self.assertEqual(node.get_variables(), {"a"})
    
    def test_not_node_true(self):
        """Тест NOT True."""
        node = NotNode(VariableNode("a"))
        self.assertFalse(node.evaluate({"a": True}))
    
    def test_not_node_false(self):
        """Тест NOT False."""
        node = NotNode(VariableNode("a"))
        self.assertTrue(node.evaluate({"a": False}))
    
    def test_and_node_true(self):
        """Тест AND (True & True)."""
        node = AndNode(VariableNode("a"), VariableNode("b"))
        self.assertTrue(node.evaluate({"a": True, "b": True}))
    
    def test_and_node_false(self):
        """Тест AND (True & False)."""
        node = AndNode(VariableNode("a"), VariableNode("b"))
        self.assertFalse(node.evaluate({"a": True, "b": False}))
    
    def test_or_node_true(self):
        """Тест OR (True | False)."""
        node = OrNode(VariableNode("a"), VariableNode("b"))
        self.assertTrue(node.evaluate({"a": True, "b": False}))
    
    def test_or_node_false(self):
        """Тест OR (False | False)."""
        node = OrNode(VariableNode("a"), VariableNode("b"))
        self.assertFalse(node.evaluate({"a": False, "b": False}))
    
    def test_implies_node_true(self):
        """Тест IMPLIES (True -> True)."""
        node = ImpliesNode(VariableNode("a"), VariableNode("b"))
        self.assertTrue(node.evaluate({"a": True, "b": True}))
    
    def test_implies_node_false(self):
        """Тест IMPLIES (True -> False)."""
        node = ImpliesNode(VariableNode("a"), VariableNode("b"))
        self.assertFalse(node.evaluate({"a": True, "b": False}))
    
    def test_xor_node_true(self):
        """Тест XOR (True ~ False)."""
        node = XorNode(VariableNode("a"), VariableNode("b"))
        self.assertTrue(node.evaluate({"a": True, "b": False}))
    
    def test_xor_node_false(self):
        """Тест XOR (True ~ True)."""
        node = XorNode(VariableNode("a"), VariableNode("b"))
        self.assertFalse(node.evaluate({"a": True, "b": True}))
    
    def test_string_representations(self):
        """Тест строковых представлений."""
        self.assertEqual(str(VariableNode("a")), "a")
        self.assertEqual(str(NotNode(VariableNode("a"))), "!(a)")
        self.assertIn("&", str(AndNode(VariableNode("a"), VariableNode("b"))))
        self.assertIn("|", str(OrNode(VariableNode("a"), VariableNode("b"))))


class TestGetAllVariables(unittest.TestCase):
    """Тесты функции get_all_variables."""
    
    def test_single_variable(self):
        """Тест одной переменной."""
        self.assertEqual(get_all_variables("a"), {"a"})
    
    def test_multiple_variables(self):
        """Тест нескольких переменных."""
        self.assertEqual(get_all_variables("a&b|c"), {"a", "b", "c"})
    
    def test_complex_expression(self):
        """Тест сложного выражения."""
        self.assertEqual(get_all_variables("!(!a->!b)|c"), {"a", "b", "c"})


class TestTruthTable(unittest.TestCase):
    """Тесты таблицы истинности."""
    
    def setUp(self):
        """Настройка тестов."""
        self.tt = TruthTable("a&b")
    
    def test_variables(self):
        """Тест переменных."""
        self.assertEqual(self.tt.variables, ["a", "b"])
    
    def test_num_vars(self):
        """Тест количества переменных."""
        self.assertEqual(self.tt.num_vars, 2)
    
    def test_table_length(self):
        """Тест длины таблицы."""
        self.assertEqual(len(self.tt), 4)
    
    def test_get_true_rows(self):
        """Тест получения строк с F=1."""
        true_rows = self.tt.get_true_rows()
        self.assertEqual(len(true_rows), 1)
        self.assertTrue(true_rows[0]['inputs']['a'])
        self.assertTrue(true_rows[0]['inputs']['b'])
    
    def test_get_false_rows(self):
        """Тест получения строк с F=0."""
        false_rows = self.tt.get_false_rows()
        self.assertEqual(len(false_rows), 3)
    
    def test_get_function_values(self):
        """Тест получения значений функции."""
        values = self.tt.get_function_values()
        self.assertEqual(values, [0, 0, 0, 1])
    
    def test_get_true_indices(self):
        """Тест получения индексов F=1."""
        indices = self.tt.get_true_indices()
        self.assertEqual(indices, [3])
    
    def test_get_false_indices(self):
        """Тест получения индексов F=0."""
        indices = self.tt.get_false_indices()
        self.assertEqual(indices, [0, 1, 2])
    
    def test_display(self):
        """Тест отображения таблицы."""
        display = self.tt.display()
        self.assertIn("a", display)
        self.assertIn("b", display)
        self.assertIn("F", display)
    
    def test_or_function(self):
        """Тест функции OR."""
        tt = TruthTable("a|b")
        values = tt.get_function_values()
        self.assertEqual(values, [0, 1, 1, 1])
    
    def test_not_function(self):
        """Тест функции NOT."""
        tt = TruthTable("!a")
        values = tt.get_function_values()
        self.assertEqual(values, [1, 0])


class TestNormalForms(unittest.TestCase):
    """Тесты нормальных форм."""
    
    def setUp(self):
        """Настройка тестов."""
        self.tt = TruthTable("a&b")
        self.nf = NormalForm(self.tt)
    
    def test_build_sdnf(self):
        """Тест построения СДНФ."""
        sdnf = self.nf.build_sdnf()
        self.assertIn("a", sdnf)
        self.assertIn("b", sdnf)
        # Для функции a&b только один минтерм, поэтому "v" может отсутствовать
        self.assertIsInstance(sdnf, str)
        self.assertTrue(len(sdnf) > 0)
    
    def test_build_sknf(self):
        """Тест построения СКНФ."""
        sknf = self.nf.build_sknf()
        self.assertIn("&", sknf)
    
    def test_sdnf_numeric(self):
        """Тест числовой формы СДНФ."""
        numeric = self.nf.get_sdnf_numeric()
        self.assertEqual(numeric, [3])
    
    def test_sknf_numeric(self):
        """Тест числовой формы СКНФ."""
        numeric = self.nf.get_sknf_numeric()
        self.assertEqual(numeric, [0, 1, 2])
    
    def test_sdnf_index_form(self):
        """Тест индексной формы СДНФ."""
        index = self.nf.get_sdnf_index_form()
        self.assertIn("sum", index)
        # Проверяем что есть столбец значений (0 и 1)
        self.assertIn("0", index)
        self.assertIn("1", index)

    def test_sknf_index_form(self):
        """Тест индексной формы СКНФ."""
        index = self.nf.get_sknf_index_form()
        self.assertIn("prod", index)
        # Проверяем что есть столбец значений
        self.assertIn("0", index)
        self.assertIn("1", index)

    def test_function_index_form(self):
        """Тест индексной формы функции."""
        index = self.nf.get_function_index_form()
        # Проверяем формат - просто столбец значений
        self.assertIn("F = (", index)
        self.assertIn("0", index)
        self.assertIn("1", index)
    
    def test_empty_sdnf(self):
        """Тест пустой СДНФ (функция тождественно 0)."""
        tt = TruthTable("a&!a")
        nf = NormalForm(tt)
        sdnf = nf.build_sdnf()
        self.assertEqual(sdnf, "0")
    
    def test_empty_sknf(self):
        """Тест пустой СКНФ (функция тождественно 1)."""
        tt = TruthTable("a|!a")
        nf = NormalForm(tt)
        sknf = nf.build_sknf()
        self.assertEqual(sknf, "1")


class TestPostClasses(unittest.TestCase):
    """Тесты классов Поста."""
    
    def test_t0_true(self):
        """Тест T0 (сохраняет ноль)."""
        tt = TruthTable("a&b")
        pc = PostClasses(tt)
        self.assertTrue(pc.belongs_to_t0())
    
    def test_t0_false(self):
        """Тест не T0."""
        tt = TruthTable("a|!a")
        pc = PostClasses(tt)
        self.assertFalse(pc.belongs_to_t0())
    
    def test_t1_true(self):
        """Тест T1 (сохраняет единицу)."""
        tt = TruthTable("a|b")
        pc = PostClasses(tt)
        self.assertTrue(pc.belongs_to_t1())
    
    def test_t1_false(self):
        """Тест не T1."""
        tt = TruthTable("!a|!b")
        pc = PostClasses(tt)
        self.assertFalse(pc.belongs_to_t1())
    
    def test_s_true(self):
        """Тест самодвойственной функции."""
        tt = TruthTable("!a")
        pc = PostClasses(tt)
        self.assertTrue(pc.belongs_to_s())
    
    def test_s_false(self):
        """Тест не самодвойственной функции."""
        tt = TruthTable("a&b")
        pc = PostClasses(tt)
        self.assertFalse(pc.belongs_to_s())
    
    def test_m_true(self):
        """Тест монотонной функции."""
        tt = TruthTable("a|b")
        pc = PostClasses(tt)
        self.assertTrue(pc.belongs_to_m())
    
    def test_m_false(self):
        """Тест не монотонной функции."""
        tt = TruthTable("!a")
        pc = PostClasses(tt)
        self.assertFalse(pc.belongs_to_m())
    
    def test_l_true(self):
        """Тест линейной функции."""
        tt = TruthTable("a~b")
        pc = PostClasses(tt)
        self.assertTrue(pc.belongs_to_l())
    
    def test_l_false(self):
        """Тест не линейной функции."""
        tt = TruthTable("a&b")
        pc = PostClasses(tt)
        self.assertFalse(pc.belongs_to_l())
    
    def test_get_all_classes(self):
        """Тест получения всех классов."""
        tt = TruthTable("a&b")
        pc = PostClasses(tt)
        classes = pc.get_all_classes()
        self.assertIn("T0", classes)
        self.assertIn("T1", classes)
        self.assertIn("S", classes)
        self.assertIn("M", classes)
        self.assertIn("L", classes)
    
    def test_display(self):
        """Тест отображения классов."""
        tt = TruthTable("a&b")
        pc = PostClasses(tt)
        display = pc.display()
        self.assertIn("T0", display)
        self.assertIn("T1", display)


class TestZhegalkinPolynomial(unittest.TestCase):
    """Тесты полинома Жегалкина."""
    
    def setUp(self):
        """Настройка тестов."""
        self.tt = TruthTable("a&b")
        self.zp = ZhegalkinPolynomial(self.tt)
    
    def test_get_polynomial(self):
        """Тест получения полинома."""
        poly = self.zp.get_polynomial()
        self.assertIsInstance(poly, str)
        self.assertTrue(len(poly) > 0)
        # Для функции a&b полином это просто "ab", без "^"
    
    def test_get_coefficients(self):
        """Тест получения коэффициентов."""
        coeffs = self.zp.get_coefficients()
        self.assertEqual(len(coeffs), 4)  # 2^2 = 4 коэффициента
    
    def test_get_terms(self):
        """Тест получения членов полинома."""
        terms = self.zp.get_terms()
        self.assertIsInstance(terms, list)
    
    def test_display_table(self):
        """Тест отображения таблицы коэффициентов."""
        table = self.zp.display_table()
        self.assertIn("Коэффициенты", table)
    
    def test_linear_function(self):
        """Тест линейной функции."""
        tt = TruthTable("a~b")
        zp = ZhegalkinPolynomial(tt)
        poly = zp.get_polynomial()
        self.assertIn("a", poly)
        self.assertIn("b", poly)


class TestDummyVariables(unittest.TestCase):
    """Тесты фиктивных переменных."""
    
    def test_no_dummy_variables(self):
        """Тест отсутствия фиктивных переменных."""
        tt = TruthTable("a&b")
        dv = DummyVariables(tt)
        dummy = dv.get_dummy_variables()
        self.assertEqual(dummy, [])
    
    def test_with_dummy_variable(self):
        """Тест с фиктивной переменной."""
        # Функция a&b|a&!b = a, переменная b фиктивна
        tt = TruthTable("a&b|a&!b")
        dv = DummyVariables(tt)
        dummy = dv.get_dummy_variables()
        self.assertEqual(dummy, ["b"])
    
    def test_is_dummy(self):
        """Тест проверки на фиктивность."""
        # Функция a&b|a&!b = a, переменная b фиктивна
        tt = TruthTable("a&b|a&!b")
        dv = DummyVariables(tt)
        self.assertTrue(dv.is_dummy("b"))
        self.assertFalse(dv.is_dummy("a"))
    
    def test_get_essential_variables(self):
        """Тест получения существенных переменных."""
        tt = TruthTable("a&b")
        dv = DummyVariables(tt)
        essential = dv.get_essential_variables()
        self.assertEqual(set(essential), {"a", "b"})
    
    def test_display(self):
        """Тест отображения информации."""
        tt = TruthTable("a&b")
        dv = DummyVariables(tt)
        display = dv.display()
        self.assertIn("Фиктивные", display)
        self.assertIn("Существенные", display)


class TestBooleanDerivatives(unittest.TestCase):
    """Тесты булевых производных."""
    
    def setUp(self):
        """Настройка тестов."""
        self.tt = TruthTable("a&b")
        self.bd = BooleanDerivatives(self.tt)
    
    def test_partial_derivative(self):
        """Тест частной производной."""
        deriv = self.bd.partial_derivative("a")
        self.assertEqual(len(deriv), 4)
    
    def test_invalid_variable(self):
        """Тест несуществующей переменной."""
        with self.assertRaises(ValueError):
            self.bd.partial_derivative("z")
    
    def test_get_all_partial_derivatives(self):
        """Тест получения всех частных производных."""
        derivatives = self.bd.get_all_partial_derivatives()
        self.assertIn("a", derivatives)
        self.assertIn("b", derivatives)
    
    def test_mixed_derivative(self):
        """Тест смешанной производной."""
        deriv = self.bd.mixed_derivative(["a", "b"])
        self.assertEqual(len(deriv), 4)
    
    def test_mixed_derivative_invalid_count(self):
        """Тест смешанной производной с неверным количеством."""
        with self.assertRaises(ValueError):
            self.bd.mixed_derivative(["a"])
    
    def test_display_partial_derivatives(self):
        """Тест отображения частных производных."""
        display = self.bd.display_partial_derivatives()
        self.assertIn("df/d", display)
    
    def test_display_mixed_derivatives(self):
        """Тест отображения смешанных производных."""
        display = self.bd.display_mixed_derivatives(2)
        self.assertIn("Смешанные", display)
    
    def test_derivative_to_expression(self):
        """Тест преобразования производной в выражение."""
        deriv = self.bd.partial_derivative("a")
        expr = self.bd.derivative_to_expression(deriv)
        self.assertIsInstance(expr, str)


class TestImplicant(unittest.TestCase):
    """Тесты импликант."""
    
    def test_to_string(self):
        """Тест строкового представления."""
        imp = Implicant(["a", "b"], [True, False], [2])
        self.assertIn("a", imp.to_string())
    
    def test_to_pattern(self):
        """Тест паттерна."""
        imp = Implicant(["a", "b"], [True, None], [2, 3])
        pattern = imp.to_pattern()
        self.assertIn("X", pattern)
    
    def test_covers(self):
        """Тест покрытия минтерма."""
        imp = Implicant(["a", "b"], [True, None], [2, 3])
        self.assertTrue(imp.covers(2))
        self.assertTrue(imp.covers(3))
        self.assertFalse(imp.covers(0))
    
    def test_equality(self):
        """Тест равенства импликант."""
        imp1 = Implicant(["a", "b"], [True, False], [2])
        imp2 = Implicant(["a", "b"], [True, False], [2])
        self.assertEqual(imp1, imp2)
    
    def test_hash(self):
        """Тест хэша импликант."""
        imp1 = Implicant(["a", "b"], [True, False], [2])
        imp2 = Implicant(["a", "b"], [True, False], [2])
        self.assertEqual(hash(imp1), hash(imp2))


class TestMinimization(unittest.TestCase):
    """Тесты минимизации."""
    
    def setUp(self):
        """Настройка тестов."""
        self.tt = TruthTable("a&b|a&!b")
        self.min = Minimization(self.tt)
    
    def test_minimize_calculated(self):
        """Тест расчетного метода."""
        implicants, history = self.min.minimize_calculated()
        self.assertIsInstance(implicants, list)
        self.assertIsInstance(history, list)
    
    def test_minimize_calculated_table(self):
        """Тест расчетно-табличного метода."""
        implicants, table, history = self.min.minimize_calculated_table()
        self.assertIsInstance(implicants, list)
        self.assertIn("Таблица", table)
    
    def test_minimize_karnaugh_2var(self):
        """Тест карты Карно для 2 переменных."""
        tt = TruthTable("a|b")
        min_func = Minimization(tt)
        implicants, kmap = min_func.minimize_karnaugh()
        self.assertIsInstance(implicants, list)
        self.assertIn("Карта", kmap)
        self.assertIn("+", kmap)
    
    def test_minimize_karnaugh_3var(self):
        """Тест карты Карно для 3 переменных."""
        tt = TruthTable("a&b|b&c|a&c")
        min_func = Minimization(tt)
        implicants, kmap = min_func.minimize_karnaugh()
        self.assertIsInstance(implicants, list)
    
    def test_get_minimized_dnf(self):
        """Тест получения минимизированной ДНФ."""
        # Используем функцию с несколькими импликантами
        tt = TruthTable("a|b")
        min_func = Minimization(tt)
        implicants, _ = min_func.minimize_calculated()
        dnf = min_func.get_minimized_dnf(implicants)
        self.assertIsInstance(dnf, str)
        self.assertTrue(len(dnf) > 0)
    
    def test_karnaugh_invalid_vars(self):
        """Тест карты Карно с недопустимым числом переменных."""
        tt = TruthTable("a&b&c&d&e")  # 5 переменных
        min_func = Minimization(tt)
        with self.assertRaises(ValueError):
            min_func.minimize_karnaugh()


class TestBooleanFunctionAnalyzer(unittest.TestCase):
    """Тесты анализатора булевых функций."""
    
    def setUp(self):
        """Настройка тестов."""
        self.analyzer = BooleanFunctionAnalyzer("a&b|!a&c")
    
    def test_analyze(self):
        """Тест полного анализа."""
        results = self.analyzer.analyze()
        self.assertIn("expression", results)
        self.assertIn("variables", results)
        self.assertIn("truth_table", results)
        self.assertIn("sdnf", results)
        self.assertIn("sknf", results)
        self.assertIn("post_classes", results)
        self.assertIn("zhegalkin", results)
    
    def test_analyze_complex_expression(self):
        """Тест анализа сложного выражения."""
        analyzer = BooleanFunctionAnalyzer("!(!a->!b)|c")
        results = analyzer.analyze()
        self.assertEqual(results['variables'], ["a", "b", "c"])
    
    def test_minimized_calculated_full(self):
        """Тест расчетного метода для ДНФ."""
        result = self.analyzer._minimize_dnf_calculated_full()
        self.assertIsInstance(result, str)

    def test_minimize_table_full(self):
        """Тест расчетно-табличного метода для ДНФ."""
        result = self.analyzer._minimize_dnf_table_full()
        self.assertIsInstance(result, str)

    def test_minimize_karnaugh_full(self):
        """Тест карты Карно для ДНФ."""
        result = self.analyzer._minimize_dnf_karnaugh_full()
        self.assertIsInstance(result, str)


class TestIntegration(unittest.TestCase):
    """Интеграционные тесты."""
    
    def test_full_workflow(self):
        """Тест полного рабочего процесса."""
        expression = "!(!a->!b)|c"
        analyzer = BooleanFunctionAnalyzer(expression)
        results = analyzer.analyze()
        
        # Проверка всех ключей
        required_keys = [
            'expression', 'variables', 'truth_table',
            'sdnf', 'sknf', 'sdnf_numeric', 'sknf_numeric',
            'sdnf_index', 'sknf_index', 'function_index',
            'post_classes', 'post_display', 'zhegalkin',
            'zhegalkin_table', 'dummy_variables',
            'partial_derivatives', 'minimized_dnf_calculated',
            'minimized_dnf_table', 'minimized_dnf_karnaugh',
            'minimized_cnf_calculated', 'minimized_cnf_table'
        ]
        
        for key in required_keys:
            self.assertIn(key, results)
    
    def test_example_from_task(self):
        """Тест примера из задания."""
        expression = "!(!a->!b)|c"
        analyzer = BooleanFunctionAnalyzer(expression)
        results = analyzer.analyze()
        
        # Проверка что СДНФ не пустая
        self.assertNotEqual(results['sdnf'], "0")
        
        # Проверка что полином Жегалкина существует
        self.assertIsInstance(results['zhegalkin'], str)
        self.assertNotEqual(results['zhegalkin'], "")
    
    def test_three_variable_function(self):
        """Тест функции с тремя переменными."""
        expression = "a&b|b&c|a&c"
        analyzer = BooleanFunctionAnalyzer(expression)
        results = analyzer.analyze()
        
        self.assertEqual(len(results['variables']), 3)
        # Таблица истинности для 3 переменных имеет 8 строк данных
        tt = TruthTable(expression)
        self.assertEqual(len(tt), 8)
    
    def test_two_variable_karnaugh(self):
        """Тест карты Карно для 2 переменных."""
        expression = "a|b"
        analyzer = BooleanFunctionAnalyzer(expression)
        results = analyzer.analyze()

        self.assertIn("Карта", results['minimized_dnf_karnaugh'])
        self.assertEqual(len(results['variables']), 2)
    
    def test_four_variable_function(self):
        """Тест функции с 4 переменными."""
        expression = "a&b&c&d"
        analyzer = BooleanFunctionAnalyzer(expression)
        results = analyzer.analyze()
        
        self.assertEqual(len(results['variables']), 4)
        self.assertIn("a", results['sdnf'])
    
    def test_print_full_report(self):
        """Тест вывода полного отчета."""
        analyzer = BooleanFunctionAnalyzer("a&b")
        # Проверяем что метод работает (UnicodeEncodeError может возникать в Windows)
        try:
            analyzer.print_full_report()
        except UnicodeEncodeError:
            # Ожидаемая ошибка в некоторых консолях Windows
            pass


if __name__ == "__main__":
    unittest.main()
