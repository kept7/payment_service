from app.utils.config import settings
from app.core.db_init import DB
from app.core.db_operations import DBAuthRepository, DBPaymentRepository

db = DB(settings.DB_NAME)

db_auth = DBAuthRepository(db.session)
db_payment = DBPaymentRepository(db.session)
