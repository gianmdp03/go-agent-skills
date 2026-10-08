# Skills profesionales para Go y Spring Boot → Go

Dos **Agent Skills**, listas para instalar en Google Antigravity o adaptar a cualquier agente compatible con [Agent Skills](https://agentskills.io/specification).

- **`go-backend`**: desarrollo y revisión de backends *idiomáticos* en **Go 1.27.1**. Arquitectura mínima necesaria, sin Java disfrazado de Go; HTTP, PostgreSQL, seguridad, concurrencia, pruebas y producción.
- **`spring-to-go`**: migración **Spring Boot 4.1.1 → Go 1.27.1**, orientada a reemplazo directo (drop-in) con contratos HTTP idénticos, lógica de negocio preservada, compatibilidad bidireccional con **PostgreSQL sin modificar el esquema ni migrar los datos**. **Cuatro fases fijas:** auditoría, diseño, migración incremental y verificación.

> La migradora exige cargar explícitamente `go-backend`. El estándar Agent Skills **no garantiza dependencias automáticas entre Skills**; por eso deben instalarse juntas, como carpetas hermanas. La ausencia de la Skill base bloquea la migración en lugar de improvisar reglas.

## Instalación en Antigravity (Windows, PowerShell)

Descomprimí el ZIP y abrí PowerShell dentro de la carpeta `go-agent-skills`.

**Global (para todos tus proyectos):**

```powershell
.\install.ps1 -Scope Global
```

**Solo en un proyecto:**

```powershell
.\install.ps1 -Scope Workspace -WorkspacePath 'C:\ruta\de\tu\backend'
```

Si PowerShell tiene restringida la ejecución de scripts, copiá manualmente **las dos carpetas** `go-backend` y `spring-to-go` a:

- Global: `%USERPROFILE%\.gemini\config\skills\`
- Proyecto: `<proyecto>\.agents\skills\`

El instalador **no sobreescribe** copias ya existentes. Reiniciá o recargá Antigravity para que descubra las Skills. La documentación de Antigravity admite ambas ubicaciones: https://antigravity.google/docs/skills

### Linux / macOS / WSL

```bash
./install.sh global
# o
./install.sh workspace /ruta/al/proyecto
```

## Cómo usarlas

Para un backend nuevo:

> Usá la Skill **go-backend** para implementar este servicio en Go 1.27.1 con una arquitectura mínima y adecuada al dominio, tests y verificaciones. No imites Java ni agregues capas sin justificación.

Para convertir un Spring Boot:

> Usá **spring-to-go** y su dependencia **go-backend** para migrar este proyecto Spring Boot 4.1.1 a Go 1.27.1 en sus **cuatro fases obligatorias**. Conservá exactamente contratos HTTP, autenticación/autorización, trabajos e integraciones, y comportamiento sobre **el esquema y los datos PostgreSQL existentes**. No cambies el frontend ni la BDD. Usá clones aislados, pruebas diferenciales y rollback verificable. No desplegues a producción sin mi autorización.

Las Skills pueden activarse automáticamente por descripción en agentes compatibles, pero invocarlas explícitamente es mejor para una migración compleja. En Antigravity pueden aparecer como `/go-backend` y `/spring-to-go` según el modo de interacción.

## Qué incluye cada Skill

```text
go-agent-skills/
├── README.md
├── install.ps1
├── install.sh
├── go-backend/
│   ├── SKILL.md
│   ├── references/       (6 guías)
│   └── scripts/
│       └── check_go.py   (gofmt, build, vet, tests, -race, govulncheck opcional)
└── spring-to-go/
    ├── SKILL.md
    ├── references/       (7 guías)
    ├── assets/           (estado de migración, matriz y reporte)
    └── scripts/
        ├── compare_snapshots.py
        └── compare_schema.py
```

## Verificaciones ejecutables

**Calidad Go**, desde la raíz del módulo Go:

```bash
python /ruta/a/go-backend/scripts/check_go.py .
```

El script exige la versión exacta `go1.27.1`. Para omitir explícitamente `-race` donde no sea compatible, usar `--skip-race` (se informa como **NOT RUN**, no como PASS). Para exigir el escáner de vulnerabilidades, usar `--require-vulncheck`. Si no está instalado, no se declara la seguridad verificada. Estos comandos pueden requerir dependencias, servicios de prueba y herramientas disponibles localmente.

**Comparación de capturas Spring vs Go** (preparadas por el agente en ambientes aislados):

```bash
python /ruta/a/spring-to-go/scripts/compare_snapshots.py spring.json go.json
```

También incluye `compare_schema.py spring-schema.sql go-schema.sql` para comparar capturas **sanitizadas** de `pg_dump --schema-only` de clones aislados, generadas con los mismos parámetros/versiones. La igualdad textual no prueba por sí sola compatibilidad.

El comparador informa diferencias estrictas de tipos, campos, HTTP, DB y efectos secundarios presentes **en las capturas**. **No contacta servidores, no lee PostgreSQL y no prueba por sí solo la compatibilidad total**. El agente debe crear o adaptar el harness real, pruebas de contratos, tests de lectura/escritura cruzada y validación del esquema. No usar datos personales ni secretos reales en capturas.

## Seguridad y límites

- Por defecto no se ejecuta nada en producción. Cualquier migración de esquema, operación destructiva, despliegue o cambio de tráfico real exige aprobación explícita.
- El esquema PostgreSQL permanece intacto, pero esto **no basta**: se comprueban transacciones, generación de IDs, tipos, nulos, precisión, sesiones, seguridad, tareas en background y compatibilidad después de escrituras desde Go.
- Una migración completa solo se declara **READY** si se ejecutaron y pasaron los gates obligatorios. Si faltan dependencias/ambiente/casos, queda **NOT READY / BLOCKED**. Ninguna Skill puede garantizar equivalencia absoluta sin pruebas sobre el sistema concreto.
- Las referencias están escritas en inglés técnico para facilitar la reutilización entre agentes; los prompts y reportes pueden pedirse en español.

## Referencias normativas consultadas (octubre de 2026)

- Agent Skills: https://agentskills.io/specification
- Antigravity Skills: https://antigravity.google/docs/skills
- Go 1.27.1: https://go.dev/doc/devel/release
- Spring Boot 4.1.1: https://spring.io/blog/2026/08/20/spring-boot-4-1-1-available-now/
- Estilo Google Go: https://google.github.io/styleguide/go/
- Comentarios de revisión Go: https://go.dev/wiki/CodeReviewComments
- Documentación de módulos: https://go.dev/doc/modules/gomod-ref

## Mantenimiento recomendado

Versionar las Skills juntas en Git, mantener versiones de librerías/herramientas verificadas, ejecutar pruebas periódicas con un backend de ejemplo y con migraciones reales (en staging), y actualizar reglas tras cada incidencia reproducible. Si cambia el target Go/Spring, actualizar explícitamente metadatos, compatibilidad, herramientas y tests; no asumir que una versión nueva conserva automáticamente el contrato anterior.
