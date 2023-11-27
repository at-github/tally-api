from sqlalchemy.orm import Session

import models.transaction as models
import schemas.transaction


def get_transactions(db: Session):
    return db.query(models.Transaction).all()
