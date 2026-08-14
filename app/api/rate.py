# ============================================================
# DIMENSION-RATE
# API RATE
# ============================================================

from flask import (
    Blueprint,
    jsonify,
    request,
)

import time

from app.services.pdf_parser import (
    extrair_texto_pdf,
    extrair_metadados_relatorio,
)

from app.services.measurement_service import (
    extrair_medicoes,
    extrair_pontos,
    extrair_pontos_forcados_fora,
)

from app.services.rate_parser import (
    extrair_rate_declarado,
)

from app.services.rate_service import (
    calcular_rate,
)


rate = Blueprint(
    "rate",
    __name__,
    url_prefix="/api/rate"
)


# ============================================================
# ANALISAR PDF
# ============================================================

@rate.route(
    "/analyze",
    methods=["POST"]
)
def analisar_rate():

    inicio_total = time.perf_counter()

    try:

        # ====================================================
        # LIMITE DE UPLOAD
        # ====================================================

        tamanho_requisicao = request.content_length

        if (
            tamanho_requisicao is not None
            and tamanho_requisicao > 50 * 1024 * 1024
        ):
            return jsonify({
                "success": False,
                "error": "O upload excede o limite máximo de 50 MB.",
            }), 413

        # ====================================================
        # ARQUIVO
        # ====================================================

        arquivo = request.files.get(
            "file"
        )

        if arquivo is None:

            return jsonify({
                "success": False,
                "error":
                    "Nenhum arquivo PDF foi enviado."
            }), 400

        if not arquivo.filename:

            return jsonify({
                "success": False,
                "error":
                    "O arquivo PDF não possui nome."
            }), 400

        nome_arquivo = (
            arquivo.filename
        )

        # ====================================================
        # VALIDAR EXTENSÃO
        # ====================================================

        if not nome_arquivo.lower().endswith(
            ".pdf"
        ):

            return jsonify({
                "success": False,
                "error":
                    "O arquivo enviado não é um PDF."
            }), 400

        # ====================================================
        # LER PDF
        # ====================================================

        inicio = time.perf_counter()

        texto = extrair_texto_pdf(
            arquivo
        )

        print(
            f"[RATE] PDF: {time.perf_counter() - inicio:.2f}s "
            f"| {len(texto):,} caracteres"
        )

        if not texto or not texto.strip():

            return jsonify({
                "success": False,
                "error":
                    "Não foi possível extrair texto do PDF."
            }), 422

        metadados = extrair_metadados_relatorio(texto, nome_arquivo=nome_arquivo)

        # ====================================================
        # RATE DECLARADO
        # ====================================================

        rate_declarado = (
            extrair_rate_declarado(
                texto
            )
        )

        # ====================================================
        # MEDIÇÕES
        # ====================================================

        inicio = time.perf_counter()

        medicoes = extrair_medicoes(
            texto
        )

        pontos_detectados = extrair_pontos(
            texto
        )

        pontos_forcados_fora = extrair_pontos_forcados_fora(
            texto
        )

        print(
            f"[RATE] Parsing: {time.perf_counter() - inicio:.2f}s "
            f"| medições={len(medicoes)} "
            f"| LOCs={len(pontos_detectados)} "
            f"| fora={len(pontos_forcados_fora)}"
        )

        if not medicoes:

            return jsonify({
                "success": False,
                "error":
                    (
                        "O PDF foi lido, mas nenhuma "
                        "medição dimensional foi reconhecida."
                    )
            }), 422

        # ====================================================
        # CALCULAR RATE
        # ====================================================

        inicio = time.perf_counter()

        resultado = calcular_rate(
            medicoes=medicoes,
            rate_declarado=rate_declarado,
            pontos_detectados=pontos_detectados,
            pontos_forcados_fora=pontos_forcados_fora,
        )

        print(
            f"[RATE] Cálculo: {time.perf_counter() - inicio:.2f}s"
        )

        resultado_json = (
            resultado.to_dict()
        )

        # ====================================================
        # RESPOSTA
        # ====================================================

        resposta = {

            "success": True,

            "document": {

                "filename":
                    nome_arquivo,

                "part_number": metadados.get("part_number"),
                "drawing_number": metadados.get("drawing_number"),
                "revision": metadados.get("revision"),
                "report_number": metadados.get("report_number"),
                "client": metadados.get("client"),
                "metrologist": metadados.get("metrologist"),
                "piece": metadados.get("piece"),

                "measurements_extracted":
                    resultado.measurements_count,

                # 45 LOCs neste relatório, mas 50 características
                # dimensionais: os 5 itens adicionais são DIST1 + PLANO1..4.
                "locs_detected":
                    len(pontos_detectados),

                "points_calculated":
                    resultado.calculated_points,

                "characteristics_calculated":
                    resultado.calculated_points,

            },

            "rate": {

                "calculated":
                    resultado_json["calculated"],

                "declared":
                    resultado_json["declared"],

                "difference":
                    resultado.difference,

                "consistent":
                    resultado.consistent,

                "status":
                    resultado.status,

            },

            # =================================================
            # RESUMO
            # =================================================

            "summary": {

                "categories":
                    resultado.categories,

            },

            # =================================================
            # NÃO CONFORMIDADES
            # =================================================

            "out_of_tolerance":
                resultado.out_of_tolerance,

            "measurements":
                resultado.measurements_details,

            # Auditoria completa: nenhum LOC é ocultado.
            "points_audit":
                resultado.points_audit,

            "audit": {
                "total_detected":
                    len(resultado.points_audit),
                "with_measurement":
                    sum(
                        1 for p in resultado.points_audit
                        if p["status"] != "SEM_MEDICAO"
                    ),
                "out_of_tolerance":
                    sum(
                        1 for p in resultado.points_audit
                        if p["status"] == "FORA"
                    ),
                "without_measurement":
                    sum(
                        1 for p in resultado.points_audit
                        if p["status"] == "SEM_MEDICAO"
                    ),
            },

        }

        print(
            f"[RATE] TOTAL: "
            f"{time.perf_counter() - inicio_total:.2f}s"
        )

        return jsonify(resposta)

    except Exception as erro:

        import traceback

        traceback.print_exc()

        return jsonify({

            "success": False,

            "error":
                str(erro)

        }), 500