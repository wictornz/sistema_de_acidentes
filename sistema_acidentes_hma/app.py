from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import os
from datetime import datetime

import psycopg2
from psycopg2.extras import RealDictCursor


DATABASE_URL = os.getenv("DATABASE_URL")

app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "hma-acidentes-local")


def get_db():
    if not DATABASE_URL:
        raise RuntimeError(
            "A variável de ambiente DATABASE_URL não foi configurada. "
            "No Render, adicione a connection string do Neon em Environment > DATABASE_URL."
        )

    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)


def fetchone(sql, params=()):
    conn = get_db()
    try:
        with conn.cursor() as cur:
            cur.execute(sql, params)
            return cur.fetchone()
    finally:
        conn.close()


def fetchall(sql, params=()):
    conn = get_db()
    try:
        with conn.cursor() as cur:
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
            cur.execute("ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS investigador TEXT")
            cur.execute(
                "ALTER TABLE acidentes ADD COLUMN IF NOT EXISTS classificacao TEXT DEFAULT 'Acidente'"
            )

        conn.commit()
    finally:
        conn.close()


def checkbox(name):
    return 1 if request.form.get(name) == "on" else 0


@app.route("/")
def dashboard():
    return render_template("dashboard.html", page="dashboard")


@app.route("/registrar", methods=["GET", "POST"])
def registrar():
    if request.method == "POST":
        classif = request.form.get("classificacao", "Acidente").strip() or "Acidente"
        conn = get_db()
        try:
            with conn.cursor() as cur:
                cur.execute(
                    """
                    INSERT INTO acidentes (
                        data_ocorrencia, classificacao, investigador, colaborador, contato, setor, funcao,
                        tipo_ocorrencia, tipo_acidente, parte_corpo, fonte_geradora,
                        turno, sexo, exposicao_biologica, perfurocortante,
                        fluxograma_seguido, quimioprofilaxia, cat_emitida, data_cat,
                        houve_afastamento, dias_afastamento, tipo_contrato,
                        observacoes, criado_em
                    ) VALUES (
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,
                        %s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s
                    )
                    """,
                    (
                        request.form["data_ocorrencia"],
                        classif,
                        request.form.get("investigador", "").strip(),
                        request.form["colaborador"].strip(),
                        request.form.get("contato", "").strip(),
                        request.form["setor"].strip(),
                        request.form.get("funcao", "").strip(),
                        request.form.get("tipo_ocorrencia", "").strip(),
                        request.form.get("tipo_acidente", "").strip(),
                        request.form.get("parte_corpo", "").strip(),
                        request.form.get("fonte_geradora", "").strip(),
                        request.form.get("turno", ""),
                        request.form.get("sexo", ""),
                        checkbox("exposicao_biologica"),
                        checkbox("perfurocortante"),
                        checkbox("fluxograma_seguido"),
                        checkbox("quimioprofilaxia"),
                        checkbox("cat_emitida"),
                        request.form.get("data_cat") or None,
                        checkbox("houve_afastamento"),
                        int(request.form.get("dias_afastamento") or 0),
                        request.form.get("tipo_contrato", ""),
                        request.form.get("observacoes", "").strip(),
                        datetime.now().isoformat(timespec="seconds"),
                    ),
                )
            conn.commit()
        finally:
            conn.close()

        flash(f"{classif} registrado com sucesso.", "success")
        return redirect(url_for("consultar"))

    return render_template("registrar.html", page="registrar")


@app.route("/consultar")
def consultar():
    busca = request.args.get("busca", "").strip()
    setor = request.args.get("setor", "").strip()
    ano = request.args.get("ano", "").strip()
    mes = request.args.get("mes", "").strip()

    sql = "SELECT * FROM acidentes WHERE 1=1"
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
def detalhe(acidente_id):
    acidente = fetchone("SELECT * FROM acidentes WHERE id = %s", (acidente_id,))

    if not acidente:
        return "Registro não encontrado", 404

    return render_template("detalhe.html", page="consultar", acidente=acidente)


@app.route("/acidente/<int:acidente_id>/editar", methods=["GET", "POST"])
def editar(acidente_id):
    acidente = fetchone("SELECT * FROM acidentes WHERE id = %s", (acidente_id,))

    if not acidente:
        return "Registro não encontrado", 404

    if request.method == "POST":
        classif = request.form.get("classificacao", "Acidente").strip() or "Acidente"

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
                        houve_afastamento=%s, dias_afastamento=%s, tipo_contrato=%s, observacoes=%s
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
                        request.form.get("turno", ""),
                        request.form.get("sexo", ""),
                        checkbox("exposicao_biologica"),
                        checkbox("perfurocortante"),
                        checkbox("fluxograma_seguido"),
                        checkbox("quimioprofilaxia"),
                        checkbox("cat_emitida"),
                        request.form.get("data_cat") or None,
                        checkbox("houve_afastamento"),
                        int(request.form.get("dias_afastamento") or 0),
                        request.form.get("tipo_contrato", ""),
                        request.form.get("observacoes", "").strip(),
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


@app.route("/api/dashboard")
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

    total = fetchone(
        "SELECT COUNT(*) AS valor FROM acidentes" + where, params_tuple
    )["valor"]
    dias = fetchone(
        "SELECT COALESCE(SUM(dias_afastamento),0) AS valor FROM acidentes" + where,
        params_tuple,
    )["valor"]
    cat = fetchone(
        "SELECT COUNT(*) AS valor FROM acidentes" + where + " AND cat_emitida=1",
        params_tuple,
    )["valor"]
    afast = fetchone(
        "SELECT COUNT(*) AS valor FROM acidentes" + where + " AND houve_afastamento=1",
        params_tuple,
    )["valor"]

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
            "kpis": {"total": total, "dias": dias, "cat": cat, "afastamentos": afast},
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


init_db()


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
