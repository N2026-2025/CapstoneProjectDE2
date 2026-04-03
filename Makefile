# =============================================================================
# Makefile — DE Zoomcamp Capstone Project
# Customer Support Ticket Analytics
# Stack: Docker · Kestra · DuckDB · dbt · Superset · Jupyter · Kafka (opt)
#
# Run from project root:  make <target>
# List all commands:       make help
# =============================================================================

SHELL        := /bin/bash
COMPOSE_FILE := docker-compose.yml
FLOW_NS      := capstone.support

FLOW  ?= 01_ingest_csv
MODEL ?=
CSV   ?= ./data/customer_support_tickets.csv
DB    ?= ./duckdb/support.duckdb

.PHONY: help check setup \
        up down restart ps logs \
        kestra superset jupyter \
        kestra-logs kestra-flows kestra-trigger \
        ingest dbt-debug dbt-run dbt-test dbt-docs dbt-clean \
        kafka-up kafka-down \
        pipeline pipeline-batch \
        status reset-db reset-all

# =============================================================================
# HELP
# =============================================================================
help:
	@echo ""
	@echo "╔══════════════════════════════════════════════════════════╗"
	@echo "║    Customer Support Analytics — make targets             ║"
	@echo "╚══════════════════════════════════════════════════════════╝"
	@echo ""
	@echo "── SETUP (primera vez) ────────────────────────────────────"
	@echo "  make setup           Crea carpetas + .env"
	@echo "  make check           Verifica docker, python3, CSV"
	@echo ""
	@echo "── STACK ──────────────────────────────────────────────────"
	@echo "  make up              Levanta kestra + superset + jupyter"
	@echo "  make down            Baja todos los contenedores"
	@echo "  make restart         Down + Up"
	@echo "  make ps              Estado de contenedores"
	@echo "  make logs            Tail de todos los logs"
	@echo ""
	@echo "── MÓDULOS INDIVIDUALES ───────────────────────────────────"
	@echo "  make kestra          Solo Kestra"
	@echo "  make superset        Solo Superset"
	@echo "  make jupyter         Solo Jupyter"
	@echo ""
	@echo "── KESTRA ─────────────────────────────────────────────────"
	@echo "  make kestra-logs     Tail logs de Kestra"
	@echo "  make kestra-flows    Lista flows en namespace $(FLOW_NS)"
	@echo "  make kestra-trigger  Dispara flow  [FLOW=01_ingest_csv]"
	@echo ""
	@echo "── DATOS + DBT ────────────────────────────────────────────"
	@echo "  make ingest          Carga CSV → DuckDB raw"
	@echo "  make dbt-debug       Testea conexión DuckDB"
	@echo "  make dbt-run         Corre todos los modelos  [MODEL=mart_fairness]"
	@echo "  make dbt-test        Corre tests de calidad"
	@echo "  make dbt-docs        Genera docs (puerto 8081)"
	@echo "  make dbt-clean       Borra target/"
	@echo ""
	@echo "── KAFKA (opcional) ───────────────────────────────────────"
	@echo "  make kafka-up        Levanta Kafka nativo (bitnami)"
	@echo "  make kafka-down      Baja Kafka"
	@echo ""
	@echo "── PIPELINES ──────────────────────────────────────────────"
	@echo "  make pipeline        ingest + dbt-run + dbt-test (completo)"
	@echo "  make pipeline-batch  Solo ingest → dbt-run"
	@echo ""
	@echo "── UTILS ──────────────────────────────────────────────────"
	@echo "  make status          Contenedores + tablas en DuckDB"
	@echo "  make reset-db        ⚠️  Borra support.duckdb"
	@echo "  make reset-all       ⚠️  Borra DuckDB + storage"
	@echo ""
	@echo "── URLs ───────────────────────────────────────────────────"
	@echo "  Kestra:   http://localhost:18080  admin@kestra.io / Admin1234"
	@echo "  Superset: http://localhost:8088   admin / support1234"
	@echo "  Jupyter:  http://localhost:8888   token: support"
	@echo ""

# =============================================================================
# PREREQUISITES
# =============================================================================
check:
	@echo "── Verificando requisitos ──"
	@command -v docker      >/dev/null 2>&1 && echo "✅ docker:    $$(docker --version)"    || echo "❌ docker no encontrado"
	@docker compose version >/dev/null 2>&1 && echo "✅ compose:   $$(docker compose version)" || echo "❌ docker compose no encontrado"
	@command -v python3     >/dev/null 2>&1 && echo "✅ python3:   $$(python3 --version)"   || echo "❌ python3 no encontrado"
	@command -v git         >/dev/null 2>&1 && echo "✅ git:       $$(git --version)"       || echo "❌ git no encontrado"
	@test -f .env           && echo "✅ .env encontrado"           || echo "⚠️  .env faltante — corré: make setup"
	@test -f $(CSV)         && echo "✅ CSV encontrado: $(CSV)"    || echo "⚠️  CSV no encontrado en $(CSV)"

