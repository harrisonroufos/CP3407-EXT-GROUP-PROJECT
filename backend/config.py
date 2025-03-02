import os

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://caseysummers:Fpa6Hvm9fMVRFyc3SJFKKBtflqG0EbMT@dpg-cuq10fhopnds73eh1q2g-a.oregon-postgres.render.com:5432/myclean_database"
)
