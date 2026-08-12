from flask import Flask, redirect


def create_app():

    app = Flask(
        __name__,
        template_folder="templates",
        static_folder="static",
    )

    # Limite de segurança para uploads de relatórios PDF.
    # Evita que arquivos excessivamente grandes consumam
    # toda a memória do worker do Gunicorn.
    app.config["MAX_CONTENT_LENGTH"] = 50 * 1024 * 1024

    @app.errorhandler(413)
    def arquivo_muito_grande(error):
        from flask import jsonify

        return jsonify({
            "success": False,
            "error": "O PDF excede o limite máximo de 50 MB.",
        }), 413


    # =========================================================
    # ROUTES
    # =========================================================

    from app.routes.rate import rate_page

    app.register_blueprint(
        rate_page
    )


    # =========================================================
    # APIs
    # =========================================================

    from app.api.rate import rate

    app.register_blueprint(
        rate
    )


    # =========================================================
    # ROOT
    # =========================================================

    @app.route("/home")
    def home():

        return redirect("/dashboard")


    return app