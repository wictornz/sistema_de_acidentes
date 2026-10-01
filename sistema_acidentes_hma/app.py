import os
import sqlite3
from datetime import datetime
from functools import wraps
import urllib.parse

from flask import (
    Flask,
    flash,
    jsonify,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from werkzeug.security import check_password_hash, generate_password_hash

# Módulos condicionais de banco de dados
psycopg2 = None
RealDictCursor = None
pg8000_dbapi = None
DB_DRIVER = None

try:
    import psycopg2 as _psycopg2
    from psycopg2.extras import RealDictCursor as _RealDictCursor
    psycopg2 = _psycopg2
    RealDictCursor = _RealDictCursor
    DB_DRIVER = "psycopg2"
except Exception:
    psycopg2 = None

try:
    import pg8000.dbapi as _pg8000_dbapi
    pg8000_dbapi = _pg8000_dbapi
    if not DB_DRIVER:
        DB_DRIVER = "pg8000"
except Exception:
    pg8000_dbapi = None

if not DB_DRIVER:
    DB_DRIVER = "sqlite"

DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hma-acidentes-local-segredo-2024")
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
)


class DictCursorWrapper:
    """Wrapper para padronizar o retorno de cursores em dicts de forma transparente."""
    def __init__(self, cursor, is_sqlite=False):
        self.cursor = cursor
        self.is_sqlite = is_sqlite

    def __enter__(self):
        if hasattr(self.cursor, "__enter__"):
            self.cursor.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.cursor, "__exit__"):
            return self.cursor.__exit__(exc_type, exc_val, exc_tb)
        if hasattr(self.cursor, "close"):
            self.cursor.close()

    def __iter__(self):
        return self

    def __next__(self):
        row = self.fetchone()
        if row is None:
            raise StopIteration
        return row

    def execute(self, sql, params=()):
        if self.is_sqlite:
            sql = sql.replace("%s", "?").replace("ILIKE", "LIKE")
            sql = sql.replace("SERIAL PRIMARY KEY", "INTEGER PRIMARY KEY AUTOINCREMENT")
            sql = sql.replace("ADD COLUMN IF NOT EXISTS", "ADD COLUMN")
        return self.cursor.execute(sql, params)

    def fetchone(self):
        row = self.cursor.fetchone()
        if not row:
            return None
        if isinstance(row, dict):
            return row
        if hasattr(row, "keys"):
            return dict(row)
        if hasattr(self.cursor, "description") and self.cursor.description:
            colnames = [d[0] for d in self.cursor.description]
            return dict(zip(colnames, row))
        return row

    def fetchall(self):
        rows = self.cursor.fetchall()
        if not rows:
            return []
        if hasattr(self.cursor, "description") and self.cursor.description:
            colnames = [d[0] for d in self.cursor.description]
            result = []
            for r in rows:
                if isinstance(r, dict):
                    result.append(r)
                elif hasattr(r, "keys"):
                    result.append(dict(r))
                else:
                    result.append(dict(zip(colnames, r)))
            return result
        return rows

    def __getattr__(self, name):
        return getattr(self.cursor, name)


class ConnWrapper:
    """Wrapper para padronizar cursores e encerramento de conexões."""
    def __init__(self, conn, is_sqlite=False, driver_name="sqlite"):
        self.conn = conn
        self.is_sqlite = is_sqlite
        self.driver_name = driver_name

    def __enter__(self):
        if hasattr(self.conn, "__enter__"):
            self.conn.__enter__()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if hasattr(self.conn, "__exit__"):
            return self.conn.__exit__(exc_type, exc_val, exc_tb)
        if hasattr(self.conn, "close"):
            self.conn.close()

    def cursor(self):
        if self.driver_name == "psycopg2" and RealDictCursor:
            cur = self.conn.cursor(cursor_factory=RealDictCursor)
            return DictCursorWrapper(cur, is_sqlite=False)
        else:
            cur = self.conn.cursor()
            return DictCursorWrapper(cur, is_sqlite=self.is_sqlite)

    def commit(self):
        return self.conn.commit()

    def close(self):
        return self.conn.close()