# =============================================================================
# SETUP
# =============================================================================
setup:
	@echo "── Creando estructura del proyecto ──"
	mkdir -p flows scripts data storage duckdb notebooks
	mkdir -p dbt/capstone_support/models/{staging,core/dimensions,core/facts,marts}
	mkdir -p dbt/capstone_support/{seeds,tests,macros}
	@test -f .env || ( \
		echo "KESTRA_USER=admin@kestra.io"                              > .env; \
		echo "KESTRA_PASS=Admin1234"                                   >> .env; \
		echo "SUPERSET_ADMIN=admin"                                    >> .env; \
		echo "SUPERSET_PASS=support1234"                               >> .env; \
		echo "SUPERSET_SECRET=support_secret_change_in_prod_32c"       >> .env; \
		echo "JUPYTER_TOKEN=support"                                   >> .env; \
		echo "✅ .env creado con valores por defecto"; )
	@echo "✅ Listo. Copiá tu CSV a ./data/ y corré: make up"

# =============================================================================
# STACK
# =============================================================================
up:
	@echo "── Levantando stack ──"
	docker compose -f $(COMPOSE_FILE) up -d kestra superset jupyter
	@echo "── Esperando Kestra (puede tardar ~2 min la primera vez)... ──"
	@bash -c 'for i in $$(seq 1 30); do curl -sf http://localhost:18080/health >/dev/null 2>&1 && break; printf "."; sleep 4; done; echo ""'
	@echo ""
	@echo "✅ Stack listo:"
	@echo "   🌐 Kestra:   http://localhost:18080  →  admin@kestra.io / Admin1234"
	@echo "   📓 Jupyter:  http://localhost:8888   →  token: support"
	@echo "   📊 Superset: http://localhost:8088   →  admin / support1234"
	@echo ""
	@echo "   Siguiente: make pipeline"

down:
	docker compose -f $(COMPOSE_FILE) down

restart: down up

ps:
	docker compose -f $(COMPOSE_FILE) ps

logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=150

# =============================================================================
# MÓDULOS INDIVIDUALES
# =============================================================================
kestra:
	docker compose -f $(COMPOSE_FILE) up -d kestra
	@echo "✅ Kestra: http://localhost:18080"

superset:
	docker compose -f $(COMPOSE_FILE) up -d superset
	@echo "✅ Superset: http://localhost:8088"
	@echo "   Conectar DuckDB: duckdb:////shared/duckdb/support.duckdb"

jupyter:
	docker compose -f $(COMPOSE_FILE) up -d jupyter
	@echo "✅ Jupyter: http://localhost:8888  (token: support)"

# =============================================================================
# KESTRA
# =============================================================================
kestra-logs:
	docker compose -f $(COMPOSE_FILE) logs -f --tail=200 kestra

kestra-flows:
	@docker compose -f $(COMPOSE_FILE) exec kestra \
		curl -s -u admin@kestra.io:Admin1234 \
		http://localhost:18080/api/v1/flows/$(FLOW_NS) \
		| python3 -c "import sys,json; [print(' -', f['id']) for f in json.load(sys.stdin)]" \
		2>/dev/null || echo "⚠️  Kestra no está corriendo. Corré: make kestra"

kestra-trigger:
	@echo "── Disparando flow: $(FLOW) ──"
	docker compose -f $(COMPOSE_FILE) exec kestra \
		curl -s -X POST -u admin@kestra.io:Admin1234 \
		http://localhost:18080/api/v1/executions/$(FLOW_NS)/$(FLOW) \
		| python3 -c "import sys,json; d=json.load(sys.stdin); print('Execution ID:', d.get('id','?'), '| State:', d.get('state',{}).get('current','?'))"

