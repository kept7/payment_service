from app.core.operations.db_balance_opers import DBBalanceRepository
from app.utils.config import settings
from app.core.db_init import DB
from app.core.operations.db_auth_opers import DBAuthRepository
from app.core.operations.db_payment_opers import DBPaymentRepository
from app.core.operations.db_paym_user_opers import DBPaymentUserRepository

db = DB(settings.DB_NAME)

db_auth = DBAuthRepository(db.session)
db_payment = DBPaymentRepository(db.session)
db_payment_user = DBPaymentUserRepository(db.session)
