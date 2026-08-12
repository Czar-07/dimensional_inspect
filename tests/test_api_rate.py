import io

from app import create_app


PDF_PATH = "uploads/relatorio_teste.pdf"


app = create_app()

app.config["TESTING"] = True


client = app.test_client()


with open(
    PDF_PATH,
    "rb",
) as arquivo:

    resposta = client.post(

        "/api/rate/analyze",

        data={
            "file": (
                io.BytesIO(
                    arquivo.read()
                ),
                "relatorio_teste.pdf",
            )
        },

        content_type="multipart/form-data",
    )


print("=" * 80)
print("DIMENSION-RATE")
print("FASE 4 - API")
print("=" * 80)

print()

print(
    "HTTP:",
    resposta.status_code
)

print()

print(
    resposta.get_json()
)

print()

print("=" * 80)