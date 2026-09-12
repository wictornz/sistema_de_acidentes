from flask import Flask, render_template, request, redirect, url_for, jsonify, flash
import sqlite3
from pathlib import Path
from datetime import datetime

BASE_DIR = Path(__file__).resolve().parent
DB_PATH = BASE_DIR / "acidentes.db"

app = Flask(__name__)
app.secret_key = "hma-acidentes-local"


def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS acidentes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
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
    try:
        conn.execute("ALTER TABLE acidentes ADD COLUMN contato TEXT")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE acidentes ADD COLUMN investigador TEXT")
    except Exception:
        pass
    try:
        conn.execute("ALTER TABLE acidentes ADD COLUMN classificacao TEXT DEFAULT 'Acidente'")
    except Exception:
        pass
    conn.commit()
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
        conn.execute(
            """
            INSERT INTO acidentes (
                data_ocorrencia, classificacao, investigador, colaborador, contato, setor, funcao,
                tipo_ocorrencia, tipo_acidente, parte_corpo, fonte_geradora,
                turno, sexo, exposicao_biologica, perfurocortante,
                fluxograma_seguido, quimioprofilaxia, cat_emitida, data_cat,
                houve_afastamento, dias_afastamento, tipo_contrato,
                observacoes, criado_em
            ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
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
        sql += " AND (colaborador LIKE ? OR matricula LIKE ? OR funcao LIKE ? OR tipo_acidente LIKE ?)"
        params += [like, like, like, like]
    if setor:
        sql += " AND setor = ?"
        params.append(setor)
    if ano:
        sql += " AND substr(data_ocorrencia,1,4) = ?"
        params.append(ano)
    if mes:
        sql += " AND substr(data_ocorrencia,6,2) = ?"
        params.append(mes.zfill(2))
    sql += " ORDER BY data_ocorrencia DESC, id DESC"

    conn = get_db()
    acidentes = conn.execute(sql, params).fetchall()
    setores = conn.execute("SELECT DISTINCT setor FROM acidentes WHERE setor <> '' ORDER BY setor").fetchall()
    anos = conn.execute("SELECT DISTINCT substr(data_ocorrencia,1,4) ano FROM acidentes ORDER BY ano DESC").fetchall()
    conn.close()

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
    conn = get_db()
    acidente = conn.execute("SELECT * FROM acidentes WHERE id = ?", (acidente_id,)).fetchone()
    conn.close()
    if not acidente:
        return "Registro não encontrado", 404
    return render_template("detalhe.html", page="consultar", acidente=acidente)


@app.route("/acidente/<int:acidente_id>/editar", methods=["GET", "POST"])
def editar(acidente_id):
    conn = get_db()
    acidente = conn.execute("SELECT * FROM acidentes WHERE id = ?", (acidente_id,)).fetchone()
    if not acidente:
        conn.close()
        return "Registro não encontrado", 404

        classif = request.form.get("classificacao", "Acidente").strip() or "Acidente"
        conn.execute(
            """
            UPDATE acidentes SET
                data_ocorrencia=?, classificacao=?, investigador=?, colaborador=?, contato=?, matricula=?, setor=?, funcao=?,
                tipo_ocorrencia=?, tipo_acidente=?, parte_corpo=?, fonte_geradora=?,
                turno=?, sexo=?, exposicao_biologica=?, perfurocortante=?,
                fluxograma_seguido=?, quimioprofilaxia=?, cat_emitida=?, data_cat=?,
                houve_afastamento=?, dias_afastamento=?, tipo_contrato=?, observacoes=?
            WHERE id=?
            """,
            (
                request.form["data_ocorrencia"],
                classif,
                request.form.get("investigador", "").strip(),
                request.form["colaborador"].strip(),
                request.form.get("contato", "").strip(),
                request.form.get("matricula", "").strip(), request.form["setor"].strip(),
                request.form.get("funcao", "").strip(), request.form.get("tipo_ocorrencia", "").strip(),
                request.form.get("tipo_acidente", "").strip(), request.form.get("parte_corpo", "").strip(),
                request.form.get("fonte_geradora", "").strip(), request.form.get("turno", ""),
                request.form.get("sexo", ""), checkbox("exposicao_biologica"),
                checkbox("perfurocortante"), checkbox("fluxograma_seguido"),
                checkbox("quimioprofilaxia"), checkbox("cat_emitida"),
                request.form.get("data_cat") or None, checkbox("houve_afastamento"),
                int(request.form.get("dias_afastamento") or 0), request.form.get("tipo_contrato", ""),
                request.form.get("observacoes", "").strip(), acidente_id,
            ),
        )
        conn.commit()
        conn.close()
        flash("Registro atualizado com sucesso.", "success")
        return redirect(url_for("detalhe", acidente_id=acidente_id))

    conn.close()
    return render_template("editar.html", page="consultar", acidente=acidente)


@app.post("/acidente/<int:acidente_id>/excluir")
def excluir(acidente_id):
    conn = get_db()
    conn.execute("DELETE FROM acidentes WHERE id = ?", (acidente_id,))
    conn.commit()
    conn.close()
    flash("Registro excluído.", "success")
    return redirect(url_for("consultar"))


@app.route("/api/dashboard")
def dashboard_data():
    ano = request.args.get("ano", "")
    setor = request.args.get("setor", "")
    conn = get_db()

    where = " WHERE 1=1"
    params = []
    if ano:
        where += " AND substr(data_ocorrencia,1,4)=?"
        params.append(ano)
    if setor:
        where += " AND setor=?"
        params.append(setor)

    total = conn.execute("SELECT COUNT(*) FROM acidentes" + where, params).fetchone()[0]
    dias = conn.execute("SELECT COALESCE(SUM(dias_afastamento),0) FROM acidentes" + where, params).fetchone()[0]
    cat = conn.execute("SELECT COUNT(*) FROM acidentes" + where + " AND cat_emitida=1", params).fetchone()[0]
    afast = conn.execute("SELECT COUNT(*) FROM acidentes" + where + " AND houve_afastamento=1", params).fetchone()[0]

    mensal = conn.execute(
        "SELECT substr(data_ocorrencia,6,2) mes, COUNT(*) qtd FROM acidentes" + where + " GROUP BY mes ORDER BY mes",
        params,
    ).fetchall()
    por_setor = conn.execute(
        "SELECT setor nome, COUNT(*) qtd FROM acidentes" + where + " GROUP BY setor ORDER BY qtd DESC LIMIT 8",
        params,
    ).fetchall()
    por_funcao = conn.execute(
        "SELECT COALESCE(NULLIF(funcao,''),'Não informado') nome, COUNT(*) qtd FROM acidentes" + where + " GROUP BY nome ORDER BY qtd DESC LIMIT 8",
        params,
    ).fetchall()
    por_tipo = conn.execute(
        "SELECT tipo_acidente nome, COUNT(*) qtd FROM acidentes" + where + " GROUP BY tipo_acidente ORDER BY qtd DESC LIMIT 8",
        params,
    ).fetchall()

    linhas_partes = conn.execute(
        "SELECT parte_corpo FROM acidentes" + where + " AND parte_corpo IS NOT NULL AND parte_corpo <> ''",
        params,
    ).fetchall()
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

    anos = [r[0] for r in conn.execute("SELECT DISTINCT substr(data_ocorrencia,1,4) FROM acidentes ORDER BY 1 DESC").fetchall()]
    setores = [r[0] for r in conn.execute("SELECT DISTINCT setor FROM acidentes WHERE setor<>'' ORDER BY setor").fetchall()]
    conn.close()

    meses = {str(i).zfill(2): nome for i, nome in enumerate([
        "", "Jan", "Fev", "Mar", "Abr", "Mai", "Jun", "Jul", "Ago", "Set", "Out", "Nov", "Dez"
    ]) if i}

    return jsonify({
        "kpis": {"total": total, "dias": dias, "cat": cat, "afastamentos": afast},
        "mensal": [{"nome": meses.get(r["mes"], r["mes"]), "qtd": r["qtd"]} for r in mensal],
        "setores": [dict(r) for r in por_setor],
        "funcoes": [dict(r) for r in por_funcao],
        "tipos": [dict(r) for r in por_tipo],
        "partes": por_parte,
        "filtros": {"anos": anos, "setores": setores},
    })


init_db()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