# =============================================================================
# INGEST — CSV → DuckDB raw
# =============================================================================
ingest:
	@test -f $(CSV) || ( \
		echo "❌ CSV no encontrado: $(CSV)"; \
		echo "   Descargalo con:"; \
		echo "   kaggle datasets download -d suraj520/customer-support-ticket-dataset -p ./data --unzip"; \
		exit 1)
	@echo "── Cargando $(CSV) → DuckDB raw ──"
	@docker compose -f $(COMPOSE_FILE) exec -T kestra python3 -c "\
import duckdb; \
con = duckdb.connect('/shared/duckdb/support.duckdb'); \
con.execute('CREATE SCHEMA IF NOT EXISTS raw'); \
con.execute(\"\"\"CREATE OR REPLACE TABLE raw.customer_support_tickets AS \
SELECT *, current_timestamp AS _ingested_at \
FROM read_csv_auto('/shared/data/customer_support_tickets.csv', header=true)\"\"\"); \
n = con.execute('SELECT COUNT(*) FROM raw.customer_support_tickets').fetchone()[0]; \
print(f'✅ {n:,} filas cargadas en raw.customer_support_tickets'); \
con.close()"

# =============================================================================
# DBT
# =============================================================================
dbt-debug:
	docker compose -f $(COMPOSE_FILE) run --rm dbt \
		dbt debug --profiles-dir /usr/app/dbt

dbt-run:
	@if [ -n "$(MODEL)" ]; then \
		docker compose -f $(COMPOSE_FILE) run --rm dbt \
			dbt run --profiles-dir /usr/app/dbt --select $(MODEL); \
	else \
		docker compose -f $(COMPOSE_FILE) run --rm dbt \
			dbt run --profiles-dir /usr/app/dbt; \
	fi

dbt-test:
	docker compose -f $(COMPOSE_FILE) run --rm dbt \
		dbt test --profiles-dir /usr/app/dbt

dbt-docs:
	docker compose -f $(COMPOSE_FILE) run --rm dbt \
		dbt docs generate --profiles-dir /usr/app/dbt
	docker compose -f $(COMPOSE_FILE) run --rm -p 8081:8081 dbt \
		dbt docs serve --port 8081 --profiles-dir /usr/app/dbt
	@echo "✅ dbt docs: http://localhost:8081"

dbt-clean:
	docker compose -f $(COMPOSE_FILE) run --rm dbt \
		dbt clean --profiles-dir /usr/app/dbt

# =============================================================================
# KAFKA (opcional — descomentá el servicio en docker-compose.yml primero)
# =============================================================================
kafka-up:
	@echo "── Levantando Kafka nativo (bitnami) ──"
	@grep -q "image: bitnami/kafka" $(COMPOSE_FILE) || \
		(echo "❌ Descomentá el servicio kafka en $(COMPOSE_FILE) primero"; exit 1)
	docker compose -f $(COMPOSE_FILE) up -d kafka
	@echo "── Esperando Kafka (15s)... ──"
	@sleep 15
	docker compose -f $(COMPOSE_FILE) exec kafka \
		kafka-topics.sh --bootstrap-server localhost:9092 \
		--create --if-not-exists --topic support_tickets_raw \
		--partitions 1 --replication-factor 1
	@echo "✅ Kafka listo. Topic: support_tickets_raw"

kafka-down:
	docker compose -f $(COMPOSE_FILE) stop kafka
	docker compose -f $(COMPOSE_FILE) rm -f kafka

# =============================================================================
# PIPELINES
# =============================================================================
pipeline: ingest dbt-run dbt-test
	@echo ""
	@echo "✅ Pipeline completo."
	@echo "   Abrí Superset: http://localhost:8088"
	@echo "   Conectar DuckDB: duckdb:////shared/duckdb/support.duckdb"

pipeline-batch: ingest dbt-run
	@echo "✅ Batch pipeline listo."

# =============================================================================
# STATUS
# =============================================================================
status:
	@echo "── Contenedores ──────────────────────────────────────────"
	@docker compose -f $(COMPOSE_FILE) ps
	@echo ""
	@echo "── Tablas en DuckDB ──────────────────────────────────────"
	@docker compose -f $(COMPOSE_FILE) exec -T kestra python3 -c "\
import duckdb; \
con = duckdb.connect('/shared/duckdb/support.duckdb'); \
df = con.execute(\"SELECT table_schema, table_name FROM information_schema.tables ORDER BY 1,2\").df(); \
print(df.to_string(index=False)) if len(df) else print('  (sin tablas aún — corré: make ingest)'); \
con.close()" 2>/dev/null || echo "  ⚠️  Kestra no disponible"

# =============================================================================
# RESET
# =============================================================================
reset-db:
	@echo "⚠️  Borrando $(DB)..."
	rm -f $(DB)
	@echo "Listo. Corré: make pipeline"

reset-all:
	@echo "⚠️  Borrando DuckDB + storage..."
	rm -f $(DB)
	rm -rf ./storage/*
	@echo "Listo. Corré: make up && make pipeline"