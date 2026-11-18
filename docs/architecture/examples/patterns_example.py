"""Изолированные примеры Repository, UoW и Strategy; не веб-приложение."""
from dataclasses import dataclass
from decimal import Decimal
from typing import Protocol
from copy import deepcopy

@dataclass(frozen=True)
class Sale:
    external_id: str
    revenue: Decimal
    cost: Decimal

class SaleRepository(Protocol):
    def add(self, sale: Sale) -> None: ...
    def all(self) -> list[Sale]: ...

class MemorySaleRepository:
    def __init__(self, records):
        self.records = records
    def add(self, sale):
        if sale.external_id in self.records:
            raise ValueError('Повторный идентификатор сделки')
        self.records[sale.external_id] = sale
    def all(self):
        return list(self.records.values())

class MemoryUnitOfWork:
    """Копия состояния публикуется только при явном commit()."""
    def __init__(self, store):
        self.store = store
    def __enter__(self):
        self.pending = deepcopy(self.store)
        self.sales = MemorySaleRepository(self.pending)
        return self
    def commit(self):
        self.store.clear()
        self.store.update(self.pending)
    def rollback(self):
        self.pending.clear()
    def __exit__(self, exc_type, exc, tb):
        self.rollback()
        return False

@dataclass(frozen=True)
class KpiInput:
    revenue: Decimal
    cost: Decimal
    won: int
    closed: int

class KpiStrategy(Protocol):
    def calculate(self, data: KpiInput) -> Decimal | None: ...

class ProfitabilityStrategy:
    def calculate(self, data):
        if data.revenue == 0:
            return None
        return (data.revenue - data.cost) / data.revenue * 100

class AverageCheckStrategy:
    def calculate(self, data):
        return None if data.won == 0 else data.revenue / data.won

class ConversionStrategy:
    def calculate(self, data):
        return None if data.closed == 0 else Decimal(data.won) / data.closed * 100

def import_sales(records, uow):
    """Service Layer: сценарий работает через UoW и Repository."""
    with uow as tx:
        for sale in records:
            if sale.revenue < 0 or sale.cost < 0:
                raise ValueError('Отрицательные суммы не поддержаны примером')
            tx.sales.add(sale)
        tx.commit()