def get_db():
    global DB_DRIVER, DATABASE_URL, psycopg2, pg8000_dbapi

    if DATABASE_URL:
        if DB_DRIVER == "psycopg2" and psycopg2 is not None:
            try:
                conn = psycopg2.connect(DATABASE_URL)
                return ConnWrapper(conn, is_sqlite=False, driver_name="psycopg2")
            except Exception as e:
                print(f"Aviso psycopg2 falhou, tentando pg8000: {e}")

        # Tenta conectar via pg8000 (Pure Python, sem DLLs binárias C)
        if pg8000_dbapi is not None:
            try:
                url = urllib.parse.urlparse(DATABASE_URL)
                user = url.username or "postgres"
                password = url.password or ""
                host = url.hostname or "localhost"
                port = url.port or 5432
                database = url.path.lstrip("/") or "postgres"

                ssl_ctx = True if ("neon.tech" in host or "sslmode" in DATABASE_URL or "render.com" in host) else None

                conn = pg8000_dbapi.connect(
                    user=user,
                    password=password,
                    host=host,
                    port=port,
                    database=database,
                    ssl_context=ssl_ctx
                )
                return ConnWrapper(conn, is_sqlite=False, driver_name="pg8000")
            except Exception as e:
                print(f"Aviso conexao PostgreSQL falhou: {e}. Usando SQLite local.")

    # Fallback local com SQLite (acidentes.db)
    db_path = os.path.join(os.path.dirname(__file__), "acidentes.db")
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return ConnWrapper(conn, is_sqlite=True, driver_name="sqlite")


def fetchone(sql, params=()):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchone()
    finally:
        conn.close()


def fetchall(sql, params=()):
    conn = get_db()
    try:
        cur = conn.cursor()
        cur.execute(sql, params)
        return cur.fetchall()
    finally:
        conn.close()


def init_db():
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS acidentes (
                    id SERIAL PRIMARY KEY,
                    data_ocorrencia TEXT NOT NULL,
                    classificacao TEXT DEFAULT 'Acidente',
                    investigador TEXT,
                    colaborador TEXT NOT NULL,
                    contato TEXT,
                    matricula TEXT,
                    setor TEXT NOT NULL,
                    funcao TEXT,
                    tipo_ocorrencia TEXT,
                    tipo_acidente TEXT NOT NULL,
                    parte_corpo TEXT,
                    fonte_geradora TEXT,
                    turno TEXT,
                    sexo TEXT,
                    exposicao_biologica INTEGER DEFAULT 0,
                    perfurocortante INTEGER DEFAULT 0,
                    fluxograma_seguido INTEGER DEFAULT 0,
                    quimioprofilaxia INTEGER DEFAULT 0,
                    cat_emitida INTEGER DEFAULT 0,
                    data_cat TEXT,
                    houve_afastamento INTEGER DEFAULT 0,
                    dias_afastamento INTEGER DEFAULT 0,
                    tipo_contrato TEXT,
                    observacoes TEXT,
                    criado_em TEXT NOT NULL
                )
                """
            )

            # Mantém compatibilidade caso a tabela já exista com uma versão anterior.
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS contato TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS matricula TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS investigador TEXT")
            cur.execute(
                "ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS classificacao TEXT DEFAULT 'Acidente'"
            )
            # Campos de Acidente Biológico x Não biológico
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS tipo_biologico TEXT DEFAULT 'Não biológico'")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS tipo_exposicao TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS paciente_fonte TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS paciente_fonte_info TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS perf_dispositivo_seguranca TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS sangue_visivel TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS colaborador_usando_epi TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS momento_exposicao TEXT")

            # Campos novos do colaborador e da ocorrência
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS turno_trabalhador TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS hora_acidente TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS local_acidente TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS turno_acidente TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS epi_dispositivo_seguranca TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS acao_corretiva TEXT")

            # Dados médicos
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS medico_nome_crm TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS unidade_atendimento TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS data_atendimento TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS necessidade_afastamento TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS dias_afastamento_tratamento INTEGER DEFAULT 0")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS cid TEXT")
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS descricao_medica TEXT")

            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS usuarios (
                    id SERIAL PRIMARY KEY,
                    nome TEXT NOT NULL,
                    email TEXT UNIQUE NOT NULL,
                    senha_hash TEXT NOT NULL,
                    tipo TEXT NOT NULL DEFAULT 'funcionario',
                    ativo BOOLEAN NOT NULL DEFAULT TRUE,
                    criado_em TEXT NOT NULL
                )
                """
            )

        conn.commit()
    finally:
        conn.close()


@app.template_filter("format_date")
def format_date_filter(val):
    if not val:
        return "-"
    s = str(val).strip()
    if len(s) >= 10 and s[4] == "-" and s[7] == "-":
        return f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
    return s


def checkbox(name):
    return 1 if request.form.get(name) == "on" else 0


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            if request.path.startswith("/api/"):
                return jsonify({"error": "Não autenticado."}), 401
            flash("Faça login para acessar o sistema.", "warning")
            return redirect(url_for("login", next=request.path))
        return f(*args, **kwargs)

    return decorated_function


