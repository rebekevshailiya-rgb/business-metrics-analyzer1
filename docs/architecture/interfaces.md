# Интерфейсы компонентов

Контракты проектируемые. `ActorContext` содержит актуальные user_id, role, department_id и доступную область; каждый сценарий проверяет её на сервере. `Period` содержит начало/конец диапазона дат, `KpiResult` допускает null при неопределённом отношении.

| Компонент | Порт / интерфейс | Ключевые методы | Зависимости |
|---|---|---|---|
| AuthService | IAuthService | login(credentials) → TokenPair; refresh(token) → TokenPair; authenticate(token) → ActorContext | IUserRepository, ITokenProvider, IUoW |
| UserService | IUserService | create(actor, user_dto) → UserDto; block(actor, user_id) → None | IUserRepository, IUoW, IAudit |
| SalesImportService | ISalesImportService | submit(actor, file) → JobDto; validate(records, scope) → ValidationResult; run(job_id) → ImportResult | IJobQueue, IObjectStorage, ISaleRepository, IUoW, валидаторы |
| KpiService | IKpiService | calculate_period(actor, period, filters) → KpiResult; get_dashboard(actor, period) → DashboardDto | ISaleRepository, IKpiCache, KpiStrategy |
| ReportService | IReportService | generate(actor, format, period) → JobDto; download(actor, report_id) → ReportFile | KpiService, ReportGeneratorFactory, IObjectStorage, IUoW |
| SqlSaleRepository | ISaleRepository | stage(import_id, batch); publish(import_id); aggregate(scope, period) → KpiInput | PostgreSQL через SQLAlchemy; сам commit не выполняет |
| SqlUserRepository | IUserRepository | get(user_id) → User; save(user) → None | PostgreSQL через SQLAlchemy |
| SqlUnitOfWork | IUoW | __enter__(); commit(); rollback(); __exit__() | Одна сессия/транзакция PostgreSQL на операцию |
| JwtProvider | ITokenProvider | issue(claims); verify(token) → Claims | Ключи и настройки алгоритма |
| RedisCache | IKpiCache | get(key); set(key, value, ttl) | Redis cache; scope + версии в ключе |
| JobQueue / dispatcher | IJobQueue | enqueue(outbox_event); retry(job_id) | Redis broker; источником состояния задания служит БД |
| Excel/PdfReportGenerator | IReportGenerator | render(dto) → bytes | openpyxl / ReportLab; не получает ORM-модели |
| ObjectStorage | IObjectStorage | put(key, bytes); get(key); delete(key) | S3 API |
| SmtpNotifier | INotifier | send(recipient, subject, body) | SMTP с TLS; ошибки доставки не откатывают готовый отчёт |
| SourceAdapter | ISalesSource | fetch(cursor) → Batch | Внешний HTTPS API; интеграционный контракт уточняется |

Контроллеры преобразуют HTTP в DTO и вызывают соответствующие сервисы. Domain не зависит от реализаций этих интерфейсов. Infrastructure реализует порты Application; соединение выполняет composition root. Транзакция публикации импорта не включает сетевую отправку письма или запись в Redis.
