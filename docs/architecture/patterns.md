# Паттерны проектирования

Выбраны семь паттернов для системы в целом. Шесть в каждом отдельном модуле не нужны: критерий оценивания требует не менее шести обоснованных паттернов и примеры. Применение по функциональным областям описано ниже.

| Паттерн | Где применяется | Обоснование | Альтернатива и компромисс |
|---|---|---|---|
| Repository | Продажи, пользователи, импорт, отчёты | Контракт не зависит от SQLAlchemy, обязательная фильтрация по scope | ORM прямо в сервисе проще, но связывает бизнес-сценарий со схемой БД |
| Unit of Work | Импорт и управление пользователями | Одна транзакция для связанных изменений, commit/rollback | Ручные commit в каждом репозитории создают частично сохранённую операцию |
| Service Layer | Auth, импорт, KPI, отчёты, пользователи | Сценарий един для API и worker; контроллер не содержит бизнес-формул | Fat-controller затрудняет повторное использование и тесты |
| DTO | API, задания, отчёты | Явный контракт между слоями; ORM-сущности не уходят в JSON | dict проще, но контракт хуже виден и проверяется |
| Strategy | Выручка, средний чек, конверсия, рентабельность | Единый KpiInput и взаимозаменяемый calculate; правила тестируются отдельно | Один if/elif допустим для прототипа, хуже при настраиваемых формулах |
| Factory | Генератор XLSX/PDF | Выбор реализации по формату; ReportService получает общий интерфейс | Условие внутри сервиса достаточно для двух форматов, но затрудняет дальнейшее расширение |
| Adapter | Источник 1С/API, SMTP, S3, JWT | Технический протокол не проникает в Domain, можно подменять реализации | Прямые сетевые вызовы из сценария проще сначала, но увеличивают связанность |

Аутентификация использует Service Layer + DTO + Repository + Adapter. Импорт — Service Layer + Repository + UoW + DTO + Adapter. KPI — Service Layer + Repository + Strategy + DTO. Отчёты — Service Layer + Factory + Adapter + DTO. Пользователи/права — Service Layer + Repository + UoW + DTO. Настройки/справочники — Repository + UoW, стратегии получают уже проверенные правила. Аудит — инфраструктурный адаптер, бизнес-операция пишет событие внутри своей транзакции. Паттерны не подменяют проверки безопасности.

## Примеры трёх ключевых паттернов

Исполняемый [patterns_example.py](examples/patterns_example.py) содержит Repository, Unit of Work и Strategy; дополнительно видны DTO и Service Layer. MemoryUnitOfWork — демонстрация транзакционной границы на копии словаря, **не** реализация PostgreSQL, параллельных транзакций или длительного импорта.

### Repository + Unit of Work

```python
class SaleRepository(Protocol):
    def add(self, sale: Sale) -> None: ...
    def all(self) -> list[Sale]: ...

def import_sales(records, uow):
    with uow as tx:
        for sale in records:
            tx.sales.add(sale)
        tx.commit()
```

Репозиторий не делает commit. В PostgreSQL SqlUnitOfWork создаёт сессию, при ошибке операции или commit вызывает rollback, а в finally закрывает сессию. Явный commit выполняется после проверок. Production-импорт дополнительно применяет staging, как описано в README; пример специально изолирован от миллионного набора.

### Strategy с единым входом

```python
class KpiStrategy(Protocol):
    def calculate(self, data: KpiInput) -> Decimal | None: ...

class ProfitabilityStrategy:
    def calculate(self, data):
        if data.revenue == 0:
            return None
        return (data.revenue - data.cost) / data.revenue * 100
```

В отличие от примера с разными сигнатурами, все стратегии принимают KpiInput; случайно передать число заказов вместо затрат нельзя через изменение интерфейса. DTO агрегирует revenue/cost/won/closed; контроллер превращает None в JSON null и понятную подпись.

## Проверка примеров

Из корня проекта:

```text
python -m unittest discover -s docs/architecture/examples -p "test_*.py" -v
```

Тесты проверяют commit, rollback всей пачки после дубля, выход без commit, рентабельность 20%, нулевые знаменатели и общий вход стратегий. Это проверка учебных примеров, а не готовности API или нагрузочного SLA.
