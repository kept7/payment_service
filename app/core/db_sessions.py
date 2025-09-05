from app.core.db_balance_opers import DBBalanceRepository
from app.utils.config import settings
from app.core.db_init import DB
from app.core.db_auth_opers import DBAuthRepository
from app.core.db_payment_opers import DBPaymentRepository

db = DB(settings.DB_NAME)

db_auth = DBAuthRepository(db.session)
db_payment = DBPaymentRepository(db.session)
db_balance = DBBalanceRepository(db.session)
