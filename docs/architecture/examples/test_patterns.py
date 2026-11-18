import unittest
from decimal import Decimal as D
from patterns_example import (Sale, MemoryUnitOfWork, import_sales, KpiInput,
                              ProfitabilityStrategy, AverageCheckStrategy, ConversionStrategy)

class PatternTests(unittest.TestCase):
    def test_success_is_committed(self):
        store = {}
        import_sales([Sale('1', D('150000'), D('120000'))], MemoryUnitOfWork(store))
        self.assertEqual(len(store), 1)
    def test_duplicate_rolls_back_whole_batch(self):
        store = {'old': Sale('old', D('10'), D('2'))}
        before = store.copy()
        with self.assertRaises(ValueError):
            import_sales([Sale('new', D('20'), D('5')), Sale('old', D('1'), D('1'))], MemoryUnitOfWork(store))
        self.assertEqual(store, before)
    def test_missing_commit_does_not_publish(self):
        store = {}
        with MemoryUnitOfWork(store) as tx:
            tx.sales.add(Sale('1', D('10'), D('2')))
        self.assertEqual(store, {})
    def test_profitability(self):
        self.assertEqual(ProfitabilityStrategy().calculate(KpiInput(D('150000'), D('120000'), 3, 5)), D('20'))
    def test_zero_denominators(self):
        data=KpiInput(D('0'), D('0'), 0, 0)
        for strategy in [ProfitabilityStrategy(), AverageCheckStrategy(), ConversionStrategy()]:
            self.assertIsNone(strategy.calculate(data))
    def test_shared_strategy_input(self):
        data=KpiInput(D('150000'), D('120000'), 3, 5)
        self.assertEqual(AverageCheckStrategy().calculate(data), D('50000'))
        self.assertEqual(ConversionStrategy().calculate(data), D('60'))

if __name__ == '__main__':
    unittest.main()
