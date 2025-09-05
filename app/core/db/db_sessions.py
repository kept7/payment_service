from app.utils.config import settings
from app.core.db.db_init import DB
from app.core.db.operations.db_auth_opers import DBAuthRepository
from app.core.db.operations.db_payment_opers import DBPaymentRepository
from app.core.db.operations.db_paym_user_opers import DBPaymentUserRepository

db = DB(settings.DB_NAME)

db_auth = DBAuthRepository(db.session)
db_payment = DBPaymentRepository(db.session)
db_payment_user = DBPaymentUserRepository(db.session)