def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if "usuario_id" not in session:
            flash("Faça login para acessar esta página.", "warning")
            return redirect(url_for("login", next=request.path))
        if session.get("usuario_tipo") != "admin":
            flash("Acesso negado. Esta área é restrita para administradores.", "danger")
            return redirect(url_for("dashboard"))
        return f(*args, **kwargs)

    return decorated_function


@app.context_processor
def inject_user():
    if "usuario_id" in session:
        return {
            "usuario_atual": {
                "id": session.get("usuario_id"),
                "nome": session.get("usuario_nome"),
                "email": session.get("usuario_email"),
                "tipo": session.get("usuario_tipo"),
                "is_admin": session.get("usuario_tipo") == "admin",
            }
        }
    return {"usuario_atual": None}


def get_acidente_com_numero(acidente_id):
    """Retorna o registro do acidente incluindo a numeração visual sequencial (posição na lista)."""
    return fetchone(
        """
        WITH base_acidentes AS (
            SELECT *, ROW_NUMBER() OVER (ORDER BY id ASC) AS numero FROM acidentes
        )
        SELECT * FROM base_acidentes WHERE id = %s
        """,
        (acidente_id,),
    )


# ── ROTAS DE AUTENTICAÇÃO E CONTA ──

@app.route("/login", methods=["GET", "POST"])
def login():
    if "usuario_id" in session:
        return redirect(url_for("dashboard"))

    if request.method == "POST":
        email = request.form.get("email", "").strip().lower()
        senha = request.form.get("senha", "")

        if not email or not senha:
            flash("Informe o e-mail e a senha para entrar.", "warning")
            return redirect(url_for("login"))

        usuario = fetchone(
            "SELECT id, nome, email, senha_hash, tipo, ativo FROM usuarios WHERE LOWER(email) = %s",
            (email,),
        )

        # Regra 3: Se o usuário não existir, negar o acesso.
        if not usuario:
            flash("E-mail ou senha incorretos.", "danger")
            return redirect(url_for("login"))

        # Regra 4 & 5: Se ativo for FALSE, negar o acesso.
        if not usuario["ativo"]:
            flash("Sua conta está desativada. Entre em contato com o administrador.", "danger")
            return redirect(url_for("login"))

        # Regra 6 & 7: Verificar a senha utilizando o hash armazenado no banco.
        if not check_password_hash(usuario["senha_hash"], senha):
            flash("E-mail ou senha incorretos.", "danger")
            return redirect(url_for("login"))

        # Regra 8 & 9: Autenticar o usuário e criar sessão segura
        session.clear()
        session["usuario_id"] = usuario["id"]
        session["usuario_nome"] = usuario["nome"]
        session["usuario_email"] = usuario["email"]
        session["usuario_tipo"] = usuario["tipo"]

        flash(f"Olá, {usuario['nome']}! Login realizado com sucesso.", "success")
        next_page = request.form.get("next") or request.args.get("next")
        if next_page and next_page.startswith("/"):
            return redirect(next_page)
        return redirect(url_for("dashboard"))

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Sessão finalizada com sucesso.", "info")
    return redirect(url_for("login"))


# ── ROTAS ADMINISTRATIVAS (GESTÃO DE FUNCIONÁRIOS) ──

@app.route("/admin/usuarios")
@admin_required
def admin_usuarios():
    usuarios = fetchall(
        "SELECT id, nome, email, tipo, ativo, criado_em FROM usuarios ORDER BY id ASC"
    )
    for u in usuarios:
        c = u.get("criado_em")
        if hasattr(c, "strftime"):
            u["data_cadastro"] = c.strftime("%d/%m/%Y")
        elif c:
            s = str(c)[:10]
            if len(s) == 10 and s[4] == "-" and s[7] == "-":
                u["data_cadastro"] = f"{s[8:10]}/{s[5:7]}/{s[0:4]}"
            else:
                u["data_cadastro"] = s
        else:
            u["data_cadastro"] = "-"

    return render_template("admin_usuarios.html", page="usuarios", usuarios=usuarios)


