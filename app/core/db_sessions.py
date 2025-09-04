from app.utils.config import settings
from app.core.db_init import DB


db = DB(settings.DB_NAME)