@app.post("/admin/usuarios/novo")
@admin_required
def admin_criar_usuario():
    nome = request.form.get("nome", "").strip()
    email = request.form.get("email", "").strip().lower()
    senha = request.form.get("senha", "").strip()

    if not nome or not email or not senha:
        flash("Todos os campos são obrigatórios.", "warning")
        return redirect(url_for("admin_usuarios"))

    # Verifica se já existe usuário com este e-mail
    usuario_existente = fetchone(
        "SELECT id FROM usuarios WHERE LOWER(email) = %s",
        (email,),
    )
    if usuario_existente:
        flash("Já existe um usuário cadastrado com este e-mail.", "danger")
        return redirect(url_for("admin_usuarios"))

    # Gera hash seguro da senha
    senha_hash = generate_password_hash(senha)

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO usuarios (nome, email, senha_hash, tipo, ativo, criado_em)
                VALUES (%s, %s, %s, %s, %s, %s)
                """,
                (
                    nome,
                    email,
                    senha_hash,
                    "funcionario",
                    True,
                    datetime.now().isoformat(timespec="seconds"),
                ),
            )
        conn.commit()
    finally:
        conn.close()

    flash(f"Funcionário(a) {nome} cadastrado(a) com sucesso!", "success")
    return redirect(url_for("admin_usuarios"))


@app.post("/admin/usuarios/<int:usuario_id>/status")
@admin_required
def admin_toggle_status(usuario_id):
    if usuario_id == session.get("usuario_id"):
        flash("Você não pode alterar o status da sua própria conta.", "danger")
        return redirect(url_for("admin_usuarios"))

    usuario = fetchone(
        "SELECT id, nome, ativo FROM usuarios WHERE id = %s",
        (usuario_id,),
    )
    if not usuario:
        flash("Usuário não encontrado.", "danger")
        return redirect(url_for("admin_usuarios"))

    novo_status = not usuario["ativo"]

    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(
                "UPDATE usuarios SET ativo = %s WHERE id = %s",
                (novo_status, usuario_id),
            )
        conn.commit()
    finally:
        conn.close()

    acao = "ativado" if novo_status else "desativado"
    flash(f"O acesso do usuário {usuario['nome']} foi {acao} com sucesso.", "success")
    return redirect(url_for("admin_usuarios"))


# ── ROTAS DO SISTEMA DE ACIDENTES ──

@app.route("/")
@login_required
def dashboard():
    return render_template("dashboard.html", page="dashboard")


@app.route("/registrar", methods=["GET", "POST"])
@login_required
def registrar():
    if request.method == "POST":
        classif = request.form.get("classificacao", "Acidente").strip() or "Acidente"
        tipo_bio = request.form.get("tipo_biologico", "Não biológico").strip() or "Não biológico"
        is_bio = 1 if tipo_bio == "Biológico" or checkbox("exposicao_biologica") else 0
        nec_afast = request.form.get("necessidade_afastamento", "").strip()
        houve_afast = 1 if (nec_afast == "Sim" or checkbox("houve_afastamento")) else 0
        dias_afast = int(request.form.get("dias_afastamento_tratamento") or request.form.get("dias_afastamento") or 0)

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO acidentes (
                        data_ocorrencia, classificacao, investigador, colaborador, contato, matricula, setor, funcao,
                        tipo_ocorrencia, tipo_acidente, parte_corpo, fonte_geradora,
                        turno, sexo, exposicao_biologica, perfurocortante,
                        fluxograma_seguido, quimioprofilaxia, cat_emitida, data_cat,
                        houve_afastamento, dias_afastamento, tipo_contrato,
                        observacoes, criado_em,
                        tipo_biologico, tipo_exposicao, paciente_fonte, paciente_fonte_info,
                        perf_dispositivo_seguranca, sangue_visivel, colaborador_usando_epi, momento_exposicao,
                        turno_trabalhador, hora_acidente, local_acidente, turno_acidente,
                        epi_dispositivo_seguranca, acao_corretiva,
                        medico_nome_crm, unidade_atendimento, data_atendimento,
                        necessidade_afastamento, dias_afastamento_tratamento, cid, descricao_medica
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,
                        %s,%s,%s,%s,
                        %s,%s,%s,%s,
                        %s,%s,%s,
                        %s,%s,
                        %s,%s,%s,%s,
                        %s,%s,%s,%s,
                        %s,%s,%s,%s,
                        %s,%s,
                        %s,%s,%s,
                        %s,%s,%s,%s
                    )
                    """,
                    (
                        request.form["data_ocorrencia"],
                        classif,
                        request.form.get("investigador", "").strip(),
                        request.form["colaborador"].strip(),
                        request.form.get("contato", "").strip(),
                        request.form.get("matricula", "").strip(),
                        request.form["setor"].strip(),
                        request.form.get("funcao", "").strip(),
                        request.form.get("tipo_ocorrencia", "").strip(),
                        request.form.get("tipo_acidente", "").strip(),
                        request.form.get("parte_corpo", "").strip(),
                        request.form.get("fonte_geradora", "").strip(),
                        request.form.get("turno_acidente") or request.form.get("turno", ""),
                        request.form.get("sexo", ""),
                        is_bio,
                        checkbox("perfurocortante"),
                        checkbox("fluxograma_seguido"),
                        checkbox("quimioprofilaxia"),
                        checkbox("cat_emitida"),
                        request.form.get("data_cat") or None,
                        houve_afast,
                        dias_afast,
                        request.form.get("tipo_contrato", ""),
                        request.form.get("observacoes", "").strip(),
                        datetime.now().isoformat(timespec="seconds"),
                        tipo_bio,
                        request.form.get("tipo_exposicao", "").strip(),
                        request.form.get("paciente_fonte", "").strip(),
                        request.form.get("paciente_fonte_info", "").strip(),
                        request.form.get("perf_dispositivo_seguranca", "").strip(),
                        request.form.get("sangue_visivel", "").strip(),
                        request.form.get("colaborador_usando_epi", "").strip(),
                        request.form.get("momento_exposicao", "").strip(),
                        request.form.get("turno_trabalhador", "").strip(),
                        request.form.get("hora_acidente", "").strip(),
                        request.form.get("local_acidente", "").strip(),
                        request.form.get("turno_acidente", "").strip(),
                        request.form.get("epi_dispositivo_seguranca", "").strip(),
                        request.form.get("acao_corretiva", "").strip(),
                        request.form.get("medico_nome_crm", "").strip(),
                        request.form.get("unidade_atendimento", "").strip(),
                        request.form.get("data_atendimento") or None,
                        nec_afast,
                        dias_afast,
                        request.form.get("cid", "").strip(),
                        request.form.get("descricao_medica", "").strip(),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

        flash(f"{classif} registrado com sucesso.", "success")
        return redirect(url_for("consultar"))

    return render_template("registrar.html", page="registrar")


@app.route("/consultar")
@login_required
def consultar():
    busca = request.args.get("busca", "").strip()
    setor = request.args.get("setor", "").strip()
    ano = request.args.get("ano", "").strip()
    mes = request.args.get("mes", "").strip()

    # Numeração sequencial baseada na ordem cronológica de registro (id ASC)
    sql = """
        WITH base_acidentes AS (
            SELECT *, ROW_NUMBER() OVER (ORDER BY id ASC) AS numero FROM acidentes
        )
        SELECT * FROM base_acidentes WHERE 1=1
    """
    params = []

    if busca:
        like = f"%{busca}%"
        sql += " AND (colaborador ILIKE %s OR contato ILIKE %s OR matricula ILIKE %s OR funcao ILIKE %s OR tipo_acidente ILIKE %s)"
        params += [like, like, like, like, like]

    if setor:
        sql += " AND setor = %s"
        params.append(setor)

    if ano:
        sql += " AND substring(data_ocorrencia,1,4) = %s"
        params.append(ano)

    if mes:
        sql += " AND substring(data_ocorrencia,6,2) = %s"
        params.append(mes.zfill(2))

    sql += " ORDER BY data_ocorrencia DESC, id DESC"

    acidentes = fetchall(sql, tuple(params))
    setores = fetchall(
        "SELECT DISTINCT setor FROM acidentes WHERE setor <> '' ORDER BY setor"
    )
    anos = fetchall(
        "SELECT DISTINCT substring(data_ocorrencia,1,4) AS ano FROM acidentes ORDER BY ano DESC"
    )

    return render_template(
        "consultar.html",
        page="consultar",
        acidentes=acidentes,
        setores=setores,
        anos=anos,
        filtros={"busca": busca, "setor": setor, "ano": ano, "mes": mes},
    )


@app.route("/acidente/<int:acidente_id>")
@login_required
def detalhe(acidente_id):
    acidente = get_acidente_com_numero(acidente_id)

    if not acidente:
        return "Registro não encontrado", 404

    return render_template("detalhe.html", page="consultar", acidente=acidente)


@app.route("/acidente/<int:acidente_id>/imprimir")
@login_required
def imprimir(acidente_id):
    acidente = get_acidente_com_numero(acidente_id)

    if not acidente:
        return "Registro não encontrado", 404

    return render_template("imprimir.html", acidente=acidente)


@app.route("/acidente/<int:acidente_id>/editar", methods=["GET", "POST"])
@login_required
def editar(acidente_id):
    acidente = get_acidente_com_numero(acidente_id)

    if not acidente:
        return "Registro não encontrado", 404

    if request.method == "POST":
        classif = request.form.get("classificacao", "Acidente").strip() or "Acidente"
        tipo_bio = request.form.get("tipo_biologico", "Não biológico").strip() or "Não biológico"
        is_bio = 1 if tipo_bio == "Biológico" or checkbox("exposicao_biologica") else 0
        nec_afast = request.form.get("necessidade_afastamento", "").strip()
        houve_afast = 1 if (nec_afast == "Sim" or checkbox("houve_afastamento")) else 0
        dias_afast = int(request.form.get("dias_afastamento_tratamento") or request.form.get("dias_afastamento") or 0)

        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    UPDATE acidentes SET
                        data_ocorrencia=%s, classificacao=%s, investigador=%s, colaborador=%s,
                        contato=%s, matricula=%s, setor=%s, funcao=%s,
                        tipo_ocorrencia=%s, tipo_acidente=%s, parte_corpo=%s, fonte_geradora=%s,
                        turno=%s, sexo=%s, exposicao_biologica=%s, perfurocortante=%s,
                        fluxograma_seguido=%s, quimioprofilaxia=%s, cat_emitida=%s, data_cat=%s,
                        houve_afastamento=%s, dias_afastamento=%s, tipo_contrato=%s, observacoes=%s,
                        tipo_biologico=%s, tipo_exposicao=%s, paciente_fonte=%s, paciente_fonte_info=%s,
                        perf_dispositivo_seguranca=%s, sangue_visivel=%s, colaborador_usando_epi=%s, momento_exposicao=%s,
                        turno_trabalhador=%s, hora_acidente=%s, local_acidente=%s, turno_acidente=%s,
                        epi_dispositivo_seguranca=%s, acao_corretiva=%s,
                        medico_nome_crm=%s, unidade_atendimento=%s, data_atendimento=%s,
                        necessidade_afastamento=%s, dias_afastamento_tratamento=%s, cid=%s, descricao_medica=%s
                    WHERE id=%s
                    """,
                    (
                        request.form["data_ocorrencia"],
                        classif,
                        request.form.get("investigador", "").strip(),
                        request.form["colaborador"].strip(),
                        request.form.get("contato", "").strip(),
                        request.form.get("matricula", "").strip(),
                        request.form["setor"].strip(),
                        request.form.get("funcao", "").strip(),
                        request.form.get("tipo_ocorrencia", "").strip(),
                        request.form.get("tipo_acidente", "").strip(),
                        request.form.get("parte_corpo", "").strip(),
                        request.form.get("fonte_geradora", "").strip(),
                        request.form.get("turno_acidente") or request.form.get("turno", ""),
                        request.form.get("sexo", ""),
                        is_bio,
                        checkbox("perfurocortante"),
                        checkbox("fluxograma_seguido"),
                        checkbox("quimioprofilaxia"),
                        checkbox("cat_emitida"),
                        request.form.get("data_cat") or None,
                        houve_afast,
                        dias_afast,
                        request.form.get("tipo_contrato", ""),
                        request.form.get("observacoes", "").strip(),
                        tipo_bio,
                        request.form.get("tipo_exposicao", "").strip(),
                        request.form.get("paciente_fonte", "").strip(),
                        request.form.get("paciente_fonte_info", "").strip(),
                        request.form.get("perf_dispositivo_seguranca", "").strip(),
                        request.form.get("sangue_visivel", "").strip(),
                        request.form.get("colaborador_usando_epi", "").strip(),
                        request.form.get("momento_exposicao", "").strip(),
                        request.form.get("turno_trabalhador", "").strip(),
                        request.form.get("hora_acidente", "").strip(),
                        request.form.get("local_acidente", "").strip(),
                        request.form.get("turno_acidente", "").strip(),
                        request.form.get("epi_dispositivo_seguranca", "").strip(),
                        request.form.get("acao_corretiva", "").strip(),
                        request.form.get("medico_nome_crm", "").strip(),
                        request.form.get("unidade_atendimento", "").strip(),
                        request.form.get("data_atendimento") or None,
                        nec_afast,
                        dias_afast,
                        request.form.get("cid", "").strip(),
                        request.form.get("descricao_medica", "").strip(),
                        acidente_id,
                    ),
                )
            conn.commit()
        finally:
            conn.close()

        flash("Registro atualizado com sucesso.", "success")
        return redirect(url_for("detalhe", acidente_id=acidente_id))

    return render_template("editar.html", page="consultar", acidente=acidente)


@app.post("/acidente/<int:acidente_id>/excluir")
@login_required
def excluir(acidente_id):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute("DELETE FROM acidentes WHERE id = %s", (acidente_id,))
        conn.commit()
    finally:
        conn.close()

    flash("Registro excluído.", "success")
    return redirect(url_for("consultar"))


@app.route("/graficos")
@login_required
def graficos():
    return render_template("graficos.html", page="graficos")


@app.route("/api/graficos")
@login_required
def graficos_data():
    classificacao = request.args.get("classificacao", "Acidente").strip()
    cargo = request.args.get("cargo", "").strip()
    setor = request.args.get("setor", "").strip()
    mes = request.args.get("mes", "").strip()
    ano = request.args.get("ano", "").strip()

    where = " WHERE 1=1"
    params = []

    if classificacao and classificacao != "Todos":
        where += " AND classificacao = %s"
        params.append(classificacao)

    if cargo:
        where += " AND funcao = %s"
        params.append(cargo)

    if setor:
        where += " AND setor = %s"
        params.append(setor)

    if mes:
        where += " AND substring(data_ocorrencia,6,2) = %s"
        params.append(mes.zfill(2))

    if ano:
        where += " AND substring(data_ocorrencia,1,4) = %s"
        params.append(ano)

    params_tuple = tuple(params)

    # 1. Cargos (Funções)
    por_cargo = fetchall(
        "SELECT COALESCE(NULLIF(funcao,''),'Não informado') AS nome, COUNT(*) AS qtd "
        "FROM acidentes" + where + " GROUP BY COALESCE(NULLIF(funcao,''),'Não informado') ORDER BY qtd DESC LIMIT 10",
        params_tuple,
    )

    # 2. Setor
    por_setor = fetchall(
        "SELECT COALESCE(NULLIF(setor,''),'Não informado') AS nome, COUNT(*) AS qtd "
        "FROM acidentes" + where + " GROUP BY COALESCE(NULLIF(setor,''),'Não informado') ORDER BY qtd DESC LIMIT 10",
        params_tuple,
    )

    # 3. Local onde ocorreu o acidente
    por_local = fetchall(
        "SELECT COALESCE(NULLIF(local_acidente,''),'Não informado') AS nome, COUNT(*) AS qtd "
        "FROM acidentes" + where + " GROUP BY COALESCE(NULLIF(local_acidente,''),'Não informado') ORDER BY qtd DESC LIMIT 10",
        params_tuple,
    )

    # 4. Tipo de exposição (considerando apenas os acidentes biológicos)
    where_bio = where + " AND (tipo_biologico = 'Biológico' OR exposicao_biologica = 1) AND tipo_exposicao IS NOT NULL AND tipo_exposicao <> ''"
    por_exposicao = fetchall(
        "SELECT tipo_exposicao AS nome, COUNT(*) AS qtd "
        "FROM acidentes" + where_bio + " GROUP BY tipo_exposicao ORDER BY qtd DESC",
        params_tuple,
    )

    # 5. Período do dia (Turno)
    por_periodo = fetchall(
        "SELECT COALESCE(NULLIF(turno_acidente,''), NULLIF(turno,''), 'Não informado') AS nome, COUNT(*) AS qtd "
        "FROM acidentes" + where + " GROUP BY COALESCE(NULLIF(turno_acidente,''), NULLIF(turno,''), 'Não informado') ORDER BY qtd DESC",
        params_tuple,
    )

    # 6. Partes do corpo atingidas
    linhas_partes = fetchall(
        "SELECT parte_corpo FROM acidentes" + where + " AND parte_corpo IS NOT NULL AND parte_corpo <> ''",
        params_tuple,
    )
    contagem_partes = {}
    for row in linhas_partes:
        partes = [p.strip() for p in (row["parte_corpo"] or "").split(",") if p.strip()]
        for p in partes:
            contagem_partes[p] = contagem_partes.get(p, 0) + 1

    por_parte = sorted(
        [{"nome": k, "qtd": v} for k, v in contagem_partes.items()],
        key=lambda x: x["qtd"],
        reverse=True,
    )[:10]

    # Opções para os filtros
    cargos_rows = fetchall(
        "SELECT DISTINCT funcao FROM acidentes WHERE funcao IS NOT NULL AND funcao <> '' ORDER BY funcao"
    )
    setores_rows = fetchall(
        "SELECT DISTINCT setor FROM acidentes WHERE setor IS NOT NULL AND setor <> '' ORDER BY setor"
    )
    anos_rows = fetchall(
        "SELECT DISTINCT substring(data_ocorrencia,1,4) AS ano FROM acidentes WHERE data_ocorrencia <> '' ORDER BY ano DESC"
    )

    return jsonify(
        {
            "cargos": por_cargo,
            "setores": por_setor,
            "locais": por_local,
            "exposicoes": por_exposicao,
            "periodos": por_periodo,
            "partes": por_parte,
            "filtros": {
                "cargos": [r["funcao"] for r in cargos_rows],
                "setores": [r["setor"] for r in setores_rows],
                "anos": [r["ano"] for r in anos_rows],
            },
        }
    )


@app.route("/api/dashboard")
@login_required
def dashboard_data():
    ano = request.args.get("ano", "")
    setor = request.args.get("setor", "")

    where = " WHERE 1=1"
    params = []

    if ano:
        where += " AND substring(data_ocorrencia,1,4)=%s"
        params.append(ano)

    if setor:
        where += " AND setor=%s"
        params.append(setor)

    params_tuple = tuple(params)

    res_total = fetchone(
        "SELECT COUNT(*) AS valor FROM acidentes" + where, params_tuple
    )
    total = res_total["valor"] if res_total and "valor" in res_total and res_total["valor"] is not None else 0

    # Item 3: Contar QUANTAS PESSOAS foram afastadas do trabalho (necessidade de afastamento = Sim / houve_afastamento = 1)
    res_afast = fetchone(
        "SELECT COUNT(*) AS valor FROM acidentes" + where + " AND (houve_afastamento=1 OR necessidade_afastamento='Sim' OR dias_afastamento > 0 OR dias_afastamento_tratamento > 0)",
        params_tuple,
    )
    afast = res_afast["valor"] if res_afast and "valor" in res_afast and res_afast["valor"] is not None else 0

    res_cat = fetchone(
        "SELECT COUNT(*) AS valor FROM acidentes" + where + " AND cat_emitida=1",
        params_tuple,
    )
    cat = res_cat["valor"] if res_cat and "valor" in res_cat and res_cat["valor"] is not None else 0

    mensal = fetchall(
        "SELECT substring(data_ocorrencia,6,2) AS mes, COUNT(*) AS qtd "
        "FROM acidentes" + where + " GROUP BY mes ORDER BY mes",
        params_tuple,
    )

    por_setor = fetchall(
        "SELECT setor AS nome, COUNT(*) AS qtd FROM acidentes"
        + where
        + " GROUP BY setor ORDER BY qtd DESC LIMIT 8",
        params_tuple,
    )

    por_funcao = fetchall(
        "SELECT COALESCE(NULLIF(funcao,''),'Não informado') AS nome, COUNT(*) AS qtd "
        "FROM acidentes"
        + where
        + " GROUP BY COALESCE(NULLIF(funcao,''),'Não informado') ORDER BY qtd DESC LIMIT 8",
        params_tuple,
    )

    por_tipo = fetchall(
        "SELECT tipo_acidente AS nome, COUNT(*) AS qtd FROM acidentes"
        + where
        + " GROUP BY tipo_acidente ORDER BY qtd DESC LIMIT 8",
        params_tuple,
    )

    linhas_partes = fetchall(
        "SELECT parte_corpo FROM acidentes"
        + where
        + " AND parte_corpo IS NOT NULL AND parte_corpo <> ''",
        params_tuple,
    )

    contagem_partes = {}
    for row in linhas_partes:
        partes = [p.strip() for p in (row["parte_corpo"] or "").split(",") if p.strip()]
        for p in partes:
            contagem_partes[p] = contagem_partes.get(p, 0) + 1

    por_parte = sorted(
        [{"nome": k, "qtd": v} for k, v in contagem_partes.items()],
        key=lambda x: x["qtd"],
        reverse=True,
    )[:8]

    anos_rows = fetchall(
        "SELECT DISTINCT substring(data_ocorrencia,1,4) AS ano FROM acidentes ORDER BY ano DESC"
    )
    setores_rows = fetchall(
        "SELECT DISTINCT setor FROM acidentes WHERE setor<>'' ORDER BY setor"
    )

    anos = [r["ano"] for r in anos_rows]
    setores = [r["setor"] for r in setores_rows]

    meses = {
        str(i).zfill(2): nome
        for i, nome in enumerate(
            ["", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"]
        )
        if i
    }

    return jsonify(
        {
            "kpis": {"total": total, "dias": afast, "cat": cat, "afastamentos": afast},
            "mensal": [
                {"nome": meses.get(r["mes"], r["mes"]), "qtd": r["qtd"]}
                for r in mensal
            ],
            "setores": por_setor,
            "funcoes": por_funcao,
            "tipos": por_tipo,
            "partes": por_parte,
            "filtros": {"anos": anos, "setores": setores},
        }
    )


if DATABASE_URL:
    try:
        init_db()
    except Exception as e:
        print(f"Aviso ao inicializar tabelas: {e}")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)

